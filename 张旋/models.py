import bcrypt
from datetime import datetime, timedelta
from bson import ObjectId
from database import borrow_records_collection

# ---------------------- 常量定义（替代枚举） ----------------------
# 图书状态
BOOK_STATUS = {
    "AVAILABLE": "available",  # 可借阅
    "BORROWED": "borrowed",    # 已借出
    "LOST": "lost",            # 丢失
    "DAMAGED": "damaged"       # 损坏
}

# 借阅状态
BORROW_STATUS = {
    "BORROWED": "borrowed",    # 借阅中
    "RETURNED": "returned",    # 已归还
    "OVERDUE": "overdue"       # 逾期
}

# ---------------------- 用户模型工具函数 ----------------------
def create_user_document(username: str, password: str, email: str, is_admin: bool = False):
    """创建用户文档"""
    # 密码加密
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    return {
        "username": username,
        "password_hash": password_hash,
        "email": email,
        "is_admin": is_admin,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

def verify_user_password(user_doc: dict, password: str) -> bool:
    """验证用户密码"""
    return bcrypt.checkpw(password.encode('utf-8'), user_doc["password_hash"].encode('utf-8'))

# ---------------------- 图书模型工具函数 ----------------------
def create_book_document(isbn: str, title: str, author: str, publisher: str, location: str):
    """创建图书文档"""
    return {
        "isbn": isbn,
        "title": title,
        "author": author,
        "publisher": publisher,
        "location": location,
        "status": BOOK_STATUS["AVAILABLE"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

# ---------------------- 借阅模型工具函数 ----------------------
def create_borrow_record_document(user_id: str, book_id: str):
    """创建借阅记录文档"""
    return {
        "user_id": ObjectId(user_id),  # 引用用户ID（ObjectId类型）
        "book_id": ObjectId(book_id),  # 引用图书ID（ObjectId类型）
        "borrow_date": datetime.now(),
        "due_date": datetime.now() + timedelta(days=30),  # 30天借阅期
        "return_date": None,
        "status": BORROW_STATUS["BORROWED"]
    }

def check_borrow_overdue(record_doc: dict) -> bool:
    """检查借阅是否逾期"""
    if record_doc["status"] == BORROW_STATUS["BORROWED"] and datetime.now() > record_doc["due_date"]:
        # 更新为逾期状态
        borrow_records_collection.update_one(
            {"_id": record_doc["_id"]},
            {"$set": {"status": BORROW_STATUS["OVERDUE"], "updated_at": datetime.now()}}
        )
        return True
    return False

# ---------------------- 通用工具函数 ----------------------
def convert_objectid_to_str(doc: dict) -> dict:
    """将文档中的ObjectId转换为字符串（便于前端展示）"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    # 转换嵌套的ObjectId
    if "user_id" in doc and isinstance(doc["user_id"], ObjectId):
        doc["user_id"] = str(doc["user_id"])
    if "book_id" in doc and isinstance(doc["book_id"], ObjectId):
        doc["book_id"] = str(doc["book_id"])
    return doc