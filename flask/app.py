# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from main import search_policy, main
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'  # 이미지 저장 폴더
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 폴더가 없으면 생성

@app.route('/run-script', methods=['POST'])
def run_script():
    # 사용자 정보 받기
    user_info = request.form.to_dict()
    
    # 이미지 저장
    if 'image' in request.files:
        image_file = request.files['image']
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)
        user_info['img_path'] = image_path
    # print(user_info)
    output = main(user_info)
    # output = search_policy(user_info)
    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(debug=True)
