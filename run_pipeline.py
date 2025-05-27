import os
from datetime import datetime

from gpt_summarize import gpt_simplify_and_summarize
from kot5_summary import refine_summary_kot5
from kobart_summary import final_summary

# === 저장 경로는 외부에서 전달받기 때문에, 여기서 직접 지정하지 않음 ===

def summarize_saved_transcript(transcript_path: str):
    if not os.path.exists(transcript_path):
        print(f"텍스트 파일이 존재하지 않습니다: {transcript_path}")
        return

    with open(transcript_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw or len(raw.split()) < 5:
        print("텍스트가 너무 짧아 요약을 생략합니다.")
        return

    print("\n인식된 전체 텍스트:\n")
    print(raw)

    try:
        print("\nGPT 요약 중...")
        simplified = gpt_simplify_and_summarize(raw)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gpt_summary_path = os.path.join("result", f"gpt_summary_{timestamp}.txt")
        with open(gpt_summary_path, "w", encoding="utf-8") as f:
            f.write(simplified + "\n")

        print(f"\nGPT 요약 저장 완료 → {gpt_summary_path}")

        # print("\nKoT5 최종 요약 중...")
        # final = refine_summary_kot5(simplified)

        # print("\nKobart 최종 요약 중...")
        final = final_summary(simplified)

        print("")
        print("\n최종 요약 결과:\n")
        print(final)

        summary_path = os.path.join("result", f"final_summary_{timestamp}.txt")

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(final + "\n")

        print(f"\n최종 요약 저장 완료 → {summary_path}")

    except Exception as e:
        print("요약 중 오류 발생:")
        print(str(e))
