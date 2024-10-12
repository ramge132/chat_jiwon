# main.py
import requests
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import cv2
from dotenv import load_dotenv

load_dotenv()

perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")

# 경고 메시지 숨기기
tf.get_logger().setLevel('ERROR')
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Perplexity API 설정
API_KEY = perplexity_api_key  # perplexity_api_key대신 "asdf1234"와 같이 큰따옴표로 묶어 api_key를 입력하세요
API_URL = "https://api.perplexity.ai/chat/completions"

# 얼굴 분류 모델 로드 (SavedModel 형식)
model = tf.saved_model.load('converted_savedmodel/model.savedmodel')

# 이미지 파일 경로
image_path = 'test/young-ad.jpg'

# 이미지 전처리 함수 (Teachable Machine 방식 적용)
def preprocess_image(image_path):
    # 이미지를 OpenCV로 읽기
    image = cv2.imread(image_path)

    # 이미지를 224x224로 크기 조정
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

    # 이미지를 numpy 배열로 변환하고 모델 입력 형태에 맞게 전처리
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

    # 이미지를 정규화 (Teachable Machine 방식: (이미지 / 127.5) - 1)
    image = (image / 127.5) - 1
    return image

# 분류 함수
def classify_image(model, image_path):
    # 이미지 전처리
    processed_image = preprocess_image(image_path)

    # 모델의 signature(서명)에서 추론을 위한 함수를 불러옴
    infer = model.signatures["serving_default"]

    # 추론 실행 (전처리된 이미지를 모델에 입력)
    predictions = infer(tf.convert_to_tensor(processed_image))

    # 결과 처리
    class_labels = ['infant_M', 'infant_F', 'young-adult_M', 'young-adult_F',
                    'middle-aged_M', 'middle-aged_F', 'elderly_M', 'elderly_F']

    predicted_class = class_labels[np.argmax(predictions['sequential_20'].numpy())]  # 모델 출력 키 확인 후 수정 필요
    
    # 얼굴 이미지 분류 결과로 성별과 연령대 추출
    if 'M' in predicted_class:
        gender = '남성'
    else:
        gender = '여성'

    if 'infant' in predicted_class:
        age_group = '유아'
    elif 'young-adult' in predicted_class:
        age_group = '청년'
    elif 'middle-aged' in predicted_class:
        age_group = '장년'
    else:
        age_group = '노년'
        
    print('자동 분류된 정보: ', gender, age_group)
    return gender, age_group

# Perplexity API 호출 함수
def get_completion_from_perplexity(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.1-sonar-huge-128k-online",
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed: {response.status_code}, {response.text}")

# 검색 요청 및 Perplexity API와 연동 함수
def search_policy(user_info):
    topic = user_info['info']

    messages = [
        {"role": "system", "content": "당신은 청년 정책 전문가입니다."},
        {"role": "user", "content": (
            f"사용자 정보: 성별: {user_info['gender']}, 나이: {user_info['age']}, 지역: {user_info['location']}, "
            f"취업상태: {user_info['employment_status']}, 학력: {user_info['education']}, "
            f"특화분야: {user_info['specialization']}, 개인/가구 특성: {user_info['household_features']}\n"
            f"검색 주제: {topic}\n"
            "이 정보를 바탕으로 사용자에게 적합한 정책을 추천해줘."
        )}
    ]

    response = get_completion_from_perplexity(messages)
    print("검색 결과:", response["choices"][0]["message"]["content"])

    return response["choices"][0]["message"]["content"]

# 메인 실행 함수
def main(userInfo):
    # 얼굴 이미지 분류
    gender, age_group = classify_image(model, userInfo['img_path'])
    userInfo['gender'] = gender
    userInfo['age'] = age_group

    # 정책 검색 요청
    return search_policy(userInfo)

# 실행
if __name__ == "__main__":
    import sys
    image_path = sys.argv

    main(image_path)
