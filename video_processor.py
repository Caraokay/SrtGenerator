import os
import subprocess
import requests
import json
import whisper
import re
import time
from requests.exceptions import RequestException
from prompts import TRANSLATE_AND_EXTRACT_PROMPT

# OpenAI API 配置
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

url = 'https://twohornedcarp.com/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

def process_video(video_path):
    print(f"Processing video: {video_path}")
    audio_path = extract_audio(video_path)
    print(f"Audio extracted: {audio_path}")
    
    srt_content = generate_srt_from_audio(audio_path)
    print("SRT generated from audio")
    
    result = translate_and_extract(srt_content)
    if result is None:
        return {'error': 'Failed to translate and extract content'}
    
    srt_path = save_srt(result['translation'], 'output.srt')
    learning_srt_path = save_srt(result['learning_content'], 'learning_content.srt')
    
    return {
        'srt_path': srt_path,
        'learning_srt_path': learning_srt_path
    }

def extract_audio(video_path):
    audio_path = video_path.rsplit('.', 1)[0] + '.wav'
    subprocess.run(['ffmpeg', '-i', video_path, '-acodec', 'pcm_s16le', '-ar', '44100', audio_path])
    return audio_path

def generate_srt_from_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, word_timestamps=True)
    
    srt_content = ""
    for i, segment in enumerate(result["segments"], 1):
        start_time = format_time(segment['start'])
        end_time = format_time(segment['end'])
        text = segment['text']
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    
    return srt_content

def translate_and_extract(srt_content, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            prompt = TRANSLATE_AND_EXTRACT_PROMPT.format(srt_content=srt_content)

            data = {
                "model": "gpt-4o-2024-08-06",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content']
            
            # 解析结果
            translation, learning_content = result.split('学习内容：')
            translation = translation.replace('翻译：\n', '').strip()
            learning_content = learning_content.strip()
            
            return {
                'translation': translation,
                'learning_content': learning_content
            }
        except RequestException as e:
            print(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print("All retry attempts failed.")
                return None

def save_srt(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"
