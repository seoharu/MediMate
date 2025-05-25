# MediMate
sw ai경진대회 project-MediMate
Clova Speech Recognition(gRPC)를 사용해 마이크 입력을 실시간으로 텍스트로 변환하고,  
OpenAI GPT와 KoBART를 통해 자연스럽게 요약하는 자동화 파이프라인입니다.

---

## 📁 프로젝트 구조

    swai/
    ├── app.py                      # Flask API (옵션)
    ├── csr_stream.py              # Clova gRPC 실시간 STT
    ├── gpt_summarize.py           # OpenAI GPT 요약
    ├── kobart_summary.py          # KoBART 기반 추가 요약
    ├── run_pipeline.py            # 전체 파이프라인 실행 스크립트
    ├── nest.proto                 # protobuf 정의 파일
    ├── requirements.txt           # 필요한 패키지 목록
    ├── .env                       # (개인 키 저장용, Git에 업로드 금지)
    ├── .gitignore                 # Git 무시 목록
    └── templates/
        └── index.html             # 웹 인터페이스용 (선택)

---

## 🚀 실행 방법

### 1. 환경 설정

```bash
conda create -n venv python=3.10
conda activate venv
pip install -r requirements.txt

macOS에서는 다음도 설치해야 PyAudio가 동작합니다:
brew install ffmpeg portaudio

### 2. .env 파일 설정

`.env` 파일을 프로젝트 루트에 생성하고, 다음과 같이 작성하세요:

```env
CLOVA_Secret_Key=your-clova-secret-key
CLOVA_gRPC_URL=clovaspeech-gw.ncloud.com:443
OPENAI_API_KEY=your-openai-key

### 3. 실행 
'''bash
python run_pipeline.py
