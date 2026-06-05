import httpx
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="FastAPI Community",
    page_icon="📝",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1120px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }
    .app-kicker {
        color: #0f766e;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .app-title {
        margin: 0.35rem 0 0.25rem;
        font-size: 2.35rem;
        font-weight: 760;
    }
    .app-description {
        color: #64748b;
        margin-bottom: 0.35rem;
    }
    .app-meta {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-bottom: 1.7rem;
    }
    .section-label {
        color: #0f766e;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        background: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def request_json(method: str, path: str, timeout: float = 10.0, **kwargs):
    try:
        response = httpx.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=timeout,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as error:
        detail = error.response.json().get("detail", "요청 처리에 실패했습니다.")
        st.error(detail)
    except httpx.RequestError:
        st.error("FastAPI 서버에 연결할 수 없습니다. 백엔드 서버를 먼저 실행해주세요.")

    return None


def stream_summary(post_id: int):
    try:
        with httpx.stream(
            "POST",
            f"{API_BASE_URL}/posts/{post_id}/summary/stream",
            timeout=90.0,
        ) as response:
            response.raise_for_status()

            for chunk in response.iter_text():
                if chunk:
                    yield chunk
    except httpx.HTTPStatusError as error:
        detail = error.response.json().get("detail", "요약 생성에 실패했습니다.")
        yield f"\n\n요약 생성 실패: {detail}"
    except httpx.RequestError:
        yield "\n\nFastAPI 서버에 연결할 수 없습니다."


def render_edit_form(post: dict):
    st.divider()
    st.markdown('<p class="section-label">Edit post</p>', unsafe_allow_html=True)
    st.markdown("#### 게시글 수정")

    with st.form(f"edit_post_form_{post['id']}"):
        title = st.text_input("제목", value=post["title"])
        content = st.text_area("내용", value=post["content"], height=180)
        save_column, cancel_column = st.columns(2)
        save = save_column.form_submit_button(
            "수정 내용 저장",
            type="primary",
            use_container_width=True,
        )
        cancel = cancel_column.form_submit_button(
            "취소",
            use_container_width=True,
        )

    if cancel:
        st.session_state.editing_post_id = None
        st.rerun()

    if save:
        if not title.strip() or not content.strip():
            st.warning("제목과 내용을 모두 입력해주세요.")
        else:
            with st.spinner("게시글과 AI 요약을 업데이트하고 있습니다..."):
                updated_post = request_json(
                    "PUT",
                    f"/posts/{post['id']}",
                    timeout=90.0,
                    json={"title": title, "content": content},
                )

            if updated_post:
                st.session_state.editing_post_id = None
                st.success("게시글이 수정되었습니다.")
                st.rerun()


def render_delete_confirmation(post: dict):
    st.divider()
    st.warning(
        "정말 이 게시글을 삭제하시겠어요? 삭제한 게시글은 복구할 수 없습니다."
    )
    confirmed = st.checkbox(
        "삭제할 게시글을 다시 확인했습니다.",
        key=f"delete_confirmation_{post['id']}",
    )
    delete_column, cancel_column = st.columns(2)

    if delete_column.button(
        "게시글 영구 삭제",
        disabled=not confirmed,
        use_container_width=True,
    ):
        deleted_post = request_json("DELETE", f"/posts/{post['id']}")

        if deleted_post:
            st.session_state.deleting_post_id = None
            st.session_state.editing_post_id = None
            st.success("게시글이 삭제되었습니다.")
            st.rerun()

    if cancel_column.button(
        "삭제 취소",
        use_container_width=True,
    ):
        st.session_state.deleting_post_id = None
        st.rerun()


def render_post_detail(post: dict):
    st.markdown('<p class="section-label">Selected post</p>', unsafe_allow_html=True)
    st.subheader(post["title"])
    st.caption(f"게시글 #{post['id']} · 마지막 업데이트 {post['postDate']}")
    st.write(post["content"])

    st.divider()
    st.markdown('<p class="section-label">AI summary</p>', unsafe_allow_html=True)
    st.markdown("#### 저장된 AI 요약")

    if post["summary"]:
        st.write(post["summary"])
    else:
        st.caption("아직 저장된 요약문이 없습니다.")

    if st.button(
        "스트리밍으로 새 요약 생성",
        type="primary",
        use_container_width=True,
    ):
        st.markdown("##### 실시간 생성 결과")
        st.write_stream(stream_summary(post["id"]))

    st.divider()
    st.markdown('<p class="section-label">Manage post</p>', unsafe_allow_html=True)
    edit_column, delete_column = st.columns(2)

    if edit_column.button("게시글 수정", use_container_width=True):
        st.session_state.editing_post_id = post["id"]
        st.session_state.deleting_post_id = None
        st.rerun()

    if delete_column.button("게시글 삭제", use_container_width=True):
        st.session_state.deleting_post_id = post["id"]
        st.session_state.editing_post_id = None
        st.session_state[f"delete_confirmation_{post['id']}"] = False
        st.rerun()

    if st.session_state.get("editing_post_id") == post["id"]:
        render_edit_form(post)

    if st.session_state.get("deleting_post_id") == post["id"]:
        render_delete_confirmation(post)


st.markdown('<p class="app-kicker">KTB Weekly Challenge</p>', unsafe_allow_html=True)
st.markdown('<h1 class="app-title">FastAPI Community</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-description">게시글을 작성하고, AI 요약이 생성되는 과정을 실시간으로 확인해보세요.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="app-meta">FastAPI {API_BASE_URL} · Ollama gemma4:e2b</p>',
    unsafe_allow_html=True,
)

posts = request_json("GET", "/posts") or []

metric_columns = st.columns(3)
metric_columns[0].metric("전체 게시글", len(posts))
metric_columns[1].metric("요약 생성 완료", sum(bool(post["summary"]) for post in posts))
summary_rate = round(sum(bool(post["summary"]) for post in posts) / len(posts) * 100) if posts else 0
metric_columns[2].metric("요약 생성률", f"{summary_rate}%")

st.divider()

list_tab, create_tab = st.tabs(["게시글 살펴보기", "새 게시글 작성"])

with list_tab:
    if not posts:
        st.info("아직 작성된 게시글이 없습니다. 새 게시글을 먼저 작성해주세요.")
    else:
        post_options = {
            f"#{post['id']} · {post['title']}": post["id"]
            for post in posts
        }
        selected_label = st.selectbox("게시글 선택", post_options)
        selected_post_id = post_options[selected_label]

        if st.session_state.get("active_post_id") != selected_post_id:
            st.session_state.active_post_id = selected_post_id
            st.session_state.editing_post_id = None
            st.session_state.deleting_post_id = None

        selected_post = request_json("GET", f"/posts/{selected_post_id}")

        if selected_post:
            with st.container(border=True):
                render_post_detail(selected_post)

with create_tab:
    with st.form("create_post_form", clear_on_submit=True):
        title = st.text_input("제목", placeholder="게시글 제목을 입력하세요.")
        content = st.text_area(
            "내용",
            placeholder="공유하고 싶은 내용을 입력하세요.",
            height=220,
        )
        submitted = st.form_submit_button(
            "게시글 등록",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not title.strip() or not content.strip():
            st.warning("제목과 내용을 모두 입력해주세요.")
        else:
            created_post = request_json(
                "POST",
                "/posts",
                json={"title": title, "content": content},
            )

            if created_post:
                st.success("게시글이 등록되었습니다.")
                st.rerun()
