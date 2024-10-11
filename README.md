## 실행 방법

### 1. git clone
```bash
git clone https://github.com/ramge132/chat_jiwon.git
```

<br /> 

### 2. 가상환경 구축

가상환경 구축을 위해
프로젝트 루트 디렉토리에서 다음을 실행
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```

<br />  

### 3. 의존 패키지 설치
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


### 4. 실행  
> 두개의 터미널 창이 필요


`$jiwon_bot/front/chatingUI` 에서
``` bash
npm run dev
```
`http://localhost:1573/` 클릭
  
<br>

`$jiwon_bot/flask` 에서
``` bash
cd ../../flask
```
```bash
python main.py
```
`TF_ENABLE_ONEDNN_OPTS=0`와 같은 문구는  
CPU를 사용하므로 속도가 느릴 수 있다는 경고문

<br />

### 5. API KEY 할당
.env를 루트 디렉토리에 생성하고 아래 내용 저장
```
PERPLEXITY_API_KEY = "여기에 API KEY 입력"
```

Perplexity API 링크: https://www.perplexity.ai/settings/api