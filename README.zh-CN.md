# MixTex-OCR-网站版

本项目由[MixTeX-Latex-OCR](https://github.com/RQLuo/MixTeX-Latex-OCR)修改而来，将原本的应用程序重构成了网站，功能基本上不变，模型用的原模型。（我只是个搬运工，再次感谢原作者）

前端使用vue，后端使用Fastapi（对这俩都不太熟，只是感觉开发比较快，代码健壮性可能有很大问题 @_ @ ）

没有用到数据库，因为感觉持久化没啥意义。（个人使用场景下，用不到）

前端界面截图：

![Frontend Interface](https://raw.githubusercontent.com/e-zz/MixTex-OCR-WebRebuild/main/assets/截图.png)
（非常简陋的界面）感谢Claude     :   )


## 功能特点

- **OCR 识别**：从包含混合文本和数学表达式的图像中提取 LaTeX 公式
- **Typst 支持**：将 LaTeX 输出转换为 Typst 格式，支持现代文档排版


## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/e-zz/MixTex-OCR-WebRebuild.git
cd MixTex-OCR-WebRebuild
```

### 2. 安装后端依赖

> **前提条件：**
> - Python 3.8+（已在 Python 3.10.18 和 3.13.7 上测试）
> - 在 Windows 10 和 Ubuntu 22.04 上运行
> - **强烈推荐**：使用虚拟环境（[venv](https://docs.python.org/3/library/venv.html) 或 [conda](https://www.anaconda.com/)）

安装后端依赖：

```bash
pip install -r requirements.txt
```

> **Typst 用户的额外设置：**
> 
要获得 Typst 输出，请确保环境中已安装 `pandoc` 并可正常访问。您可以按照 [Pandoc 安装指南](https://pandoc.org/installing.html) 进行安装，并通过运行以下命令进行验证

```
pandoc -v
```


### 3. 安装前端依赖

> **前提条件：** 
> * [Node.js](https://nodejs.org/) 16+ 和 `npm` 

```bash
cd web-frontend
npm install
```

## 运行项目

> **重要提示：** 启动前确保已激活 python 虚拟环境（上文中安装后端依赖的环境）。

### 启动应用程序

**推荐方法：**
```bash
python start.py
# 使用 Ctrl+C 安全停止所有服务
```

启动后，应用程序将在以下地址可用：
- **前端**：http://localhost:3000
- **后端API**：http://localhost:8000



**其它方法：**

<details>
    <summary>使用 start.sh</summary>

```bash
./start.sh
# 使用 ./stop_app.sh 停止（可能无法可靠工作）
```

> **注意：** `start.sh` + `stop_app.sh` 不太可靠，因为它在日志文件中跟踪进程ID，可能会失败。我们建议使用 `python start.py` 以确保干净关闭。

</details>

<details>
<summary>手动启动（用于开发）</summary>

后端：
```bash
cd webapi
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

前端：
```bash
cd ../web-frontend
npm run dev
```

</details>

### 首次设置

1. 点击网页右上角的**"下载并设置模型"**
2. 等待下载完成
3. 开始使用OCR功能



### 2. 模型下载
点击网页右上角的`下载并设置模型`按钮，等待下载完成即可。若模型更新，再次点击下载可自动覆盖。


> 或者：手动前往 https://github.com/RQLuo/MixTeX-Latex-OCR/releases/latest 下载解压，并将 `onxx` 文件夹内容，复制到项目`model`文件夹内。




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
- [Pandoc](https://github.com/jgm/pandoc) 和 [pypandoc](https://github.com/boisgera/pandoc)
