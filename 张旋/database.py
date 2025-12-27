from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# MongoDB连接配置
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "library_system")

# 创建MongoDB客户端（支持MongoDB 6.0+）
client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi('1'),
    maxPoolSize=10,
    minPoolSize=1
)

# 获取数据库实例
db = client[MONGODB_DB_NAME]

# 验证连接
try:
    client.admin.command('ping')
    print("✅ MongoDB连接成功")
except Exception as e:
    print(f"❌ MongoDB连接失败: {e}")

# 获取集合（表）的快捷方式
users_collection = db["users"]
books_collection = db["books"]
borrow_records_collection = db["borrow_records"]

# 创建索引（提升查询性能）
def create_indexes():
    # 用户集合索引
    users_collection.create_index("username", unique=True)
    users_collection.create_index("email", unique=True)
    # 图书集合索引
    books_collection.create_index("isbn", unique=True)
    books_collection.create_index("title")
    books_collection.create_index("author")
    books_collection.create_index("status")
    # 借阅记录索引
    borrow_records_collection.create_index("user_id")
    borrow_records_collection.create_index("book_id")
    borrow_records_collection.create_index("status")
    borrow_records_collection.create_index("due_date")

# 初始化索引
create_indexes()