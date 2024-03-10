import dotenv
import json
import os

from openai import OpenAI
from translator import translate_openai
dotenv.load_dotenv()

client = OpenAI()

def youtube_to_transcript(full_path, language):
  # Extract the audio from the YouTube video
  timestamped_transcript_list = list()

  # Open the audio file
  file = open(f'.{full_path}', "rb")

  # timestamp가 기록된 스크립트 추출 (원래의 언어)
  timestamp_transcript = client.audio.transcriptions.create(
    file=file,
    model="whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["segment"]
  )

  # 각각의 타임스탬프와 해당하는 텍스트를 json 형태로 저장하고 리스트에 담기
  for i in range(len(timestamp_transcript.segments)):
    needed_dictionary = {
      "Start" : timestamp_transcript.segments[i]['start'],
      "End" : timestamp_transcript.segments[i]['end'],
      "Text" : timestamp_transcript.segments[i]['text']
    }
    timestamped_transcript_list.append(needed_dictionary)

  # 파일로 저장
  os.makedirs(("./result/"), exist_ok=True)
  with open("./result/original_with_timestamp.json", "w", encoding="utf-8") as f :
        json.dump(timestamped_transcript_list, f, indent=4, ensure_ascii=False)

  # 번역 수행
  final_list = translate_openai(timestamped_transcript_list, target_language=language)

  return final_list
