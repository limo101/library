from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis import router
import database  # 初始化MongoDB连接

# 创建FastAPI应用
app = FastAPI(
    title="图书管理系统API（MongoDB版）",
    description="基于MongoDB的简易图书管理系统后端API",
    version="1.0.0"
)

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(router)

# 根路径
@app.get("/", summary="健康检查")
def root():
    return {
        "message": "图书管理系统API（MongoDB版）运行正常",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )