import dotenv
import json

from openai import OpenAI

dotenv.load_dotenv()

client = OpenAI()

def youtube_to_transcript(full_path):
    # Open the audio file
    file = open(f'{full_path}', "rb")

    timestamp_transcript = client.audio.transcriptions.create(
        file=file,
        model="whisper-1",
        response_format="srt",
        timestamp_granularities=["segment"],
    )

    with open("./result/원본_텍스트.srt", "w", encoding="utf-8") as f:
        f.write(timestamp_transcript)

    return timestamp_transcript

if __name__ == "__main__":
    youtube_to_transcript("temp")