from dotenv import load_dotenv
from openai import OpenAI
from openai.types.shared_params import reasoning

load_dotenv()

client = OpenAI()
res = client.responses.create(
    model="gpt-6-luna",
    reasoning={"effort": "none"},
    instructions="당신은 친절한 AI 보안 학습 도우미입니다.",
    input="Prompt Injection이 무엇인지 한 문장으로 설명해 줘.",
    max_output_tokens=150
)

print(res.output_text)

# 실제 사용한 토큰 확인
print("입력 토큰:", res.usage.input_tokens)
print("출력 토큰:", res.usage.output_tokens)