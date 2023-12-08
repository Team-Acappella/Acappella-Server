import os
from dotenv import load_dotenv
from google.cloud import texttospeech  

# 로컬에 GOOGLE API JSON 저장된 위치에서 파일 로드
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("GOOGLE_API_JSON")
print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

def synthesize_text(text, professor_tts_string):     
    client = texttospeech.TextToSpeechClient()

    # 최대 길이 200 지정
    max_length = 200

    # . 단위로 문장 분리
    words = text.split('. ')
    sentences = []
    current_sentence = ''
    for word in words:
        if len(current_sentence + word) <= max_length:
            current_sentence += word + ' '
        else:
            sentences.append(current_sentence.strip() + '.')
            current_sentence = word + ' '
    if current_sentence:
        sentences.append(current_sentence.strip() + '.')

    # 빈 배열 생성
    audio_data = []

    # 문장 개수 단위로 텍스트 변환
    for sentence in sentences:
        input_text = texttospeech.SynthesisInput(text=sentence)

        # 오디오 설정 (예: 한국어, 남성C)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=professor_tts_string,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )

        audio_data.append(response.audio_content)
    audio_data = b"".join(audio_data)
    
    # output.wav 파일 생성
    with open("/Users/idongseob/dev/Acappella-temp/Acappella-Server/app/audio/output.wav", "wb") as out:        
        out.write(audio_data)
        print("TTS has been successfully created.")