一、环境准备（必做）
1. 安装 MongoDB
本地部署：下载对应系统的 MongoDB 安装包（https://www.mongodb.com/try/download/community），安装后启动 MongoDB 服务（默认端口 27017）；
验证：打开终端输入mongod --version，能显示版本即安装成功。
2. 安装 Python 依赖
在「张旋」根目录下新建requirements.txt文件，粘贴以下内容：
txt
# 后端核心依赖
fastapi>=0.104.1,<0.110.0
uvicorn[standard]>=0.24.0,<0.28.0
pymongo>=4.6.1,<4.10.0
python-jose[cryptography]>=3.3.0,<3.5.0
bcrypt>=4.0.1,<4.2.0
python-multipart>=0.0.6

# 前端核心依赖
streamlit>=1.28.0,<1.35.0
requests>=2.31.0,<2.32.0

# 辅助依赖
python-dotenv>=1.0.0,<1.3.0
pandas>=2.0.3,<2.2.0
打开终端，进入「张旋」根目录，执行安装命令：
bash
运行
pip install -r requirements.txt
二、文件确认（必做）
确认「张旋」根目录下有以下文件（缺一不可）：
database.py（MongoDB 配置）、models.py（数据模型）、services.py（业务逻辑）
apis.py（API 接口）、main.py（后端入口）、frontend.py（前端页面）
.env（环境变量）、requirements.txt（依赖清单）
三、启动步骤（按顺序执行）
1. 启动后端服务
打开终端，进入「张旋」根目录；
执行启动命令：
bash
运行
python main.py
验证：终端显示「✅ MongoDB 连接成功」且无报错，访问http://localhost:8000/docs能看到 API 文档页面，说明后端启动成功。
2. 启动前端页面
新建一个终端（不要关闭后端终端），仍进入「张旋」根目录；
执行启动命令：
bash
运行
streamlit run frontend.py
验证：终端显示「You can now view your Streamlit app in your browser」，自动打开http://localhost:8501页面，说明前端启动成功。
四、核心操作流程
用户注册：前端页面选「用户注册」，输入用户名、密码、邮箱，可勾选「注册为管理员」；
用户登录：用注册的账号登录，管理员账号可看到「图书入库」功能，普通用户无此权限；
图书入库（管理员）：登录管理员账号，进入「图书入库」，填写 ISBN、书名等信息提交；
图书查询：所有用户均可进入「图书查询」，输入书名 / 作者等条件搜索图书；
借书 / 还书：登录普通用户账号，复制图书 ID 完成借书，复制借阅记录 ID 完成还书。
五、常见问题排查
后端启动报错「MongoDB 连接失败」：检查 MongoDB 服务是否启动，.env中MONGODB_URI是否正确；
前端启动报错「模块找不到」：确认依赖已安装，终端执行pip list检查 streamlit/requests 是否存在；
借书 / 还书提示「ID 格式错误」：确保输入的是 MongoDB 的 ObjectId（如658a7b2c8d9e0f1234567890），而非其他格式。
六、停止服务
前端：在前端终端按Ctrl+C，确认停止即可；
后端：在后端终端按Ctrl+C，MongoDB 服务可保留运行（下次启动无需重新开启）。
