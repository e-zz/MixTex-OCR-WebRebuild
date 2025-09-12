from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
import re
import numpy as np
from transformers import RobertaTokenizer, ViTImageProcessor
import onnxruntime as ort
import base64
import logging
import shutil
import requests
import zipfile
from pathlib import Path
from tqdm import tqdm
from mitex_python import convert_latex_to_typst

# 配置日志
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# Create logs directory if it doesn't exist
log_dir = Path(__file__).resolve().parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "mixtex_api.log"

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# 模型路径配置
MODEL_PATHS = [os.path.abspath("../model")]

# 全局变量
model = None

app = FastAPI(title="MixTeX OCR API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def find_valid_model_path():
    """查找有效的模型路径"""
    for path in MODEL_PATHS:
        if os.path.exists(path):
            required_files = [
                os.path.join(path, "encoder_model.onnx"),
                os.path.join(path, "decoder_model_merged.onnx"),
                os.path.join(path, "tokenizer.json"),
                os.path.join(path, "vocab.json"),
            ]

            if all(os.path.exists(f) for f in required_files):
                return path
    return None


def get_latest_release_url():
    """Get the URL of the latest MixTeX model release"""
    fallback_url = "https://github.com/RQLuo/MixTeX-Latex-OCR/releases/tag/MixTex-B"
    
    try:
        # Get latest release info from GitHub API
        logger.info("Fetching latest release information...")
        api_url = "https://api.github.com/repos/RQLuo/MixTeX-Latex-OCR/releases/latest"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        release_data = response.json()
        
        # Find the MixTex-B.zip asset
        for asset in release_data['assets']:
            if asset['name'].lower() == 'mixtex-b.zip':
                logger.info(f"Found latest model at: {asset['browser_download_url']}")
                return asset['browser_download_url']
        
        logger.warning(f"MixTex-B.zip not found in latest release, using fallback URL")
        return fallback_url
    except Exception as e:
        logger.warning(f"Error fetching release info: {str(e)}, using fallback URL")
        return fallback_url


def download_model_file(url, zip_path):
    """Download model file with progress tracking"""
    logger.info(f"Downloading model from: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    
    with open(zip_path, 'wb') as f, tqdm(
            desc="Downloading MixTeX model",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
        for data in response.iter_content(block_size):
            size = f.write(data)
            bar.update(size)


def download_and_setup_model():
    """Download MixTeX model from GitHub release, extract and set up"""
    # Set paths
    base_dir = Path(__file__).resolve().parent.parent
    model_dir = base_dir / "model"
    temp_dir = base_dir / "temp"
    unzip_dir = temp_dir / "MixTex-B"
    unzip_model_dir = unzip_dir / "onnx"
    
    # Create directories if they don't exist
    model_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)
    unzip_dir.mkdir(exist_ok=True)
    
    # Download file path
    zip_path = temp_dir / "MixTex-B.zip"
    
    try:
        # Get the latest release URL
        model_url = get_latest_release_url()
        
        # Download the model
        download_model_file(model_url, zip_path)
        
        # Extract the model
        logger.info("Extracting model file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_dir)
        
        # Move files to model directory
        logger.info("Setting up model files...")
        
        # Remove existing model directory if it exists
        if model_dir.exists():
            shutil.rmtree(model_dir)
        
        # Copy the entire extracted directory to the model directory
        shutil.copytree(unzip_model_dir, model_dir)
        logger.info(f"Copied entire model directory from {unzip_model_dir} to {model_dir}")
        
        # Clean up temporary files
        logger.info("Cleaning up...")
        if zip_path.exists():
            os.remove(zip_path)
        
        try:
            shutil.rmtree(unzip_dir)
        except Exception as e:
            logger.warning(f"Could not remove temporary files: {e}")
        
        # Reload the model
        load_model()
        
        return {
            "status": "success", 
            "message": "Model downloaded and set up successfully",
            "source": model_url
        }
    except Exception as e:
        logger.error(f"Model download and setup failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to download and setup model: {str(e)}"
        }

def load_model():
    """加载ONNX模型"""
    global model
    try:
        valid_path = find_valid_model_path()

        if valid_path is None:
            raise Exception(
                "找不到有效的模型文件，请确保onnx文件夹包含完整的模型文件。"
            )

        logger.info(f"Loading model from: {valid_path}")

        tokenizer = RobertaTokenizer.from_pretrained(valid_path)
        feature_extractor = ViTImageProcessor.from_pretrained(valid_path)

        # 打印feature_extractor的配置信息
        logger.info(f"Feature extractor config: {feature_extractor}")
        logger.info(f"Feature extractor size: {feature_extractor.size}")
        logger.info(f"Feature extractor do_resize: {feature_extractor.do_resize}")
        logger.info(f"Feature extractor do_normalize: {feature_extractor.do_normalize}")

        encoder_session = ort.InferenceSession(f"{valid_path}/encoder_model.onnx", providers=["CPUExecutionProvider"])
        decoder_session = ort.InferenceSession(
            f"{valid_path}/decoder_model_merged.onnx", 
            providers=["CPUExecutionProvider"]
        )

        model = (tokenizer, feature_extractor, encoder_session, decoder_session)
        logger.info("Model loaded successfully!")
        return True

    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        return False


def pad_image(img, out_size=(448, 448)):
    """调整图片大小并填充"""
    x_img, y_img = out_size
    logger.info(f"Target image size: {out_size}")
    logger.info(f"Input image size: {img.size}")

    background = Image.new("RGB", (x_img, y_img), (255, 255, 255))
    width, height = img.size

    if width < x_img and height < y_img:
        x = (x_img - width) // 2
        y = (y_img - height) // 2
        background.paste(img, (x, y))
        logger.info(f"Image padded to center: ({x}, {y})")
    else:
        scale = min(x_img / width, y_img / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        x = (x_img - new_width) // 2
        y = (y_img - new_height) // 2
        background.paste(img_resized, (x, y))
        logger.info(
            f"Image resized and padded: scale={scale:.3f}, new_size=({new_width}, {new_height}), position=({x}, {y})"
        )

    logger.info(f"Final processed image size: {background.size}")
    return background


def check_repetition(s, repeats=12):
    """检查字符串重复"""
    for pattern_length in range(1, len(s) // repeats + 1):
        for start in range(len(s) - repeats * pattern_length + 1):
            pattern = s[start : start + pattern_length]
            if s[start : start + repeats * pattern_length] == pattern * repeats:
                return True
    return False


def convert_align_to_equations(text):
    """转换align环境为单行公式"""
    text = re.sub(r"\\begin\{align\*\}|\\end\{align\*\}", "", text).replace("&", "")
    equations = text.strip().split("\\\\")
    converted = []
    for eq in equations:
        eq = eq.strip().replace("\\[", "").replace("\\]", "").replace("\n", "")
        if eq:
            converted.append(f"$$ {eq} $$")
    return "\n".join(converted)


def base64_to_image(base64_string):
    """将base64字符串转换为PIL Image"""
    try:
        if not isinstance(base64_string, str):
            return None

        if base64_string.startswith("data:image"):
            base64_string = base64_string.split(",")[1]

        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        logger.error(f"Base64 to image conversion failed: {e}")
        return None


def mixtex_inference(image, max_length=512, use_dollars=False, convert_align=False, use_typst=False):
    """执行LaTeX推理"""
    if model is None:
        return "模型未加载", False

    tokenizer, feature_extractor, encoder_session, decoder_session = model

    try:
        # 处理图片 - 使用448x448尺寸
        processed_image = pad_image(image.convert("RGB"), (448, 448))
        logger.info(f"Processed image size: {processed_image.size}")

        # 使用feature_extractor处理图片
        inputs = feature_extractor(processed_image, return_tensors="np")
        pixel_values = inputs.pixel_values
        logger.info(f"Feature extractor output shape: {pixel_values.shape}")

        # 编码器推理
        encoder_outputs = encoder_session.run(None, {"pixel_values": pixel_values})[0]
        logger.info(f"Encoder output shape: {encoder_outputs.shape}")

        # 模型推理参数
        num_layers = 6
        hidden_size = 768
        num_attention_heads = 12
        batch_size = 1
        head_size = hidden_size // num_attention_heads

        # 解码器初始化
        decoder_inputs = {
            "input_ids": tokenizer("<s>", return_tensors="np").input_ids.astype(
                np.int64
            ),
            "encoder_hidden_states": encoder_outputs,
            "use_cache_branch": np.array([True], dtype=bool),
            **{
                f"past_key_values.{i}.{t}": np.zeros(
                    (batch_size, num_attention_heads, 0, head_size), dtype=np.float32
                )
                for i in range(num_layers)
                for t in ["key", "value"]
            },
        }

        generated_text = ""

        # 生成循环
        for step in range(max_length):
            decoder_outputs = decoder_session.run(None, decoder_inputs)
            next_token_id = np.argmax(decoder_outputs[0][:, -1, :], axis=-1)
            token_text = tokenizer.decode(next_token_id, skip_special_tokens=True)
            generated_text += token_text

            # 检查重复
            if check_repetition(generated_text, 21):
                logger.info("检测到重复，停止生成")
                break

            # 检查结束
            if next_token_id == tokenizer.eos_token_id:
                logger.info("生成完成")
                break

            # 更新解码器输入
            decoder_inputs.update(
                {
                    "input_ids": next_token_id[:, None],
                    **{
                        f"past_key_values.{i}.{t}": decoder_outputs[i * 2 + 1 + j]
                        for i in range(num_layers)
                        for j, t in enumerate(["key", "value"])
                    },
                }
            )

        # 后处理
        result = (
            generated_text.replace("\\[", "\\begin{align*}")
            .replace("\\]", "\\end{align*}")
            .replace("%", "\\%")
        )

        if convert_align:
            result = convert_align_to_equations(result)

        if use_dollars:
            result = result.replace("\\(", "$").replace("\\)", "$")
            
        if use_typst:
            try:
                result = convert_latex_to_typst(result)
                logger.info(result)
            except Exception as e:
                # TODO text and equation mixed handling
                logger.error(f"Typst conversion failed: {e}")
                return f"Typst conversion failed: {str(e)}", False

        return result, True

    except Exception as e:
        logger.error(f"推理过程中出错: {str(e)}")
        return f"推理过程中出错: {str(e)}", False


@app.on_event("startup")
async def startup_event():
    """启动时加载模型"""
    if not load_model():
        logger.error("Failed to load model during startup")



@app.get("/")
async def root():
    return {"message": "MixTeX OCR API is running"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/download_model")
async def download_model():
    """Download and setup the model files from GitHub release"""
    try:
        result = download_and_setup_model()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Common prediction function to handle all three endpoints
async def process_prediction(image, use_dollars=False, convert_align=False, use_typst=False, source="unknown"):
    """Common function for processing predictions from different sources"""
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        if image is None:
            raise HTTPException(status_code=400, detail=f"Invalid {source} image data")

        # Run inference
        result, success = mixtex_inference(
            image, use_dollars=use_dollars, convert_align=convert_align, use_typst=use_typst
        )

        if success:
            return {"success": True, "latex": result, "message": f"{source} 识别成功"}
        else:
            raise HTTPException(status_code=500, detail=result)

    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        raise
    except Exception as e:
        logger.error(f"{source} prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"{source} prediction failed: {str(e)}")


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    use_dollars: bool = Form(False),
    convert_align: bool = Form(False),
    use_typst: bool = Form(False),
):
    """图片转数学公式接口"""
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # 读取图片
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    
    return await process_prediction(
        image=img,
        use_dollars=use_dollars,
        convert_align=convert_align,
        use_typst=use_typst,
        source="文件上传"
    )


@app.post("/predict_base64")
async def predict_base64(
    image_data: str = Form(...),
    use_dollars: bool = Form(False),
    convert_align: bool = Form(False),
    use_typst: bool = Form(False),
):
    """基于base64的图片转数学公式接口"""
    # 转换base64为图片
    img = base64_to_image(image_data)
    
    return await process_prediction(
        image=img,
        use_dollars=use_dollars,
        convert_align=convert_align,
        use_typst=use_typst,
        source="Base64图片"
    )


@app.post("/predict_clipboard")
async def predict_clipboard(
    image_data: str = Form(...),
    use_dollars: bool = Form(False),
    convert_align: bool = Form(False),
    use_typst: bool = Form(False),
):
    """处理剪贴板图片粘贴的接口"""
    # 转换base64为图片
    img = base64_to_image(image_data)
    
    return await process_prediction(
        image=img,
        use_dollars=use_dollars,
        convert_align=convert_align,
        use_typst=use_typst,
        source="剪贴板"
    )


@app.post("/feedback")
async def submit_feedback(
    latex_text: str = Form(...), feedback: str = Form(...), image_data: str = Form(None)
):
    """提交反馈接口"""
    try:
        # 简化反馈处理，不再保存到文件
        return {"success": True, "message": "反馈已记录"}

    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Feedback submission failed: {str(e)}"
        )


@app.get("/statistics")
async def get_statistics():
    """获取数据统计"""
    try:
        # 简化统计，不再依赖CSV文件
        return {
            "success": True,
            "total_count": 0,
            "feedback_counts": {},
            "message": "统计功能已简化",
        }
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics failed: {str(e)}")


@app.post("/reload_model")
async def reload_model():
    """重新加载模型"""
    try:
        success = load_model()
        if success:
            return {"success": True, "message": "模型重新加载成功"}
        else:
            raise HTTPException(status_code=500, detail="模型重新加载失败")
    except Exception as e:
        logger.error(f"Model reload error: {e}")
        raise HTTPException(status_code=500, detail=f"Model reload failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
