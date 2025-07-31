from fastapi import FastAPI, File, UploadFile, Form
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from PIL import Image
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
from fastapi.responses import JSONResponse


load_dotenv()

app = FastAPI()
app = FastAPI(root_path="/ai")


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

setup_cors(app)

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)


@app.post("/extract-text")
async def extract_text(prompt: str = Form(...), image: UploadFile = File(...)):
    try:
    
        contents = await image.read()
        image_pil = Image.open(io.BytesIO(contents))

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        response = model.generate_content(
            [image_pil, prompt],
            generation_config={"temperature": 0},
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        return {"text": response.text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
