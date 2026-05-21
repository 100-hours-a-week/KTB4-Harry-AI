from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import httpx

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"  # OLLAMA 서버 URL
OLLAMA_MODEL = "gemma4:e2b"  # 사용할 OLLAMA 모델 이름

# RDBMS 사용 전 인메모리 저장소
posts_db = []


# 게시글 생성 요청 모델
class PostBase(BaseModel):
    title: str
    content: str
    
    # 서버가 만들어야 하는 값이다.
    # postDate: str = datetime.now().strftime("%Y-%m-%d %H:%M")

# 게시글 응답 모델
# class SummaryRequest(PostBase):
#     pass


# AI 요약 응답 모델
class SummaryResponse(BaseModel):
    summary: str = ""  # AI 요약 결과를 저장해야하는 필드


# 메인 페이지 확인 - 서버 초기 구동 확인용
@app.get("/")
def read_root():
    return {"message": "커뮤니티 게시판 API 메인 페이지."}


# 게시글 생성
# 메세지 dict로 생성된거 알려야 하는가 ?
@app.post("/posts")
def create_post(post: PostBase) -> dict:
    new_post = {
        "title": post.title,
        "content": post.content,
        # postDate는 서버에서 생성해야 하는 값이므로, PostBase 모델에서 제거하고 여기서 생성
        "postDate": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    posts_db.append(new_post)

    return {"message": "게시물이 성공적으로 등록되었습니다.", "post": new_post}


# 게시글 목록 조회 - 상세 조회보다 위에 두기(경로 설정)
@app.get("/posts")
def read_post_list() -> list:
    return posts_db


# 게시글 하나 조회
@app.get("/posts/{post_id}") 
def read_post(post_id: int) -> dict:
    return posts_db[post_id]


# 게시글 수정
# 메세지 dict로 수정된거 알려야 하는가 ?
@app.put("/posts/{post_id}") 
def update_post(post_id: int, updated_post: PostBase):
    posts_db[post_id] = {
        "title": updated_post.title,
        "content": updated_post.content,
        # postDate는 서버에서 생성해야 하는 값이므로, PostBase 모델에서 제거하고 여기서 생성
        "postDate": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    return {"message": "게시글이 성공적으로 수정되었습니다.", "post": posts_db[post_id]}


# 게시글 삭제
# 메세지 dict로 삭제된거 알려야 하는가 ?
@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    del posts_db[post_id]
    return {"message": "게시물이 성공적으로 삭제되었습니다."}


# ------------ AI 요약 기능 연결 ------------


# AI 요약 생성 요청 및 요약문 반환 - 게시글 상세 조회보다 아래에 두기(경로 설정)
@app.post("/posts/{post_id}/summary", response_model=SummaryResponse)
async def generate_summary(post_id: int):
    post = posts_db[post_id]
    # request_ai_summary에서 비동기 http 요청을 보내므로 await 키워드 사용
    summary = await request_ai_summary(post["title"], post["content"])
    post["summary"] = summary  # 게시글 데이터에 요약 결과 저장

    # summary[:100] 슬라이싱 나중에 
    return {"summary": summary}

'''
서버 내부에서 LLM 요청만 담당하는 helper 함수

httpx 비동기 HTTP 클라이언트 라이브러리를 사용해서
실제 LLM API에 요청을 보내는 형태로 구현
'''
async def request_ai_summary(title: str, content: str) -> str:
    # """ 안 들여쓰기 너무 많아서 깔끔하게 정리하는게 좋다는 피드백 ?
    prompt = f"""
                "다음 게시글을 2~3문장으로 요약해줘.\n\n"
                f"제목: {title}\n\n"
                f"내용:\n{content}"
            """
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                # system - 모델의 전체 역할, 태도, 규칙을 정함
                "role": "system",
                "content": "너는 커뮤니티 게시글을 간결하게 요약하는 한국어 AI 도우미야. 답변은 최대한 간결하게 해.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        # 스트리밍
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()  # 요청 실패 시 예외 발생

        result = response.json()
        return result["choices"][0]["message"]["content"]


# AI 요약 조회 - 게시글 상세 조회보다 아래에 두기(경로 설정)
@app.get("/posts/{post_id}/summary", response_model=SummaryResponse)
async def summarize_post(post_id: int):

    # 요약 미생성 후 조회시 임시 방어 코드 
    if "summary" not in posts_db[post_id]:
        return {"summary": "아직 생성된 요약문이 없습니다."}
    
    return {"summary": f"게시글의 요약된 내용: {posts_db[post_id]['summary'][:200]}"}


