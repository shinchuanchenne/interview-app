import hashlib
import json
import random
import secrets
from pathlib import Path
from uuid import uuid4

import streamlit as st


USERS_FILE = Path("users.json")
USER_DATA_DIR = Path("user_data")
DEFAULT_CATEGORIES = ["經歷", "前職", "人柄", "專案", "志望動機"]
DEFAULT_CATEGORY = DEFAULT_CATEGORIES[0]


def ensure_users_file() -> None:
    if not USERS_FILE.exists():
        USERS_FILE.write_text("{}", encoding="utf-8")


def ensure_user_data_dir() -> None:
    USER_DATA_DIR.mkdir(exist_ok=True)


def normalize_username(username: str) -> str:
    return username.strip()


def user_file_path(username: str) -> Path:
    safe_name = hashlib.sha256(username.encode("utf-8")).hexdigest()
    return USER_DATA_DIR / f"{safe_name}.json"


def password_hash(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        100_000,
    ).hex()


def load_users() -> dict:
    ensure_users_file()
    try:
        data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    USERS_FILE.write_text("{}", encoding="utf-8")
    return {}


def save_users(users: dict) -> None:
    USERS_FILE.write_text(
        json.dumps(users, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_user(username: str, password: str) -> tuple[bool, str]:
    username = normalize_username(username)
    if not username:
        return False, "請輸入帳號。"
    if not password:
        return False, "請輸入密碼。"

    users = load_users()
    if username in users:
        return False, "這個帳號已經存在。"

    salt = secrets.token_hex(16)
    users[username] = {
        "salt": salt,
        "password_hash": password_hash(password, salt),
    }
    save_users(users)
    ensure_user_data_file(username)
    return True, "帳號建立成功，請使用新帳號登入。"


def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    username = normalize_username(username)
    users = load_users()
    user = users.get(username)

    if not user:
        return False, "找不到這個帳號。"

    expected_hash = user.get("password_hash", "")
    salt = user.get("salt", "")
    if not salt or password_hash(password, salt) != expected_hash:
        return False, "密碼不正確。"

    return True, ""


def ensure_user_data_file(username: str) -> None:
    ensure_user_data_dir()
    file_path = user_file_path(username)
    if not file_path.exists():
        default_payload = {
            "username": username,
            "categories": DEFAULT_CATEGORIES.copy(),
            "items": [],
        }
        file_path.write_text(
            json.dumps(default_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_user_payload(username: str) -> dict:
    ensure_user_data_file(username)
    file_path = user_file_path(username)
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            categories = clean_categories(data.get("categories", []))
            items = normalize_items(data.get("items", []), categories)
            payload = {
                "username": username,
                "categories": categories,
                "items": items,
            }
            save_user_payload(username, payload["categories"], payload["items"])
            return payload
    except json.JSONDecodeError:
        pass

    payload = {
        "username": username,
        "categories": DEFAULT_CATEGORIES.copy(),
        "items": [],
    }
    save_user_payload(username, payload["categories"], payload["items"])
    return payload


def save_user_payload(username: str, categories: list[str], items: list[dict]) -> None:
    ensure_user_data_dir()
    payload = {
        "username": username,
        "categories": clean_categories(categories),
        "items": sort_items(items, clean_categories(categories)),
    }
    user_file_path(username).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def clean_categories(categories: list[str]) -> list[str]:
    cleaned = []
    for category in categories:
        if isinstance(category, str):
            value = category.strip()
            if value and value not in cleaned:
                cleaned.append(value)
    if not cleaned:
        return DEFAULT_CATEGORIES.copy()
    return cleaned


def normalize_item(item: dict, default_order: int, categories: list[str]) -> dict:
    category = item.get("category", DEFAULT_CATEGORY)
    if category not in categories:
        category = categories[0] if categories else DEFAULT_CATEGORY

    return {
        "id": item.get("id", str(uuid4())),
        "category": category,
        "order": int(item.get("order", default_order)),
        "question": item.get("question", "").strip(),
        "points": item.get("points", "").strip(),
        "answer": item.get("answer", "").strip(),
    }


def normalize_items(items: list, categories: list[str]) -> list[dict]:
    if not isinstance(items, list):
        return []
    normalized = [
        normalize_item(item, default_order=index, categories=categories)
        for index, item in enumerate(items)
        if isinstance(item, dict)
    ]
    return sort_items(normalized, categories)


def sort_items(items: list[dict], categories: list[str]) -> list[dict]:
    category_index = {category: index for index, category in enumerate(categories)}
    return sorted(
        items,
        key=lambda item: (category_index.get(item["category"], len(categories)), item.get("order", 0)),
    )


def compact_category_orders(items: list[dict], categories: list[str]) -> list[dict]:
    sorted_items = sort_items(items, categories)
    for category in categories:
        category_items = [item for item in sorted_items if item["category"] == category]
        for index, item in enumerate(category_items):
            item["order"] = index
    return sort_items(sorted_items, categories)


def reorder_category_items(items: list[dict], categories: list[str], category: str, item_id: str, direction: int) -> list[dict]:
    sorted_items = sort_items(items, categories)
    category_items = [item for item in sorted_items if item["category"] == category]
    current_index = next((index for index, item in enumerate(category_items) if item["id"] == item_id), None)

    if current_index is None:
        return sorted_items

    target_index = current_index + direction
    if target_index < 0 or target_index >= len(category_items):
        return sorted_items

    category_items[current_index], category_items[target_index] = (
        category_items[target_index],
        category_items[current_index],
    )

    order_map = {item["id"]: index for index, item in enumerate(category_items)}
    for item in sorted_items:
        if item["category"] == category and item["id"] in order_map:
            item["order"] = order_map[item["id"]]

    return sort_items(sorted_items, categories)


def get_item_by_id(items: list[dict], item_id: str | None) -> dict | None:
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def set_selected_item(item_id: str) -> None:
    st.session_state.selected_item_id = item_id


def pick_random_item(pool: list[dict], current_item_id: str | None) -> dict | None:
    if not pool:
        return None
    candidates = [item for item in pool if item["id"] != current_item_id]
    if not candidates:
        return None
    return random.choice(candidates)


def add_category(categories: list[str], new_name: str) -> tuple[list[str], str | None]:
    cleaned = new_name.strip()
    if not cleaned:
        return categories, "請先輸入分類名稱。"
    if cleaned in categories:
        return categories, "這個分類已經存在。"
    return categories + [cleaned], None


def reset_app_state_for_login() -> None:
    st.session_state.selected_item_id = None
    st.session_state.show_points = True
    st.session_state.show_answer = True
    st.session_state.category_edit_target = None
    st.session_state.category_message = None


def render_auth_screen() -> None:
    st.title("面試回答管理 App")
    st.caption("請先登入，資料會依使用者分開儲存。")

    login_tab, register_tab = st.tabs(["登入", "建立帳號"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("帳號")
            password = st.text_input("密碼", type="password")
            submitted = st.form_submit_button("登入", use_container_width=True)

        if submitted:
            success, message = authenticate_user(username, password)
            if success:
                st.session_state.current_user = normalize_username(username)
                reset_app_state_for_login()
                st.rerun()
            else:
                st.error(message)

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("新帳號")
            new_password = st.text_input("新密碼", type="password")
            confirm_password = st.text_input("確認密碼", type="password")
            created = st.form_submit_button("建立帳號", use_container_width=True)

        if created:
            if new_password != confirm_password:
                st.error("兩次輸入的密碼不一致。")
            else:
                success, message = create_user(new_username, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)


st.set_page_config(page_title="面試回答管理 App", page_icon="🗂️", layout="wide")
st.markdown(
    """
    <style>
    .section-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stack-card {
        border: 1px solid #d6d9de;
        border-radius: 14px;
        padding: 18px 20px;
        background: #ffffff;
        margin-top: 14px;
    }
    .stack-card-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #5d6472;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .stack-card-question {
        font-size: 1.9rem;
        font-weight: 700;
        line-height: 1.45;
        color: #2f3441;
    }
    .stack-card-points {
        font-size: 1.02rem;
        line-height: 1.8;
        color: #2f3441;
        white-space: pre-wrap;
    }
    .answer-box {
        border: 1px solid #d6d9de;
        border-radius: 12px;
        padding: 20px 22px;
        background: #ffffff;
    }
    .answer-box p {
        font-size: 1.08rem;
        line-height: 1.85;
        margin: 0 0 0.8rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if not st.session_state.current_user:
    render_auth_screen()
    st.stop()

current_user = st.session_state.current_user
payload = load_user_payload(current_user)
categories = payload["categories"]
items = payload["items"]

if "selected_item_id" not in st.session_state:
    st.session_state.selected_item_id = items[0]["id"] if items else None
if "show_points" not in st.session_state:
    st.session_state.show_points = True
if "show_answer" not in st.session_state:
    st.session_state.show_answer = True
if "category_edit_target" not in st.session_state:
    st.session_state.category_edit_target = None
if "category_message" not in st.session_state:
    st.session_state.category_message = None

if st.session_state.selected_item_id is None and items:
    st.session_state.selected_item_id = items[0]["id"]

if st.session_state.selected_item_id and not get_item_by_id(items, st.session_state.selected_item_id):
    st.session_state.selected_item_id = items[0]["id"] if items else None

selected_item = get_item_by_id(items, st.session_state.selected_item_id)

st.title("面試回答管理 App")
st.caption(f"目前登入帳號：{current_user}")

with st.sidebar:
    st.write(f"登入中：`{current_user}`")
    if st.button("登出", use_container_width=True):
        st.session_state.current_user = None
        reset_app_state_for_login()
        st.rerun()

    interview_mode_clicked = st.button("面試模式", use_container_width=True)
    if interview_mode_clicked:
        if items:
            random_item = pick_random_item(items, st.session_state.selected_item_id)
            if random_item:
                st.session_state.selected_item_id = random_item["id"]
                st.rerun()
            else:
                st.warning("目前至少需要兩題，才能切換到不同題目。")
        else:
            st.warning("目前還沒有題目可以抽。")

    st.header("題目目錄")

    if st.session_state.category_message:
        message_type, message_text = st.session_state.category_message
        if message_type == "success":
            st.success(message_text)
        else:
            st.warning(message_text)
        st.session_state.category_message = None

    for category in categories:
        category_items = [item for item in items if item["category"] == category]
        name_col, random_col, edit_col, delete_col = st.columns([4, 1.2, 1.2, 1.2])
        with name_col:
            st.markdown(f"**{category}**")
        with random_col:
            category_mode_clicked = st.button(
                "抽題",
                key=f"category_random_{category}",
                use_container_width=True,
                disabled=len(category_items) < 2,
            )
            if category_mode_clicked:
                random_item = pick_random_item(category_items, st.session_state.selected_item_id)
                if random_item:
                    st.session_state.selected_item_id = random_item["id"]
                    st.rerun()
        with edit_col:
            if st.button("編輯", key=f"category_edit_{category}", use_container_width=True):
                st.session_state.category_edit_target = category
                st.rerun()
        with delete_col:
            if st.button("刪除", key=f"category_delete_{category}", use_container_width=True):
                if category_items:
                    st.session_state.category_message = ("warning", f"分類「{category}」內還有卡片，不能刪除。")
                else:
                    updated_categories = [item for item in categories if item != category]
                    save_user_payload(current_user, updated_categories, items)
                    if st.session_state.category_edit_target == category:
                        st.session_state.category_edit_target = None
                    st.session_state.category_message = ("success", f"分類「{category}」已刪除。")
                st.rerun()

        if st.session_state.category_edit_target == category:
            with st.form(f"rename_category_{category}"):
                renamed_category = st.text_input("新的分類名稱", value=category)
                rename_submitted = st.form_submit_button("更新分類", use_container_width=True)
            if rename_submitted:
                cleaned_name = renamed_category.strip()
                if not cleaned_name:
                    st.session_state.category_message = ("warning", "分類名稱不能空白。")
                elif cleaned_name != category and cleaned_name in categories:
                    st.session_state.category_message = ("warning", "這個分類名稱已經存在。")
                else:
                    updated_categories = [cleaned_name if item == category else item for item in categories]
                    for item in items:
                        if item["category"] == category:
                            item["category"] = cleaned_name
                    items = compact_category_orders(items, updated_categories)
                    save_user_payload(current_user, updated_categories, items)
                    st.session_state.category_edit_target = None
                    st.session_state.category_message = ("success", f"分類已更新為「{cleaned_name}」。")
                st.rerun()

        if category_items:
            for index, item in enumerate(category_items):
                title_col, up_col, down_col = st.columns([6, 1, 1])
                with title_col:
                    button_type = "primary" if item["id"] == st.session_state.selected_item_id else "secondary"
                    st.button(
                        item["question"] or "未命名題目",
                        key=f"sidebar_item_{item['id']}",
                        on_click=set_selected_item,
                        args=(item["id"],),
                        use_container_width=True,
                        type=button_type,
                    )
                with up_col:
                    move_up = st.button(
                        "↑",
                        key=f"move_up_{item['id']}",
                        disabled=index == 0,
                        use_container_width=True,
                    )
                with down_col:
                    move_down = st.button(
                        "↓",
                        key=f"move_down_{item['id']}",
                        disabled=index == len(category_items) - 1,
                        use_container_width=True,
                    )

                if move_up:
                    items = reorder_category_items(items, categories, category, item["id"], -1)
                    save_user_payload(current_user, categories, items)
                    st.session_state.selected_item_id = item["id"]
                    st.rerun()

                if move_down:
                    items = reorder_category_items(items, categories, category, item["id"], 1)
                    save_user_payload(current_user, categories, items)
                    st.session_state.selected_item_id = item["id"]
                    st.rerun()
        else:
            st.caption("目前沒有題目")


st.markdown('<div class="section-title">題目小卡</div>', unsafe_allow_html=True)
if not selected_item:
    st.info("請先在左側選擇題目，或在下方新增一筆資料。")
else:
    toggle_col1, toggle_col2 = st.columns(2)
    with toggle_col1:
        st.checkbox("顯示 Point", key="show_points")
    with toggle_col2:
        st.checkbox("顯示答案", key="show_answer")

    st.caption(f"分類：{selected_item['category']}")
    question_text = selected_item["question"] or "尚未填寫"
    points_text = selected_item["points"] or "尚未填寫"
    answer_text = selected_item["answer"] or "尚未填寫"
    answer_html = "<p>" + answer_text.replace("\n", "</p><p>") + "</p>"

    st.markdown(
        f"""
        <div class="stack-card">
            <div class="stack-card-label">題目</div>
            <div class="stack-card-question">{question_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.show_points:
        st.markdown(
            f"""
            <div class="stack-card">
                <div class="stack-card-label">回答 Point</div>
                <div class="stack-card-points">{points_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.show_answer:
        st.markdown(
            f"""
            <div class="stack-card">
                <div class="stack-card-label">回答答案</div>
                <div class="answer-box">{answer_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("編輯這張小卡", expanded=False):
        with st.form("edit_form"):
            edit_category = st.selectbox(
                "分類",
                categories,
                index=categories.index(selected_item["category"]),
            )
            edit_question = st.text_input(
                "日文面試題目 question",
                value=selected_item["question"],
            )
            edit_points = st.text_area(
                "回答 point points",
                value=selected_item["points"],
                height=120,
            )
            edit_answer = st.text_area(
                "正式回答 answer",
                value=selected_item["answer"],
                height=160,
            )

            col1, col2 = st.columns(2)
            with col1:
                update_submitted = st.form_submit_button("更新資料", use_container_width=True)
            with col2:
                delete_submitted = st.form_submit_button("刪除資料", use_container_width=True)

        if update_submitted:
            if not edit_question.strip():
                st.warning("題目不能空白。")
            else:
                for item in items:
                    if item["id"] == selected_item["id"]:
                        old_category = item["category"]
                        item["category"] = edit_category
                        if old_category != edit_category:
                            item["order"] = len(
                                [row for row in items if row["category"] == edit_category and row["id"] != item["id"]]
                            )
                        item["question"] = edit_question.strip()
                        item["points"] = edit_points.strip()
                        item["answer"] = edit_answer.strip()
                        break
                items = compact_category_orders(items, categories)
                save_user_payload(current_user, categories, items)
                st.success("資料已更新。")
                st.rerun()

        if delete_submitted:
            remaining_items = [item for item in items if item["id"] != selected_item["id"]]
            remaining_items = compact_category_orders(remaining_items, categories)
            save_user_payload(current_user, categories, remaining_items)
            st.session_state.selected_item_id = remaining_items[0]["id"] if remaining_items else None
            st.success("資料已刪除。")
            st.rerun()


with st.expander("新增一筆面試準備資料", expanded=False):
    with st.form("create_form", clear_on_submit=True):
        st.caption("可直接選擇現有分類，或輸入新的分類名稱。若有輸入新的分類名稱，系統會優先使用新分類。")
        selected_create_category = st.selectbox("現有分類", categories)
        new_category_name = st.text_input("新的分類名稱（可選）")

        new_question = st.text_input("日文面試題目 question")
        new_points = st.text_area("回答 point points", height=120)
        new_answer = st.text_area("正式回答 answer", height=160)
        create_submitted = st.form_submit_button("新增資料", use_container_width=True)

    if create_submitted:
        working_categories = categories
        target_category = selected_create_category

        if new_category_name.strip():
            working_categories, category_error = add_category(categories, new_category_name)
            if category_error:
                st.warning(category_error)
                st.stop()
            target_category = new_category_name.strip()

        if not new_question.strip():
            st.warning("請先輸入日文面試題目。")
        else:
            new_item = {
                "id": str(uuid4()),
                "category": target_category,
                "order": len([item for item in items if item["category"] == target_category]),
                "question": new_question.strip(),
                "points": new_points.strip(),
                "answer": new_answer.strip(),
            }
            items.append(new_item)
            items = compact_category_orders(items, working_categories)
            save_user_payload(current_user, working_categories, items)
            st.session_state.selected_item_id = new_item["id"]
            st.success("資料已新增。")
            st.rerun()
