from datetime import datetime
from bson import ObjectId
from models import (
    create_user_document, verify_user_password,
    create_book_document, BOOK_STATUS,
    create_borrow_record_document, BORROW_STATUS, check_borrow_overdue,
    convert_objectid_to_str
)
from database import users_collection, books_collection, borrow_records_collection

# ---------------------- 用户业务逻辑 ----------------------
def create_user(username: str, password: str, email: str, is_admin: bool = False):
    """创建新用户"""
    # 检查用户名是否已存在
    if users_collection.find_one({"username": username}):
        raise ValueError("用户名已存在")
    
    # 检查邮箱是否已存在
    if users_collection.find_one({"email": email}):
        raise ValueError("邮箱已存在")
    
    # 创建用户文档
    user_doc = create_user_document(username, password, email, is_admin)
    result = users_collection.insert_one(user_doc)
    
    # 返回创建的用户信息（转换ObjectId为字符串）
    user = users_collection.find_one({"_id": result.inserted_id})
    return convert_objectid_to_str(user)

def authenticate_user(username: str, password: str):
    """用户登录验证"""
    user_doc = users_collection.find_one({"username": username})
    if not user_doc or not verify_user_password(user_doc, password):
        raise ValueError("用户名或密码错误")
    
    # 返回用户信息（转换ObjectId为字符串）
    return convert_objectid_to_str(user_doc)

def get_user_by_id(user_id: str):
    """根据ID获取用户信息"""
    try:
        user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise ValueError("用户不存在")
        return convert_objectid_to_str(user_doc)
    except:
        raise ValueError("用户ID格式错误")

# ---------------------- 图书业务逻辑 ----------------------
def create_book(isbn: str, title: str, author: str, publisher: str, location: str):
    """添加新图书"""
    # 检查ISBN是否已存在
    if books_collection.find_one({"isbn": isbn}):
        raise ValueError("ISBN已存在")
    
    # 创建图书文档
    book_doc = create_book_document(isbn, title, author, publisher, location)
    result = books_collection.insert_one(book_doc)
    
    # 返回创建的图书信息
    book = books_collection.find_one({"_id": result.inserted_id})
    return convert_objectid_to_str(book)

def search_books(
    isbn: str = None,
    title: str = None,
    author: str = None,
    publisher: str = None,
    status: str = None,
    page: int = 1,
    page_size: int = 10
):
    """多条件搜索图书（分页）"""
    # 构建查询条件
    query = {}
    if isbn:
        query["isbn"] = isbn
    if title:
        # 模糊查询（MongoDB正则）
        query["title"] = {"$regex": title, "$options": "i"}  # i表示不区分大小写
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if publisher:
        query["publisher"] = {"$regex": publisher, "$options": "i"}
    if status and status in BOOK_STATUS.values():
        query["status"] = status
    
    # 分页处理
    skip = (page - 1) * page_size
    total = books_collection.count_documents(query)
    
    # 执行查询
    books_cursor = books_collection.find(query).skip(skip).limit(page_size).sort("created_at", -1)
    books = [convert_objectid_to_str(book) for book in books_cursor]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": books
    }

def update_book_status(book_id: str, status: str):
    """更新图书状态"""
    try:
        # 验证状态合法性
        if status not in BOOK_STATUS.values():
            raise ValueError("无效的图书状态")
        
        # 更新图书
        result = books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": {"status": status, "updated_at": datetime.now()}}
        )
        
        if result.modified_count == 0:
            raise ValueError("图书不存在或状态未变更")
        
        # 返回更新后的图书
        book = books_collection.find_one({"_id": ObjectId(book_id)})
        return convert_objectid_to_str(book)
    except:
        raise ValueError("图书ID格式错误或图书不存在")

def get_book_by_id(book_id: str):
    """根据ID获取图书信息"""
    try:
        book_doc = books_collection.find_one({"_id": ObjectId(book_id)})
        if not book_doc:
            raise ValueError("图书不存在")
        return convert_objectid_to_str(book_doc)
    except:
        raise ValueError("图书ID格式错误")

# ---------------------- 借阅业务逻辑 ----------------------
def borrow_book(user_id: str, book_id: str):
    """借书操作"""
    # 检查图书状态
    book = get_book_by_id(book_id)
    if book["status"] != BOOK_STATUS["AVAILABLE"]:
        raise ValueError("该图书不可借阅")
    
    # 创建借阅记录
    borrow_doc = create_borrow_record_document(user_id, book_id)
    result = borrow_records_collection.insert_one(borrow_doc)
    
    # 更新图书状态为已借出
    update_book_status(book_id, BOOK_STATUS["BORROWED"])
    
    # 返回借阅记录
    borrow_record = borrow_records_collection.find_one({"_id": result.inserted_id})
    return convert_objectid_to_str(borrow_record)

def return_book(borrow_id: str):
    """还书操作"""
    try:
        # 检查借阅记录
        borrow_record = borrow_records_collection.find_one({"_id": ObjectId(borrow_id)})
        if not borrow_record:
            raise ValueError("借阅记录不存在")
        
        # 转换ObjectId为字符串（便于判断）
        borrow_record = convert_objectid_to_str(borrow_record)
        
        if borrow_record["status"] == BORROW_STATUS["RETURNED"]:
            raise ValueError("该图书已归还")
        
        # 检查是否逾期
        check_borrow_overdue(borrow_record)
        
        # 更新借阅记录
        borrow_records_collection.update_one(
            {"_id": ObjectId(borrow_id)},
            {
                "$set": {
                    "status": BORROW_STATUS["RETURNED"],
                    "return_date": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )
        
        # 更新图书状态为可借阅
        update_book_status(borrow_record["book_id"], BOOK_STATUS["AVAILABLE"])
        
        # 返回更新后的借阅记录
        updated_record = borrow_records_collection.find_one({"_id": ObjectId(borrow_id)})
        return convert_objectid_to_str(updated_record)
    except:
        raise ValueError("借阅记录ID格式错误或记录不存在")

def get_user_borrow_records(user_id: str, page: int = 1, page_size: int = 10):
    """获取用户借阅记录（分页）"""
    try:
        # 构建查询条件
        query = {"user_id": ObjectId(user_id)}
        
        # 先检查所有记录的逾期状态
        records_cursor = borrow_records_collection.find(query)
        for record in records_cursor:
            check_borrow_overdue(record)
        
        # 分页查询
        skip = (page - 1) * page_size
        total = borrow_records_collection.count_documents(query)
        records_cursor = borrow_records_collection.find(query).skip(skip).limit(page_size).sort("borrow_date", -1)
        
        # 转换格式并返回
        records = [convert_objectid_to_str(record) for record in records_cursor]
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": records
        }
    except:
        raise ValueError("用户ID格式错误")

def get_borrow_record_by_id(borrow_id: str):
    """根据ID获取借阅记录"""
    try:
        record_doc = borrow_records_collection.find_one({"_id": ObjectId(borrow_id)})
        if not record_doc:
            raise ValueError("借阅记录不存在")
        return convert_objectid_to_str(record_doc)
    except:
        raise ValueError("借阅记录ID格式错误")