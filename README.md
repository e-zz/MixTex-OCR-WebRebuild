# MixTex-OCR-Web Version

> 中文文档请阅读 [README.zh-CN.md](./README.zh-CN.md)

This project is modified from [MixTeX-Latex-OCR](https://github.com/RQLuo/MixTeX-Latex-OCR), restructuring the original application into a web-based version. The functionality remains largely unchanged, using the original model. (Thanks again to the original author)

No database is used, as I felt persistence wasn't meaningful. (In personal use scenarios, it's not needed)

Frontend interface screenshot:

![Frontend Interface](https://raw.githubusercontent.com/e-zz/MixTex-OCR-WebRebuild/main/assets/screenshot.png)

(Very rudimentary interface) Thanks Claude     :   )

## Installation Steps

### 1. Clone the Project

```bash
git clone git@github.com:e-zz/MixTex-OCR-WebRebuild.git
cd MixTex-OCR-WebRebuild
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

To get Typst output, ensure `pandoc` is installed and accessible in your environment. For example, verify by running

```
pandoc -v
```


### 3. Install Frontend Dependencies

```bash
cd ../web-frontend
npm install
```

## Running the Project

### 1. Startup
You can launch the application by running the `start.sh` script, or use `python start.py` as an alternative.

After successful startup, by default the frontend will use http://localhost:3000 port, and the backend API will be available at http://localhost:8000.

<details>
    <summary>Alternatively, you can manually run the following</summary>

> Start backend service
```bash
cd webapi
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
>
> Frontend development server
> 
```bash
cd ../web-frontend
npm run dev
```

</details>

### 2. Model Download
Click the `Download and Setup Model` button in the top-right corner of the webpage and wait for the download to complete. If the model updates, clicking download again will automatically overwrite.

> Alternatively: Manually go to https://github.com/RQLuo/MixTeX-Latex-OCR/releases/latest to download and extract, then copy the contents of the `onnx` folder to the project's model folder.

## TODO
- [ ] Output as `Typst`

## Development

### Project Structure

```
├── model/                # Model files directory
│   ├── encoder_model.onnx       # Encoder model
│   ├── decoder_model_merged.onnx # Decoder model
│   ├── tokenizer.json           # Tokenizer configuration
│   └── ...                      # Other model files
├── web-frontend/        # Frontend project
│   ├── src/                     # Source code
│   ├── package.json             # Frontend dependency configuration
│   └── ...                      # Other frontend files
└── webapi/              # Backend API
    ├── app.py                   # FastAPI application
    └── ...                      # Other backend files
```

### Backend Environment

- Python 3.8+
- ONNX Runtime
- FastAPI
- Uvicorn
- Transformers
- Pillow
- Other dependencies (see requirements.txt)

### Frontend Environment

- Node.js 16+
- npm or yarn
- Vue 3
- Element Plus
- Axios

### API Interface Documentation

- `GET /`: API health check
- `GET /health`: Model loading status check
- `POST /predict`: Upload image to recognize mathematical formulas
- `POST /predict_base64`: Recognize mathematical formulas using Base64 encoded images
- `POST /predict_clipboard`: Process clipboard image recognition for mathematical formulas
- `POST /feedback`: Submit feedback (not very useful)
- `GET /statistics`: Get usage statistics (removed from frontend)
- `POST /reload_model`: Reload model

## Acknowledgments

- [MixTeX-Latex-OCR](https://github.com/RQLuo/MixTeX-Latex-OCR)
- [MixTex-OCR-WebRebuild](https://github.com/OnHaiping/MixTex-OCR-WebRebuild)
- [mitex-rs](https://github.com/mitex-rs/mitex)