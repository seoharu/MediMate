import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt_simplify_and_summarize(raw_text: str) -> str:
    system_prompt = (
        "당신은 음성 인식 결과를 요약하는 전문가입니다. "
        "다음 인식 결과에서 어려운 용어는 누구나 이해할 수 있게 풀어 쓰고, "
        "핵심만 요약해 주세요."
    )
    user_prompt = f"다음은 음성 인식 결과입니다. 읽기 쉽고 간결하게 요약해 주세요:\n\n{raw_text}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=400
    )

    return response.choices[0].message.content.strip()
