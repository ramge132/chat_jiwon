## 실행 방법

### 1. 전체 파일을 다운로드하고  
가상환경 구축을 위해
루트 디렉토리에서 다음을 실행
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```

<br />  

### 2. 의존 패키지 설치
```bash
pip install -r requirements.txt 
```
```bash
cd front/chatingUI
```
``` bash
npm install
```

<br />

### 3. 실행  
(두개의 터미널 창이 필요)


터미널1 위치 : `$jiwon_bot/front/chatingUI`
``` bash
npm run dev
```
`http://localhost:1573/` 클릭
  
<br>

터미널2 위치 : `$jiwon_bot/flask`
``` bash
cd ../../flask
```
```bash
python main.py
```
`TF_ENABLE_ONEDNN_OPTS=0`와 같은 문구는  
CPU를 사용하므로 속도가 느릴 수 있다는 경고문



