# main.py
# ------------------------------------------------------------
# 두 수의 사칙연산 API (FastAPI)
# - /docs 에서 자동 문서와 실습 가능 (Swagger UI)
# - GET(쿼리스트링) & POST(JSON 본문) 모두 지원
# - 0으로 나누기, 비유한수(Inf/NaN) 등 기본 검증 포함
# ------------------------------------------------------------

from enum import Enum
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import math

# ---------------------------
# 데이터 모델
# ---------------------------
class Numbers(BaseModel):
    a: float = Field(..., description="첫 번째 수", examples=[3, 3.14])
    b: float = Field(..., description="두 번째 수", examples=[4, 2.5])

    # Pydantic v2 스타일 유효성 검사 (FastAPI 최신 버전 기준)
    @field_validator("a", "b")
    @classmethod
    def must_be_finite(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("유한한 실수만 허용합니다 (Inf/NaN 불가).")
        return v


class Op(str, Enum):
    add = "add"   # 덧셈
    sub = "sub"   # 뺄셈
    mul = "mul"   # 곱셈
    div = "div"   # 나눗셈


class OperationResponse(BaseModel):
    a: float
    b: float
    operator: Op
    result: float


# ---------------------------
# 비즈니스 로직
# ---------------------------
def compute(a: float, b: float, op: Op) -> float:
    if op == Op.add:
        return a + b
    if op == Op.sub:
        return a - b
    if op == Op.mul:
        return a * b
    if op == Op.div:
        if b == 0:
            raise HTTPException(status_code=400, detail="0으로 나눌 수 없습니다.")
        return a / b
    # 방어적 코드
    raise HTTPException(status_code=400, detail="지원하지 않는 연산자입니다.")


# ---------------------------
# FastAPI 앱 설정
# ---------------------------
app = FastAPI(
    title="두 수 사칙연산 API",
    version="1.0.0",
    description="""
두 실수를 입력받아 사칙연산을 수행하는 학습용 API입니다.

- **GET /calc** : 쿼리스트링으로 연산 (예: /calc?op=add&a=3&b=5)
- **POST /calc/{op}** : JSON 본문으로 연산 (예: /calc/add, body: {"a":3,"b":5})
- **단축 엔드포인트** : /add, /sub, /mul, /div (POST)
- **문서** : /docs (Swagger UI), /redoc
""",
)

# CORS (수업용: 모든 출처 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
# GET 방식 (쿼리스트링)
# 예) /calc?op=mul&a=2.5&b=4
# ---------------------------
@app.get("/calc", response_model=OperationResponse)
def calc_query(op: Op, a: float, b: float):
    if not math.isfinite(a) or not math.isfinite(b):
        raise HTTPException(status_code=400, detail="유한한 실수만 허용합니다 (Inf/NaN 불가).")
    result = compute(a, b, op)
    return OperationResponse(a=a, b=b, operator=op, result=result)


# ---------------------------
# POST 방식 (JSON 본문)
# 예) POST /calc/add  body: {"a":3,"b":5}
# ---------------------------
@app.post("/calc/{op}", response_model=OperationResponse)
def calc_body(op: Op, payload: Numbers):
    result = compute(payload.a, payload.b, op)
    return OperationResponse(a=payload.a, b=payload.b, operator=op, result=result)


# ---------------------------
# 단축 엔드포인트 (POST)
# ---------------------------
@app.post("/add", response_model=OperationResponse)
def add(payload: Numbers):
    return OperationResponse(a=payload.a, b=payload.b, operator=Op.add, result=compute(payload.a, payload.b, Op.add))


@app.post("/sub", response_model=OperationResponse)
def sub(payload: Numbers):
    return OperationResponse(a=payload.a, b=payload.b, operator=Op.sub, result=compute(payload.a, payload.b, Op.sub))


@app.post("/mul", response_model=OperationResponse)
def mul(payload: Numbers):
    return OperationResponse(a=payload.a, b=payload.b, operator=Op.mul, result=compute(payload.a, payload.b, Op.mul))


@app.post("/div", response_model=OperationResponse)
def div(payload: Numbers):
    return OperationResponse(a=payload.a, b=payload.b, operator=Op.div, result=compute(payload.a, payload.b, Op.div))


# ---------------------------
# 로컬 실행 진입점
# ---------------------------
if __name__ == "__main__":
    import uvicorn

    # reload=True 는 수업 중 코드 수정 시 자동 반영에 편리합니다.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
