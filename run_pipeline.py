import time
import threading
import traceback
import sys
from csr_stream import start_csr, transcripts
from gpt_summarize import gpt_simplify_and_summarize
from kobart_summary import final_summary


def run_pipeline(capture_duration=30):
    print("CSR 스트리밍 시작")
    t = threading.Thread(target=start_csr, daemon=True)
    t.start()

    time.sleep(capture_duration)
    print(f"{capture_duration}초 입력 완료, 텍스트 획득")

    raw = "\n".join(transcripts).strip()
    print("\n[인식된 전체 텍스트]")
    print(raw if raw else "(없음)")

    if not raw or len(raw.split()) < 5:
        print("\n 인식된 텍스트가 충분하지 않아 요약을 생략합니다.")
        return

    try:
        simplified = gpt_simplify_and_summarize(raw)
        print("\n[GPT 요약 결과]\n", simplified)

        final = final_summary(simplified)
        print("\n[최종 압축 요약 결과]\n", final)
    except Exception:
        print("요약 단계에서 오류 발생")
        traceback.print_exc()


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception:
        traceback.print_exc()
        input("엔터를 누르면 종료합니다...")
