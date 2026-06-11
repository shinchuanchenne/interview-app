import json
import random
from pathlib import Path
from uuid import uuid4

import streamlit as st


DATA_FILE = Path("data.json")
CATEGORIES = ["經歷", "前職", "人柄", "專案", "志望動機"]
DEFAULT_CATEGORY = CATEGORIES[0]


def ensure_data_file() -> None:
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def normalize_item(item: dict, default_order: int) -> dict:
    category = item.get("category", DEFAULT_CATEGORY)
    if category not in CATEGORIES:
        category = DEFAULT_CATEGORY

    return {
        "id": item.get("id", str(uuid4())),
        "category": category,
        "order": int(item.get("order", default_order)),
        "question": item.get("question", "").strip(),
        "points": item.get("points", "").strip(),
        "answer": item.get("answer", "").strip(),
    }


def load_items() -> list[dict]:
    ensure_data_file()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            normalized_items = [
                normalize_item(item, default_order=index)
                for index, item in enumerate(data)
                if isinstance(item, dict)
            ]
            normalized_items = sort_items(normalized_items)
            if normalized_items != data:
                save_items(normalized_items)
            return normalized_items
    except json.JSONDecodeError:
        pass

    save_items([])
    return []


def save_items(items: list[dict]) -> None:
    DATA_FILE.write_text(
        json.dumps(sort_items(items), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_item_by_id(items: list[dict], item_id: str | None) -> dict | None:
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def set_selected_item(item_id: str) -> None:
    st.session_state.selected_item_id = item_id


def sort_items(items: list[dict]) -> list[dict]:
    category_index = {category: index for index, category in enumerate(CATEGORIES)}
    return sorted(
        items,
        key=lambda item: (category_index.get(item["category"], len(CATEGORIES)), item.get("order", 0)),
    )


def reorder_category_items(items: list[dict], category: str, item_id: str, direction: int) -> list[dict]:
    sorted_items = sort_items(items)
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

    order_map = {}
    for index, item in enumerate(category_items):
        order_map[item["id"]] = index

    for item in sorted_items:
        if item["category"] == category and item["id"] in order_map:
            item["order"] = order_map[item["id"]]

    return sort_items(sorted_items)


def compact_category_orders(items: list[dict]) -> list[dict]:
    sorted_items = sort_items(items)
    for category in CATEGORIES:
        category_items = [item for item in sorted_items if item["category"] == category]
        for index, item in enumerate(category_items):
            item["order"] = index
    return sort_items(sorted_items)


def pick_random_item(pool: list[dict], current_item_id: str | None) -> dict | None:
    if not pool:
        return None

    candidates = [item for item in pool if item["id"] != current_item_id]
    if not candidates:
        return None

    return random.choice(candidates)


st.set_page_config(page_title="面試回答管理 App", page_icon="🗂️", layout="wide")
st.title("面試回答管理 App")
st.caption("左側像目錄一樣管理題目，右側查看與編輯內容。")
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

items = load_items()

if "selected_item_id" not in st.session_state:
    st.session_state.selected_item_id = items[0]["id"] if items else None

if "show_points" not in st.session_state:
    st.session_state.show_points = True

if "show_answer" not in st.session_state:
    st.session_state.show_answer = True

if st.session_state.selected_item_id and not get_item_by_id(items, st.session_state.selected_item_id):
    st.session_state.selected_item_id = items[0]["id"] if items else None

selected_item = get_item_by_id(items, st.session_state.selected_item_id)


with st.sidebar:
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
    for category in CATEGORIES:
        category_items = [item for item in items if item["category"] == category]
        header_col, action_col = st.columns([4, 2])
        with header_col:
            st.markdown(f"**{category}**")
        with action_col:
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
                    items = reorder_category_items(items, category, item["id"], -1)
                    save_items(items)
                    st.session_state.selected_item_id = item["id"]
                    st.rerun()

                if move_down:
                    items = reorder_category_items(items, category, item["id"], 1)
                    save_items(items)
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
                CATEGORIES,
                index=CATEGORIES.index(selected_item["category"]),
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
                            item["order"] = len([row for row in items if row["category"] == edit_category and row["id"] != item["id"]])
                        item["question"] = edit_question.strip()
                        item["points"] = edit_points.strip()
                        item["answer"] = edit_answer.strip()
                        break
                items = compact_category_orders(items)
                save_items(items)
                st.success("資料已更新。")
                st.rerun()

        if delete_submitted:
            remaining_items = [item for item in items if item["id"] != selected_item["id"]]
            remaining_items = compact_category_orders(remaining_items)
            save_items(remaining_items)

            st.session_state.selected_item_id = remaining_items[0]["id"] if remaining_items else None
            st.success("資料已刪除。")
            st.rerun()


with st.expander("新增一筆面試準備資料", expanded=False):
    with st.form("create_form", clear_on_submit=True):
        new_category = st.selectbox("分類", CATEGORIES)
        new_question = st.text_input("日文面試題目 question")
        new_points = st.text_area("回答 point points", height=120)
        new_answer = st.text_area("正式回答 answer", height=160)
        create_submitted = st.form_submit_button("新增資料", use_container_width=True)

    if create_submitted:
        if not new_question.strip():
            st.warning("請先輸入日文面試題目。")
        else:
            new_item = {
                "id": str(uuid4()),
                "category": new_category,
                "order": len([item for item in items if item["category"] == new_category]),
                "question": new_question.strip(),
                "points": new_points.strip(),
                "answer": new_answer.strip(),
            }
            items.append(new_item)
            items = compact_category_orders(items)
            save_items(items)
            st.session_state.selected_item_id = new_item["id"]
            st.success("資料已新增。")
            st.rerun()
