from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import time

app = FastAPI()
load_dotenv()  # .env 파일에서 환경변수를 로드
professor_image_url = {
    1: os.getenv("OAK_IMAGE_URL"),
    2: os.getenv("RYU_IMAGE_URL"),
}

class VideoRequest(BaseModel):
    question_query: str
    professor_id: int

class SpecificRequest(BaseModel):
    talk_id: str

@app.post("/create-video")
async def create_video(request: VideoRequest):
    
    # 1. 질문에 대한 답변 텍스트를 생성한다.

    # 2. 생성된 텍스트를 음성으로 변환한다.

    # 3. 변환된 음성을 업로드한다.
    audio_url = upload_audio("test.m4a")

    # 4. 사진과 음성의 URL을 통해 POST /talks를 해서 talk id를 받아온다.
    talk_id = create_talk(professor_image_url[request.professor_id], audio_url)

    time.sleep(5)

    # 5. talk id를 통해 실제 영상 데이터와 스크립트를 리턴한다.
    result_url = get_specific_talk(talk_id)
    return { "text": request.question_query, "url": result_url, "talk_id": talk_id }

@app.get("/specific")
async def get_specific_video(request: SpecificRequest):

    result_url = get_specific_talk(request.talk_id)
    return { "url": result_url }

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

