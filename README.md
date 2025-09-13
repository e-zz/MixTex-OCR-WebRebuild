# MixTex-OCR-Web Version

> 中文文档请阅读 [README.zh-CN.md](./README.zh-CN.md)

This project is modified from [MixTeX-Latex-OCR](https://github.com/RQLuo/MixTeX-Latex-OCR), restructuring the original application into a web-based version. The functionality remains largely unchanged, using the original model. (Thanks again to the original author)

No database is used, as I felt persistence wasn't meaningful. (In personal use scenarios, it's not needed)

Frontend interface screenshot:

![Frontend Interface](https://raw.githubusercontent.com/e-zz/MixTex-OCR-WebRebuild/main/assets/screenshot.png)

(Very rudimentary interface) Thanks Claude     :   )

## Features

- **OCR Recognition**: Extract LaTeX formulas from images containing mixed text and mathematical expressions
- **Typst Support**: Convert LaTeX output to Typst format for modern document typesetting


## Installation Steps

### 1. Clone the Project

```bash
git clone https://github.com/e-zz/MixTex-OCR-WebRebuild.git
cd MixTex-OCR-WebRebuild
```

### 2. Install Backend Dependencies

> **Prerequisites:**
> - Python 3.8+ (tested with Python 3.10.18 and 3.13.7)
> - Works on Windows 10 and Ubuntu 22.04
> - **Strongly recommended**: Use a virtual environment ([venv](https://docs.python.org/3/library/venv.html) or [conda](https://www.anaconda.com/))

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

> **Additional setup for Typst users:**
> 
> To get Typst output, ensure `pandoc` is installed and accessible in your environment. You can follow [the Pandoc installation guide](https://pandoc.org/installing.html) and verify by running
> 
> ```
> pandoc -v
> ```


### 3. Install Frontend Dependencies


> **Prerequisites:** 
> * [Node.js](https://nodejs.org/) 16+ and `npm` 


```bash
cd web-frontend
npm install
```


## Running the Project

> **Important:** Activate your virtual environment (where you installed the backend dependencies) before starting.

### Starting the Application

**Recommended method:**
```bash
python start.py
# Use Ctrl+C to safely stop all services
```

After startup, the application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

**Alternative methods:**

<details>
    <summary> Use start.sh (Linux/Mac) </summary>
```bash
./start.sh
# Use ./stop_app.sh to stop (may not work reliably)
```

> **Note:** `start.sh` + `stop_app.sh` is less reliable as it tracks process IDs in log files, which can fail. We recommend using `python start.py` for guaranteed clean shutdown.

</details>

<details>
<summary>Manual startup (for development)</summary>

Backend:
```bash
cd webapi
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:
```bash
cd ../web-frontend
npm run dev
```

</details>

### First-Time Setup

1. Click **"Download and Setup Model"** in the top-right corner of the webpage
2. Wait for the download to complete
3. Start using the OCR functionality

> **Alternative**: Manually download from [MixTeX-Latex-OCR releases](https://github.com/RQLuo/MixTeX-Latex-OCR/releases/latest), extract, and copy the `onnx` folder contents to `./model/`


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
- [Pandoc](https://github.com/jgm/pandoc) and [pypandoc](https://github.com/boisgera/pandoc)