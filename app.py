import streamlit as st
import os
import pandas as pd
import time

from youtube_downloader import download_and_convert_to_mp3
from whisper_extractor import youtube_to_transcript


def main():
    st.title('유튜브 음성 텍스트 추출 및 번역 텍스트 생성')

    # Get YouTube URL from user
    url = st.text_input('유튜브 URL : ')

    # Get language from user
    lang = st.text_input('번역하고 싶은 언어 (ex. 영어) : ')

    if st.button('추출하기'):
        if url == '':
            st.error('YouTube URL을 입력하세요.')
        else:
            output_dir = "/video/"
            os.makedirs(output_dir, exist_ok=True)

            ext = "mp3"
            path = os.path.join(output_dir, "converted_video_to_sound")
            file_full_path = os.path.join(output_dir, f"converted_video_to_sound.{ext}")

            placeholder = st.empty()

            placeholder.info('비디오 다운로드하는 중...')
            download_and_convert_to_mp3(path, file_full_path, url)
            placeholder.empty()

            placeholder.info('비디오 다운로드가 완료되었습니다!')
            time.sleep(2)
            placeholder.empty()

            placeholder.info('텍스트 추출하는 중...')
            original_full_text, translated_full_text = youtube_to_transcript(file_full_path, language=lang)
            placeholder.empty()

            placeholder.info('텍스트 추출이 완료되었습니다!')
            time.sleep(2)
            placeholder.empty()

            result_toggle = {
                "원 언어 내용 전사" : pd.DataFrame(original_full_text),
                "번역된 내용 전사" : pd.DataFrame(translated_full_text)
            }

            for section_name, df in result_toggle.items():
                with st.expander(section_name):
                    st.dataframe(df)

if __name__ == '__main__':
    main()
