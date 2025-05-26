import asyncio
import json
import logging
import os
import time
from io import DEFAULT_BUFFER_SIZE
from urllib.parse import urlencode

import numpy as np
import requests
import sounddevice as sd
import websockets
from dotenv import load_dotenv

# === 환경변수 로드 ===
load_dotenv()
CLIENT_ID = os.getenv("RTZR_CLIENT_ID")
CLIENT_SECRET = os.getenv("RTZR_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("RTZR_CLIENT_ID and RTZR_CLIENT_SECRET must be set")

# === 기본 설정 ===
API_BASE = "https://openapi.vito.ai"
SAMPLE_RATE = 8000
BYTES_PER_SAMPLE = 2
BLOCK_SIZE = 1024
CHANNELS = 1
DTYPE = 'int16'

TRANSCRIPT_PATH = "transcription_result.txt"
buffer = []
last_result_time = time.time()
END_TIMEOUT = 5  # 초 (무응답 간격 기준)

# === 인증 토큰 관리 클래스 ===
class RTZROpenAPIClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._sess = requests.Session()
        self._token = None

    @property
    def token(self):
        if self._token is None or self._token["expire_at"] < time.time():
            resp = self._sess.post(
                API_BASE + "/v1/authenticate",
                data={"client_id": self.client_id, "client_secret": self.client_secret},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            resp.raise_for_status()
            self._token = resp.json()
        return self._token["access_token"]

# === 텍스트 저장 함수 ===
def save_transcript():
    full_text = " ".join(buffer).strip()
    if not full_text:
        print("저장할 텍스트가 없습니다.")
        return
    with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(full_text + "\n")
    print(f"\n텍스트 저장 완료 → {TRANSCRIPT_PATH}")
    buffer.clear()

# === 실시간 마이크 입력 → WebSocket 전송 ===
async def streaming_transcribe_mic(client: RTZROpenAPIClient):
    token = client.token
    config = dict(
        sample_rate=str(SAMPLE_RATE),
        encoding="LINEAR16",
        use_itn="true",
        use_disfluency_filter="false",
        use_profanity_filter="false",
    )

    query = urlencode(config)
    STREAMING_ENDPOINT = f"wss://openapi.vito.ai/v1/transcribe:streaming?{query}"

    conn_kwargs = dict(extra_headers={"Authorization": "bearer " + client.token})

    async with websockets.connect(STREAMING_ENDPOINT, **conn_kwargs) as websocket:
        print("WebSocket 연결 성공. 마이크로 말하면 텍스트로 출력됩니다.")

        audio_queue = asyncio.Queue()
        loop = asyncio.get_running_loop()  # 메인 루프를 여기서 확보

        def callback(indata, frames, time_info, status):
            if status:
                print("입력 오류:", status)
            asyncio.run_coroutine_threadsafe(
                audio_queue.put(indata.copy()), loop
            )
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            blocksize=BLOCK_SIZE,
            dtype=DTYPE,
            callback=callback,
        )

        async def sender():
            with stream:
                while True:
                    audio = await audio_queue.get()
                    await websocket.send(audio.tobytes())

        async def receiver():
            global last_result_time
            async for msg in websocket:
                res = json.loads(msg)
                if res.get("final"):
                    text = res["alternatives"][0]["text"]
                    print("최종:", text)
                    buffer.append(text)
                    last_result_time = time.time()
                else:
                    print("중간:", res["alternatives"][0]["text"])

        async def watcher():
            while True:
                await asyncio.sleep(1)
                if buffer and (time.time() - last_result_time) > END_TIMEOUT:
                    print("\n발화 종료 감지 (무응답 5초)")
                    save_transcript()

        async def key_listener():
            loop = asyncio.get_running_loop()
            while True:
                await loop.run_in_executor(None, input, "\n[Enter]를 누르면 수동 저장\n")
                if buffer:
                    print("\nEnter 감지 → 텍스트 저장")
                    save_transcript()

        await asyncio.gather(sender(), receiver(), watcher(), key_listener())

# === 외부에서 불러서 실행할 수 있도록 함수로 래핑 ===
def stream_and_save_transcript():
    client = RTZROpenAPIClient(CLIENT_ID, CLIENT_SECRET)
    asyncio.run(streaming_transcribe_mic(client))


# === 실행부 ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("실시간 음성 인식을 시작합니다...")
    stream_and_save_transcript()
