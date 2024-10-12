# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from main import search_policy, main, classify_image, model
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'  # 이미지 저장 폴더
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 폴더가 없으면 생성

@app.route('/classify-image', methods=['POST'])
def classify_image_endpoint():
    # 이미지 저장
    if 'image' in request.files:
        image_file = request.files['image']
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)
        # 이미지 분류 함수 호출
        gender, age_group = classify_image(model, image_path)
        # 분류 결과 반환
        return jsonify({'gender': gender, 'age_group': age_group})
    else:
        return jsonify({'error': 'No image provided'}), 400

@app.route('/run-script', methods=['POST'])
def run_script():
    # 사용자 정보 받기
    user_info = request.form.to_dict()
    
    # 성별과 연령대가 이미 있는지 확인
    if 'gender' not in user_info or 'age' not in user_info:
        # 이미지 저장
        if 'image' in request.files:
            image_file = request.files['image']
            image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
            image_file.save(image_path)
            user_info['img_path'] = image_path
            # 이미지 분류
            gender, age_group = classify_image(model, user_info['img_path'])
            user_info['gender'] = gender
            user_info['age'] = age_group
        else:
            # 이미지가 제공되지 않은 경우 처리
            user_info['gender'] = '미상'  # Unknown
            user_info['age'] = '미상'
    
    # 정책 검색 요청
    output = search_policy(user_info)
    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(debug=True)
