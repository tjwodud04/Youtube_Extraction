import yt_dlp
import os

def download_and_convert_to_mp3(path, full_path, url):
    ydl_opts = {
        'format': 'worstaudio/worst', # 저품질 오디오 선택
        'postprocessors': [{ # MP3 변환 설정
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192', # MP3 품질 설정
        }],
        'postprocessor_args': [
            '-ar', '48000', # 샘플 레이트 설정
            '-ac', '2', # 오디오 채널 설정
        ],
        'prefer_ffmpeg': True,
        'keepvideo': False, # 비디오 파일은 삭제
        'outtmpl': path, # 출력 파일명 포맷
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if os.path.exists(full_path):
            os.remove(full_path)
        ydl.download([url])

if __name__ == '__main__':
    url = input("Youtube URL : ")
    path = "./result/"
    full_path = ""
    download_and_convert_to_mp3(path, full_path, path)
