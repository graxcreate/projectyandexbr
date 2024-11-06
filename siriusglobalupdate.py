from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import logging
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment
from g4f.client import Client

app = FastAPI()
client = Client()

logging.basicConfig(filename='audio_extractor.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

URL = 'https://cloud-api.yandex.net/v1/disk/resources'

class TokenRequest(BaseModel):
    token: str

def get_all_files(token, path="/"):
    headers = {'Authorization': f'OAuth {token}'}
    files = []
    offset = 0
    limit = 100

    while True:
        try:
            response = requests.get(f'{URL}/files?path={path}&limit={limit}&offset={offset}', headers=headers)
            response.raise_for_status()
            data = response.json()
            files.extend([item['name'] for item in data['items'] if item['type'] == 'file'])
            offset += limit

            if len(data['items']) < limit:
                break
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching file list: {e}")
            break

    return files

def download_file(token, file_name, output_dir):
    headers = {'Authorization': f'OAuth {token}'}
    download_url = get_download_link(token, file_name)
    if download_url:
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            with open(os.path.join(output_dir, file_name), 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            logging.info(f"File {file_name} downloaded successfully")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading file {file_name}: {e}")

def get_download_link(token, file_name):
    headers = {'Authorization': f'OAuth {token}'}
    try:
        response = requests.get(f'{URL}/download?path={file_name}', headers=headers)
        response.raise_for_status()
        return response.json()['href']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting download link for {file_name}: {e}")
        return None

def extract_audio(file_path, output_dir):
    try:
        video = VideoFileClip(file_path)
        audio = video.audio
        output_file_name = os.path.splitext(os.path.basename(file_path))[0] + ".wav"
        output_file_path = os.path.join(output_dir, output_file_name)
        audio.write_audiofile(output_file_path)
        logging.info(f"Audio extracted from {file_path}")
    except Exception as e:
        logging.error(f"Error extracting audio from {file_path}: {e}")

def transcribe_audio(audio_file_path):
    r = sr.Recognizer()
    song = AudioSegment.from_wav(audio_file_path)

    chunk_length_ms = 60 * 1000  # 5 минут
    chunks = [song[i:i + chunk_length_ms] for i in range(0, len(song), chunk_length_ms)]

    transcription = ""
    for i, chunk in enumerate(chunks):
        chunk_silent = AudioSegment.silent(duration=10)
        audio_chunk = chunk_silent + chunk + chunk_silent

        chunk_file = f"chunk{i}.wav"
        audio_chunk.export(chunk_file, format="wav")

        with sr.AudioFile(chunk_file) as source:
            audio_data = r.record(source)
            try:
                text = r.recognize_google(audio_data, language="ru-RU")
                transcription += text + " "
            except sr.UnknownValueError:
                logging.warning(f"Chunk {i} could not be understood")
            except sr.RequestError as e:
                logging.error(f"Could not request results for chunk {i}; {e}")
        os.remove(chunk_file)

    return transcription.strip()
def correct_spelling_and_punctuation(text):

    messages = [{"role": "user", "content": f"Пожалуйста, исправь орфографию, пунктуацию и логику построения предложений в следующем тексте и отправь исключительно исправленный текст полностью на русском языке без специальных символов, ТЕКСТ ПОЛНОСТЬЮ НА РУССКОМ ЯЗЫКЕ, СПЕЦИАЛЬНЫЕ СИМВОЛЫ ИСПОЛЬЗОВАТЬ ЗАПРЕЩЕНО. В ОТВЕТ ОТПРАВЬ ИСКЛЮЧИТЕЛЬНО ИСПРАВЛЕННЫЙ ТЕКСТ: {text}"}]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response.choices[0].message.content

def summarize_text_openai(text):
    """Суммаризирует текст с помощью ChatGPT."""
    messages = [{"role": "user", "content": f"Напиши суммаризацию данного текста на РУССКОМ ЯЗЫКЕ, в ответ пришли исключительно суммаризацию на РУССКОМ ЯЗЫКЕ: {text}"}]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response.choices[0].message.content

def correct_text(text):

 text = text.replace("Generated by BLACKBOX.AI, try unlimited chat https://www.blackbox.ai", " ")
 text = text.replace("\n", " ")

 return text

@app.post('/process_files')
async def process_files(request: TokenRequest):
    token = request.token
    output_dir = "extracted_audio"
    os.makedirs(output_dir, exist_ok=True)

    all_files = get_all_files(token)
    mp4_files = [file for file in all_files if file.endswith(".mp4")]

    logging.info(f"Found {len(mp4_files)} MP4 files")

    results = []

    for file_name in mp4_files:
        download_file(token, file_name, output_dir)
        file_path = os.path.join(output_dir, file_name)
        extract_audio(file_path, output_dir)

        audio_file_path = os.path.join(output_dir, os.path.splitext(file_name)[0] + ".wav")
        try:
            transcription = transcribe_audio(audio_file_path)
            correct_transcription = correct_spelling_and_punctuation(transcription)
            summary = summarize_text_openai(correct_transcription)
            summary = correct_text(summary)
            results.append({
                "file_name": file_name,
                "transcription": transcription,
                "summary": summary
            })

            with open(os.path.splitext(audio_file_path)[0] + ".txt", 'w', encoding='utf-8') as f:
                f.write(transcription)
        except Exception as e:
            logging.error(f"Error processing {file_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing {file_name}")

    return {"results": results}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
