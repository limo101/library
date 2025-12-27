from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, EmailStr
from services import (
    create_user, authenticate_user, get_user_by_id,
    create_book, search_books, get_book_by_id,
    borrow_book, return_book, get_user_borrow_records, get_borrow_record_by_id
)

# 创建总路由
router = APIRouter()

# ---------------------- 用户API ----------------------
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    is_admin: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/users/register", summary="用户注册", tags=["用户管理"])
def register_user(user: UserCreate):
    try:
        return create_user(user.username, user.password, user.email, user.is_admin)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/login", summary="用户登录", tags=["用户管理"])
def login_user(user: UserLogin):
    try:
        user_info = authenticate_user(user.username, user.password)
        return {
            "id": user_info["_id"],
            "username": user_info["username"],
            "email": user_info["email"],
            "is_admin": user_info["is_admin"],
            "message": "登录成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/users/{user_id}", summary="获取用户信息", tags=["用户管理"])
def get_user(user_id: str):
    try:
        return get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------------------- 图书API ----------------------
class BookCreate(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    location: str

@router.post("/books/add", summary="添加图书", tags=["图书管理"])
def add_book(book: BookCreate):
    try:
        return create_book(book.isbn, book.title, book.author, book.publisher, book.location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/books/search", summary="搜索图书", tags=["图书管理"])
def search_book_api(
    isbn: str = Query(None, description="ISBN编号"),
    title: str = Query(None, description="图书名称"),
    author: str = Query(None, description="作者"),
    publisher: str = Query(None, description="出版社"),
    status: str = Query(None, description="图书状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
):
    try:
        return search_books(isbn, title, author, publisher, status, page, page_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/books/{book_id}", summary="获取图书详情", tags=["图书管理"])
def get_book(book_id: str):
    try:
        return get_book_by_id(book_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------------------- 借阅API ----------------------
@router.post("/borrow/borrow", summary="借书操作", tags=["借阅管理"])
def borrow_book_api(
    user_id: str = Query(..., description="用户ID"),
    book_id: str = Query(..., description="图书ID"),
):
    try:
        return borrow_book(user_id, book_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/borrow/return", summary="还书操作", tags=["借阅管理"])
def return_book_api(
    borrow_id: str = Query(..., description="借阅记录ID"),
):
    try:
        return return_book(borrow_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/borrow/records/{user_id}", summary="获取用户借阅记录", tags=["借阅管理"])
def get_borrow_records(
    user_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
):
    try:
        return get_user_borrow_records(user_id, page, page_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/borrow/record/{borrow_id}", summary="获取借阅记录详情", tags=["借阅管理"])
def get_borrow_record(borrow_id: str):
    try:
        return get_borrow_record_by_id(borrow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))