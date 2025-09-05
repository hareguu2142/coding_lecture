# main.py
# ------------------------------------------------------------
# 두 수의 사칙연산 API (FastAPI) - 단순화 버전
# ------------------------------------------------------------

from fastapi import FastAPI, HTTPException
import math

# ---------------------------
# 비즈니스 로직
# ---------------------------
def compute(a: float, b: float, op: str) -> float:
    if not math.isfinite(a) or not math.isfinite(b):
        raise HTTPException(status_code=400, detail="유한한 실수만 허용합니다 (Inf/NaN 불가).")

    if op == "add":
        return a + b
    elif op == "sub":
        return a - b
    elif op == "mul":
        return a * b
    elif op == "div":
        if b == 0:
            raise HTTPException(status_code=400, detail="0으로 나눌 수 없습니다.")
        return a / b
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 연산자입니다. (add, sub, mul, div 중 하나를 사용하세요.)")


# ---------------------------
# FastAPI 앱 설정
# ---------------------------
app = FastAPI(
    title="두 수 사칙연산 API (단순화)",
    version="1.0.0",
    description="두 실수를 입력받아 사칙연산을 수행하는 단순화된 API입니다."
)


# ---------------------------
# 기본/헬스 엔드포인트
# ---------------------------
@app.get("/")
def root():
    return {
        "message": "두 수 사칙연산 API에 오신 것을 환영합니다.",
        "try": ["/docs", "/calc?op=add&a=3&b=5"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------
# 단일 /calc 엔드포인트 (GET/POST 모두 지원)
# 예) GET /calc?op=add&a=3&b=5
# 예) POST /calc body: {"op":"add", "a":3, "b":5}
# ---------------------------
@app.api_route("/calc", methods=["GET", "POST"])
def calc(op: str, a: float, b: float):
    result = compute(a, b, op)
    return {"a": a, "b": b, "operator": op, "result": result}


# ---------------------------
# 로컬 실행 진입점
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
