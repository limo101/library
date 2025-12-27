import streamlit as st
import requests
import json
from datetime import datetime

# 页面基本配置
st.set_page_config(
    page_title="图书管理系统（MongoDB版）",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API基础地址
API_BASE_URL = "http://localhost:8000"

# 初始化会话状态
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

init_session_state()

# 工具函数：格式化日期
def format_datetime(dt_obj):
    if not dt_obj:
        return "无"
    try:
        # MongoDB返回的日期是ISO格式字符串
        if isinstance(dt_obj, str):
            dt = datetime.fromisoformat(dt_obj.replace("Z", "+00:00"))
        else:
            dt = dt_obj
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(dt_obj)

# 侧边栏
st.sidebar.title("📚 图书管理系统（MongoDB版）")

# 登录状态判断
if st.session_state.logged_in:
    st.sidebar.success(f"当前用户：{st.session_state.user['username']}")
    st.sidebar.info(f"用户类型：{'管理员' if st.session_state.user['is_admin'] else '普通用户'}")
    
    # 功能菜单
    menu_options = ["首页", "图书查询", "借阅管理"]
    if st.session_state.user["is_admin"]:
        menu_options.insert(2, "图书入库")
    choice = st.sidebar.selectbox("功能菜单", menu_options)
    
    # 退出登录按钮
    if st.sidebar.button("退出登录", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
else:
    # 未登录时的菜单
    choice = st.sidebar.selectbox("功能菜单", ["首页", "用户注册", "用户登录"])

# 首页
if choice == "首页":
    st.title("欢迎使用图书管理系统（MongoDB版）")
    st.markdown("---")
    
    if st.session_state.logged_in:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📖 快速操作")
            if st.session_state.user["is_admin"]:
                st.button("添加新图书", on_click=lambda: st.session_state.update(current_page="图书入库"))
            st.button("查询图书", on_click=lambda: st.session_state.update(current_page="图书查询"))
            st.button("我的借阅记录", on_click=lambda: st.session_state.update(current_page="借阅管理"))
        
        with col2:
            st.subheader("ℹ️ 系统信息")
            st.info("""
            - 基于MongoDB文档型数据库开发
            - 支持多条件图书模糊查询
            - 实时借阅状态更新、逾期自动校验
            - 密码加密存储，数据索引优化
            """)
    else:
        st.info("""
        ### 系统介绍
        这是基于MongoDB的图书管理系统，支持：
        - 图书入库、多条件模糊查询
        - 用户注册/登录（区分管理员/普通用户）
        - 借书/还书操作，逾期自动校验
        
        ### 使用说明
        1. 点击左侧菜单进行用户注册
        2. 使用注册的账号登录系统
        3. 普通用户可查询图书、借阅/归还图书
        4. 管理员可添加图书、管理借阅记录
        """)

# 用户注册
elif choice == "用户注册":
    st.title("📝 用户注册")
    st.markdown("---")
    
    with st.form("register_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("用户名", placeholder="请输入用户名", max_chars=50)
            password = st.text_input("密码", type="password", placeholder="请输入密码")
        with col2:
            email = st.text_input("邮箱", placeholder="请输入邮箱", max_chars=100)
            is_admin = st.checkbox("注册为管理员", help="管理员可添加图书")
        
        submit_btn = st.form_submit_button("提交注册", type="primary")
        
        if submit_btn:
            if not username or not password or not email:
                st.error("❌ 请填写完整的注册信息")
            else:
                try:
                    # 调用注册接口
                    response = requests.post(
                        f"{API_BASE_URL}/users/register",
                        json={
                            "username": username,
                            "password": password,
                            "email": email,
                            "is_admin": is_admin
                        }
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ 注册成功！请前往登录页面")
                    else:
                        st.error(f"❌ 注册失败：{response.json().get('detail', '未知错误')}")
                except Exception as e:
                    st.error(f"❌ 请求失败：{str(e)}")

# 用户登录
elif choice == "用户登录":
    st.title("🔑 用户登录")
    st.markdown("---")
    
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        submit_btn = st.form_submit_button("登录", type="primary")
        
        if submit_btn:
            if not username or not password:
                st.error("❌ 请填写用户名和密码")
            else:
                try:
                    # 调用登录接口
                    response = requests.post(
                        f"{API_BASE_URL}/users/login",
                        json={"username": username, "password": password}
                    )
                    
                    if response.status_code == 200:
                        st.session_state.logged_in = True
                        st.session_state.user = response.json()
                        st.success("✅ 登录成功！")
                        st.rerun()
                    else:
                        st.error(f"❌ 登录失败：{response.json().get('detail', '用户名或密码错误')}")
                except Exception as e:
                    st.error(f"❌ 请求失败：{str(e)}")

# 图书入库（仅管理员）
elif choice == "图书入库":
    if not st.session_state.logged_in:
        st.error("❌ 请先登录系统")
    elif not st.session_state.user["is_admin"]:
        st.error("❌ 仅管理员可执行此操作")
    else:
        st.title("📥 图书入库")
        st.markdown("---")
        
        with st.form("add_book_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                isbn = st.text_input("ISBN编号", placeholder="如：9787115546081", max_chars=20)
                title = st.text_input("图书名称", placeholder="请输入书名", max_chars=200)
                author = st.text_input("作者", placeholder="请输入作者姓名", max_chars=100)
            with col2:
                publisher = st.text_input("出版社", placeholder="请输入出版社名称", max_chars=100)
                location = st.text_input("馆藏位置", placeholder="如：A区1排2架", max_chars=50)
            
            submit_btn = st.form_submit_button("提交入库", type="primary")
            
            if submit_btn:
                if not all([isbn, title, author, publisher, location]):
                    st.error("❌ 请填写完整的图书信息")
                else:
                    try:
                        # 调用添加图书接口
                        response = requests.post(
                            f"{API_BASE_URL}/books/add",
                            json={
                                "isbn": isbn,
                                "title": title,
                                "author": author,
                                "publisher": publisher,
                                "location": location
                            }
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ 图书入库成功！")
                        else:
                            st.error(f"❌ 入库失败：{response.json().get('detail', '未知错误')}")
                    except Exception as e:
                        st.error(f"❌ 请求失败：{str(e)}")

# 图书查询
elif choice == "图书查询":
    st.title("🔍 图书查询")
    st.markdown("---")
    
    # 查询条件
    col1, col2, col3 = st.columns(3)
    with col1:
        isbn = st.text_input("ISBN编号", placeholder="精确匹配")
        title = st.text_input("图书名称", placeholder="模糊匹配")
    with col2:
        author = st.text_input("作者", placeholder="模糊匹配")
        publisher = st.text_input("出版社", placeholder="模糊匹配")
    with col3:
        status = st.selectbox(
            "图书状态",
            ["", "available", "borrowed", "lost", "damaged"],
            format_func=lambda x: {"": "全部", "available": "可借阅", "borrowed": "已借出", "lost": "丢失", "damaged": "损坏"}[x]
        )
    
    # 分页控制
    col4, col5, col6 = st.columns(3)
    with col4:
   # 确保current_page是整数类型
        page = st.number_input("页码", min_value=1, value=int(st.session_state.current_page))
    with col5:
        page_size = st.number_input("每页条数", min_value=1, max_value=50, value=10)
    with col6:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("开始查询", type="primary")
    
    # 执行查询
    if search_btn or st.session_state.current_page != page:
        st.session_state.current_page = page
        
        try:
            # 构建查询参数
            params = {
                "page": page,
                "page_size": page_size
            }
            if isbn:
                params["isbn"] = isbn
            if title:
                params["title"] = title
            if author:
                params["author"] = author
            if publisher:
                params["publisher"] = publisher
            if status:
                params["status"] = status
            
            # 调用查询接口
            response = requests.get(f"{API_BASE_URL}/books/search", params=params)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ 查询成功，共找到 {result['total']} 条记录")
                st.markdown("---")
                
                # 展示结果
                if result["data"]:
                    # 转换数据格式
                    display_data = []
                    for book in result["data"]:
                        display_data.append({
                            "ID": book["_id"],  # MongoDB用_id替代id
                            "ISBN": book["isbn"],
                            "书名": book["title"],
                            "作者": book["author"],
                            "出版社": book["publisher"],
                            "馆藏位置": book["location"],
                            "状态": {"available": "可借阅", "borrowed": "已借出", "lost": "丢失", "damaged": "损坏"}[book["status"]],
                            "创建时间": format_datetime(book["created_at"])
                        })
                    
                    # 显示表格
                    st.dataframe(display_data, use_container_width=True)
                    
                    # 分页按钮
                    col7, col8, col9 = st.columns(3)
                    with col7:
                        if page > 1:
                            if st.button("上一页"):
                                st.session_state.current_page = page - 1
                                st.rerun()
                    with col8:
                        total_pages = (result["total"] + page_size - 1) // page_size
                        st.write(f"第 {page} 页 / 共 {total_pages} 页")
                    with col9:
                        if page < total_pages:
                            if st.button("下一页"):
                                st.session_state.current_page = page + 1
                                st.rerun()
                else:
                    st.warning("⚠️ 未查询到符合条件的图书")
            else:
                st.error(f"❌ 查询失败：{response.json().get('detail', '未知错误')}")
        except Exception as e:
            st.error(f"❌ 请求失败：{str(e)}")

# 借阅管理
elif choice == "借阅管理":
    st.title("📖 借阅管理")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["借书", "还书", "我的借阅记录"])
    
    # 借书
    with tab1:
        with st.form("borrow_form", clear_on_submit=True):
            book_id = st.text_input("图书ID", placeholder="从图书查询页面复制图书ID（MongoDB ObjectId）")
            submit_borrow = st.form_submit_button("确认借书", type="primary")
            
            if submit_borrow:
                if not book_id:
                    st.error("❌ 请输入图书ID")
                else:
                    try:
                        # 调用借书接口
                        response = requests.post(
                            f"{API_BASE_URL}/borrow/borrow",
                            params={
                                "user_id": st.session_state.user["id"],
                                "book_id": book_id
                            }
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ 借书成功！")
                        else:
                            st.error(f"❌ 借书失败：{response.json().get('detail', '未知错误')}")
                    except Exception as e:
                        st.error(f"❌ 请求失败：{str(e)}")
    
    # 还书
    with tab2:
        with st.form("return_form", clear_on_submit=True):
            borrow_id = st.text_input("借阅记录ID", placeholder="从我的借阅记录页面复制记录ID")
            submit_return = st.form_submit_button("确认还书", type="primary")
            
            if submit_return:
                if not borrow_id:
                    st.error("❌ 请输入借阅记录ID")
                else:
                    try:
                        # 调用还书接口
                        response = requests.post(
                            f"{API_BASE_URL}/borrow/return",
                            params={"borrow_id": borrow_id}
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ 还书成功！")
                        else:
                            st.error(f"❌ 还书失败：{response.json().get('detail', '未知错误')}")
                    except Exception as e:
                        st.error(f"❌ 请求失败：{str(e)}")
    
    # 我的借阅记录
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            page = st.number_input("页码", min_value=1, value=1)
        with col2:
            page_size = st.number_input("每页条数", min_value=1, max_value=50, value=10)
        
        if st.button("查询我的借阅记录", type="primary"):
            try:
                # 调用借阅记录接口
                response = requests.get(
                    f"{API_BASE_URL}/borrow/records/{st.session_state.user['id']}",
                    params={"page": page, "page_size": page_size}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ 查询成功，共找到 {result['total']} 条借阅记录")
                    st.markdown("---")
                    
                    if result["data"]:
                        # 转换数据格式
                        display_data = []
                        for record in result["data"]:
                            display_data.append({
                                "记录ID": record["_id"],
                                "图书ID": record["book_id"],
                                "借阅日期": format_datetime(record["borrow_date"]),
                                "到期日期": format_datetime(record["due_date"]),
                                "归还日期": format_datetime(record["return_date"]),
                                "状态": {"borrowed": "借阅中", "returned": "已归还", "overdue": "逾期"}[record["status"]]
                            })
                        
                        # 显示表格
                        st.dataframe(display_data, use_container_width=True)
                    else:
                        st.warning("⚠️ 暂无借阅记录")
                else:
                    st.error(f"❌ 查询失败：{response.json().get('detail', '未知错误')}")
            except Exception as e:
                st.error(f"❌ 请求失败：{str(e)}")