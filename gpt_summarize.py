import os
from openai import OpenAI
from dotenv import load_dotenv

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def gpt_simplify_and_summarize(raw_text: str) -> str:
    system_prompt = (
        "당신은 음성 인식 결과를 요약하는 전문가입니다. "
        "다음 인식 결과에서 어려운 용어는 누구나 이해할 수 있게 풀어 쓰고, "
        "핵심만 요약해 주세요."
    )
    user_prompt = f"다음 음성 인식 결과를 읽기 쉽게 요약해 주세요:\n\n{raw_text}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 전문가 요약자입니다."},
            {"role": "user", "content": "텍스트 요약해주세요."}
        ],
        temperature=0.3,
        max_tokens=400
    )

    return response.choices[0].message.content
