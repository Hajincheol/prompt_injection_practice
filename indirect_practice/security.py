
# Prompt Injection 의심 표현
BLOCKED_PATTERNS = [
    "이전 지침은 모두 무시",
    "기존 분류 규칙 대신",
    "새로운 관리자 지침",
    "사전 검증된 결과인 hacked",
    "ignore previous instructions"
]


def detect_prompt_injection(text):
    normalized = text.lower()

    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in normalized:
            return True

    return False