import json
import os

import dotenv
from openai import OpenAI

dotenv.load_dotenv()

client = OpenAI()

def translate_openai(list, target_language):
    final_list = []

    system_input = "이제부터 너는 주어진 텍스트를 잘 번역하는 작업을 수행할 거야."
    first_shot_input = f"제공되는 텍스트를 영어로 번역해줘. 제공되는 텍스트는 다음과 같아. 텍스트 : 안녕하세요. 뷰성형외과 정재현 원장입니다."
    first_shot_output = "Hello. I am Director Jung Jae-hyun from View Plastic Surgery."
    second_shot_input = "가슴 보형물의 사이즈와 컵 사이즈 간의 상관관계에 대해서"
    second_shot_output = "The correlation between breast implant size and cup size"

    for i in range(len(list)):
        # OpenAI의 번역 엔진을 사용하여 텍스트 번역
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 사용할 모델 선택 (최신 정보를 위해 OpenAI 문서 참조)
            messages=[
                {"role": "system", "content": system_input},
                {"role": "user", "content": first_shot_input},
                {"role": "assistant", "content": first_shot_output},
                {"role": "user", "content": second_shot_input},
                {"role": "assistant", "content": second_shot_output},
                {"role": "user", "content": f"제공되는 텍스트를 {target_language}로 번역해줘. 제공되는 텍스트는 다음과 같아. 텍스트 : {list[i]['Text']}"},
            ]
        )

        final_dict = {
            "Start": list[i]['Start'],
            "End": list[i]['End'],
            "Text": response.choices[0].message.content
        }

        final_list.append(final_dict)

    os.makedirs(("./result/"), exist_ok=True)
    with open("./result/translated_with_timestamp.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)


    return list, final_list