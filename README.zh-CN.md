# MixTex-OCR-网站版

本项目由[MixTeX-Latex-OCR](https://github.com/RQLuo/MixTeX-Latex-OCR)修改而来，将原本的应用程序重构成了网站，功能基本上不变，模型用的原模型。（我只是个搬运工，再次感谢原作者）

前端使用vue，后端使用Fastapi（对这俩都不太熟，只是感觉开发比较快，代码健壮性可能有很大问题 @_ @ ）

没有用到数据库，因为感觉持久化没啥意义。（个人使用场景下，用不到）

前端界面截图：

![Frontend Interface](https://raw.githubusercontent.com/e-zz/MixTex-OCR-WebRebuild/main/assets/截图.png)
（非常简陋的界面）感谢Claude     :   )



## 安装步骤

### 1. 克隆项目

```bash
git clone git@github.com:e-zz/MixTex-OCR-WebRebuild.git
cd MixTex-OCR-WebRebuild
```

### 2. 安装后端依赖

```bash
cd webapi
pip install -r requirements.txt
```

要获得 Typst 输出，请确保此项目在安装了 `mitex-python` 的环境中运行。安装请参照：[mitex-python](https://github.com/e-zz/mitex/tree/main/crates/mitex-python)。

### 3. 安装前端依赖
若未安装 npm, 需要 
```bash
cd ../web-frontend
npm install
```

## 运行项目

### 1. 启动
可以直接运行 `.run.sh` 启动，或者运行 `python start.py`。

成功运行后，默认情况下前端将使用 http://localhost:3000 端口，后端API将在 http://localhost:8000 提供服务。
<details>
    <summary>另外，也可手动运行如下</summary>


> 启动后端服务
```bash
cd webapi
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
>
> 前端开发服务器
> 
```bash
cd ../web-frontend
npm run dev
```

</details>




### 2. 模型下载
点击网页右上角的`下载并设置模型`按钮，等待下载完成即可。若模型更新，再次点击下载可自动覆盖。


> 或者：手动前往 https://github.com/RQLuo/MixTeX-Latex-OCR/releases/latest 下载解压，并将 `onxx` 文件夹内容，复制到项目`model`文件夹内。


## TODO
- [ ] 输出为 `Typst`


## 开发

### 项目结构

```
├── model/                # 模型文件目录
│   ├── encoder_model.onnx       # 编码器模型
│   ├── decoder_model_merged.onnx # 解码器模型
│   ├── tokenizer.json           # 分词器配置
│   └── ...                      # 其他模型文件
├── web-frontend/        # 前端项目
│   ├── src/                     # 源代码
│   ├── package.json             # 前端依赖配置
│   └── ...                      # 其他前端文件
└── webapi/              # 后端API
    ├── app.py                   # FastAPI应用
    └── ...                      # 其他后端文件
```

### 后端环境

- Python 3.8+
- ONNX Runtime
- FastAPI
- Uvicorn
- Transformers
- Pillow
- 其他依赖（见requirements.txt）

### 前端环境

- Node.js 16+
- npm 或 yarn
- Vue 3
- Element Plus
- Axios

### API接口说明

- `GET /`: API健康检查
- `GET /health`: 模型加载状态检查
- `POST /predict`: 上传图片识别数学公式
- `POST /predict_base64`: 使用Base64编码图片识别数学公式
- `POST /predict_clipboard`: 处理剪贴板图片识别数学公式
- `POST /feedback`: 提交反馈（没什么用）
- `GET /statistics`: 获取使用统计（前端给删了）
- `POST /reload_model`: 重新加载模型


## 致谢

- [MixTeX-Latex-OCR](https://github.com/RQLuo/MixTeX-Latex-OCR)
- [MixTex-OCR-WebRebuild](https://github.com/OnHaiping/MixTex-OCR-WebRebuild)
- [mitex-rs](https://github.com/mitex-rs/mitex)
