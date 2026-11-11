import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# 임시 주문 데이터 (추후 Spring Boot API로 교체)
ORDERS = {
    "1001": {"owner": "userA", "status": "배송 중"},
    "1002": {"owner": "userB", "status": "배송 완료"}
}


# 현재 로그인한 사용자(가정)
CURRENT_USER = "userA"


# AI Agent가 사용할 도구
def get_order_status(order_id):
    order = ORDERS.get(order_id)

    if order is None:
        return {"error": "존재하지 않는 주문입니다."}

    # AI의 판단과 관계없이 Python에서 권한 검증
    if order["owner"] != CURRENT_USER:
        return {"error": "조회 권한이 없습니다."}

    return {
        "order_id": order_id,
        "status": order["status"]
    }


# LLM에 제공할 도구 명세
tools = [{
    "type": "function",
    "name": "get_order_status",
    "description": "주문번호를 이용해 배송 상태를 조회합니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "조회할 주문번호"
            }
        },
        "required": ["order_id"],
        "additionalProperties": False
    },
    "strict": True
}]

def run_agent(message):
    response = client.responses.create(
        model="gpt-6-luna",
        reasoning={"effort": "none"},
        instructions=(
            "당신은 주문 조회 AI Agent입니다. "
            "주문 정보가 필요하면 도구를 사용하세요. "
            "도구 결과에 없는 주문 정보는 만들어내지 마세요."
        ),
        input=message,
        tools=tools,
        max_output_tokens=300
    )

    input_items = [*response.output]

    # 도구 호출은 최대 1회만 허용
    for item in response.output:
        if item.type != "function_call":
            continue

        print("호출된 도구:", item.name)

        if item.name != "get_order_status":
            result = {"error": "허용되지 않은 도구입니다."}
        else:
            try:
                args = json.loads(item.arguments)
                result = get_order_status(args["order_id"])
            except (ValueError, KeyError, TypeError):
                result = {"error": "잘못된 도구 인자입니다."}

        print("도구 실행 결과:", result)

        input_items.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result, ensure_ascii=False)
        })

    if any(item.type == "function_call" for item in response.output):
        response = client.responses.create(
            model="gpt-6-luna",
            reasoning={"effort": "none"},
            instructions=(
                "당신은 주문 조회 AI Agent입니다. "
                "도구 결과에 근거해서만 답하세요. "
                "권한이 없으면 주문 정보를 공개하지 마세요."
            ),
            input=input_items,
            tools=tools,
            tool_choice="none",
            max_output_tokens=300
        )

    print("Agent 응답:", response.output_text)

run_agent("1002번 주문의 배송 상태를 알려줘.")