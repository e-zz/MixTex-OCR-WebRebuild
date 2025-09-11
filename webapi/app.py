from fastapi import FastAPI, File, UploadFile, HTTPException, Form
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

# 配置日志
logging.basicConfig(level=logging.INFO)
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


def mixtex_inference(image, max_length=512, use_dollars=False, convert_align=False):
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


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    use_dollars: bool = Form(False),
    convert_align: bool = Form(False),
):
    """图片转数学公式接口"""
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # 读取图片
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")

        # 推理
        result, success = mixtex_inference(
            img, use_dollars=use_dollars, convert_align=convert_align
        )

        if success:
            return {"success": True, "latex": result, "message": "识别成功"}
        else:
            raise HTTPException(status_code=500, detail=result)

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict_base64")
async def predict_base64(
    image_data: str = Form(...),
    use_dollars: bool = Form(False),
    convert_align: bool = Form(False),
):
    """基于base64的图片转数学公式接口"""
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # 转换base64为图片
        img = base64_to_image(image_data)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        # 推理
        result, success = mixtex_inference(
            img, use_dollars=use_dollars, convert_align=convert_align
        )

        if success:
            return {"success": True, "latex": result, "message": "识别成功"}
        else:
            raise HTTPException(status_code=500, detail=result)

    except Exception as e:
        logger.error(f"Base64 prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict_clipboard")
async def predict_clipboard(
    image_data: str = Form(...),
    use_dollars: bool = Form(False),
    convert_align: bool = Form(False),
):
    """处理剪贴板图片粘贴的接口"""
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # 转换base64为图片
        img = base64_to_image(image_data)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid clipboard image data")

        # 推理
        result, success = mixtex_inference(
            img, use_dollars=use_dollars, convert_align=convert_align
        )

        if success:
            return {"success": True, "latex": result, "message": "剪贴板图片识别成功"}
        else:
            raise HTTPException(status_code=500, detail=result)

    except Exception as e:
        logger.error(f"Clipboard prediction error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Clipboard prediction failed: {str(e)}"
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
