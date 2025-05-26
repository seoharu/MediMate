import time
import threading
import traceback
import sys
import asyncio
import os

from gpt_summarize import gpt_simplify_and_summarize
from kot5_summary import refine_summary_kot5

TRANSCRIPT_PATH = "transcription_result.txt"
SUMMARY_PATH = "summary_result.txt"

# socket_stream.py의 마이크 + STT 실행 함수
from socket_stream import streaming_transcribe_mic, RTZROpenAPIClient, CLIENT_ID, CLIENT_SECRET

def run_pipeline(capture_duration=30):
    print("실시간 STT 시작 - 마이크 입력 대기 중..")
    client = RTZROpenAPIClient(CLIENT_ID, CLIENT_SECRET)
    asyncio.run(streaming_transcribe_mic(client))  # 마이크 → 텍스트 저장

    if not os.path.exists(TRANSCRIPT_PATH):
        print("인식된 텍스트 파일이 존재하지 않습니다.")
        return

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw or len(raw.split()) < 5:
        print("\n인식된 텍스트가 너무 짧아 요약을 생략합니다.")
        return

    print("\n인식된 전체 텍스트:\n")
    print(raw)

    try:
        print("\nGPT 요약 중...")
        simplified = gpt_simplify_and_summarize(raw)

        print("\nKoT5 최종 요약 중...")
        final = refine_summary_kot5(simplified)

        print("\n최종 요약 결과:\n")
        print(final)

        with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
            f.write(final + "\n")

    except Exception:
        print("요약 단계에서 오류 발생")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception:
        traceback.print_exc()
        input("엔터를 누르면 종료합니다...")
