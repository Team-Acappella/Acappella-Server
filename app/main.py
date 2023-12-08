from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import time
from TTS import synthesize_text
from answer_generator import task

import nbformat
from nbconvert import PythonExporter
from nbconvert.preprocessors import ExecutePreprocessor

app = FastAPI()
load_dotenv()  # .env 파일에서 환경변수를 로드
professor_image_url = {
    1: os.getenv("RYU_IMAGE_URL"), #ko-KR-Standard-D
    2: os.getenv("JANG_IMAGE_URL"), #ko-KR-Neural2-C
    3: os.getenv("RYANG_IMAGE_URL"), #ko-KR-Neural2-B
    4: os.getenv("OAK_IMAGE_URL"), #ko-KR-Standard-B
    5: os.getenv("JAE_IMAGE_URL"), #ko-KR-Wavenet-C
    6: os.getenv("PARK_IMAGE_URL"), #ko-KR-Wavenet-D
    7: os.getenv("AHN_IMAGE_URL"), #ko-KR-Standard-C
}
professor_tts_string = {
    1: "ko-KR-Standard-D",
    2: "ko-KR-Neural2-C",
    3: "ko-KR-Neural2-B",
    4: "ko-KR-Standard-B",
    5: "ko-KR-Wavenet-C",
    6: "ko-KR-Wavenet-D",
    7: "ko-KR-Standard-C",
}

class VideoRequest(BaseModel):
    question_query: str
    professor_id: int

class SpecificRequest(BaseModel):
    talk_id: str

@app.post("/create-video")
async def create_video(request: VideoRequest):
    
    # 1, 2. 생성된 텍스트를 음성으로 변환한다.
    synthesize_text(task(request.question_query), professor_tts_string[request.professor_id])

    # 3. 변환된 음성을 업로드한다.
    audio_url = upload_audio("app/audio/output.wav")

    # 4. 사진과 음성의 URL을 통해 POST /talks를 해서 talk id를 받아온다.
    talk_id = create_talk(professor_image_url[request.professor_id], audio_url)

    # 5. talk id를 통해 실제 영상 데이터와 스크립트를 리턴한다.
    result_url = get_specific_talk(talk_id)
    return { "text": request.question_query, "url": result_url, "talk_id": talk_id }

@app.get("/specific")
async def get_specific_video(request: SpecificRequest):

    result_url = get_specific_talk(request.talk_id)
    return { "url": result_url }

@app.get("/diffusion")
async def run_diffusion():
    file_path = "./test.ipynb"
    with open(file_path, 'r', encoding='utf-8') as nb_file:
        notebook = nbformat.read(nb_file, as_version=4)
    
    python_exporter = PythonExporter()
    python_code, _ = python_exporter.from_notebook_node(notebook)

    exec_preprocessor = ExecutePreprocessor(timeout=600)
    exec_preprocessor.preprocess(notebook, {'metadata': {'path': './'}})

    cell_outputs = notebook.cells[-1].outputs

    print(cell_outputs)

    return { "test": "working" }

# 파일명 형식 제한이 존재하니 고려해야함
def upload_audio(audio_file_path):
    url = os.getenv("UPLOAD_AUDIO_URL")
    files = { "audio": ("tmp.m4a", open(audio_file_path, "rb"), "audio/x-m4a") }
    headers = {
        "accept": "application/json",
        "authorization": os.getenv("AUTHORIZATION")  
    }
    try:
        response = requests.post(url, files=files, headers=headers)
        print(response.text)
        return response.json().get("url")
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error calling D-ID API: {e}")

def create_talk(image_url, audio_url):
    url = os.getenv("CREATE_TALK_URL")
    payload = {
        "source_url": image_url,
        "script": {
            "type": "audio",
            "audio_url": audio_url
        },
        "config": {
            "stitch": True
        }
    }
    headers = {
        "accept": "application/json",
        "authorization": os.getenv("AUTHORIZATION")  
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return response.json().get("id")
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error calling D-ID API: {e}")

def get_specific_talk(talk_id):
    url = os.getenv("GET_TALK_URL") + f"{talk_id}"
    
    headers = {
        "accept": "application/json",
        "authorization": os.getenv("AUTHORIZATION")  
    }

    try:
        response = requests.get(url, headers=headers)
        print(response.text)
        return response.json().get("result_url")
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error calling D-ID API: {e}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)