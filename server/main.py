"""
FastAPI 应用入口模块

职责：
1. 创建 FastAPI 应用；
2. 配置跨域中间件（CORS）；
3. 注册全部业务路由；
4. 统一参数校验异常与未知异常的响应格式。

启动命令（在 server 目录下）：
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import json

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, chat, documents, history, knowledge, stats, users

# 创建 FastAPI 应用
app = FastAPI(
    title="企业知识库问答系统 API",
    description="基于 LangChain + Chroma + 阿里云百炼 的 RAG 问答后端服务",
    version="1.0.0",
)

# 配置 CORS：允许前端 Vite 默认地址（5173）跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全部路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(knowledge.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(stats.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    统一处理请求参数校验异常，返回结构化错误信息。

    :param request: 请求对象
    :param exc: 校验异常
    :return: 422 JSON 响应
    """
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "请求参数校验失败",
            "detail": json.loads(exc.json()),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局兜底异常处理，避免向前端暴露堆栈信息。

    :param request: 请求对象
    :param exc: 未被捕获的异常
    :return: 500 JSON 响应
    """
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": f"服务器内部错误：{exc}"},
    )


@app.get("/", tags=["默认接口"], summary="服务健康检查")
def root():
    """
    根路径健康检查接口。

    :return: 服务运行状态
    """
    return {"code": 200, "message": "企业知识库问答系统后端服务运行中"}


if __name__ == "__main__":
    """
    直接运行入口：支持在 PyCharm 中右键运行/调试 main.py。

    说明：调试时不开启 reload（热重载会额外启动子进程，导致断点不生效）；
    若需要修改代码后自动重启，可把 reload 改为 True。
    """
    import uvicorn

    # 以字符串方式传入应用路径，便于后续开启 reload
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
