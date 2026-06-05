# 📝 FastAPI Community

FastAPI로 구현한 커뮤니티 게시글 API 학습 프로젝트입니다.

---

## 소개

이 프로젝트는 카카오테크 부트캠프 2주차 과제인 **FastAPI 커뮤니티 서비스 백엔드 구현**을 위해 진행했습니다.

게시글 CRUD API를 시작으로 Ollama 기반 AI 요약 기능, SQLAlchemy 데이터베이스 연동, 예외 처리, 계층형 구조 분리를 단계적으로 적용했습니다.

단순히 기능을 한 번에 완성하기보다, `CRUD → AI 요약 → 데이터베이스 → 구조 개선` 순서로 기능을 확장하며 FastAPI 백엔드의 기본 구성 요소를 학습하는 데 초점을 두었습니다.

---

## 주요 기능

- 게시글 생성, 목록 조회, 상세 조회, 수정, 삭제
- 게시글 제목과 본문 기반 AI 요약 생성
- 생성된 AI 요약문 조회
- SQLite + SQLAlchemy 기반 게시글 저장
- `HTTPException` 기반 예외 응답 처리
- 역할별 디렉토리 구조 분리

---

## 사용 기술

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- SQLite
- httpx
- Ollama
- Streamlit
- uv

---

## 디렉토리 구조

```text
week02-fastapi-community/
├── main.py
├── core/
│   └── config.py
├── database/
│   ├── base.py
│   └── session.py
├── models/
│   └── post.py
├── schemas/
│   └── post.py
├── api/
│   └── routes/
│       └── posts.py
├── services/
│   └── ai_summary_service.py
├── streamlit_app.py
├── README.md
├── pyproject.toml
├── uv.lock
└── .python-version
```

---

## 실행 방법

의존성 설치:

```bash
uv sync
```

FastAPI 서버 실행:

```bash
uv run uvicorn main:app --reload --port 8001
```

새 터미널에서 Streamlit 실행:

```bash
uv run streamlit run streamlit_app.py
```

API 문서 접속:

```text
http://127.0.0.1:8001/docs
```

Streamlit 화면 접속:

```text
http://localhost:8501
```

AI 요약 기능을 사용하려면 로컬에서 Ollama 서버와 사용할 모델이 준비되어 있어야 합니다.

```bash
ollama pull gemma4:e2b
```

---

## API 요약

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/` | 서버 상태 확인 |
| POST | `/posts` | 게시글 생성 |
| GET | `/posts` | 게시글 목록 조회 |
| GET | `/posts/{post_id}` | 게시글 상세 조회 |
| PUT | `/posts/{post_id}` | 게시글 수정 |
| DELETE | `/posts/{post_id}` | 게시글 삭제 |
| POST | `/posts/{post_id}/summary` | AI 요약 생성 |
| GET | `/posts/{post_id}/summary` | AI 요약 조회 |
| POST | `/posts/{post_id}/summary/stream` | AI 요약 스트리밍 생성 |

---

## 구현 흐름

```text
1. FastAPI 기본 앱 생성
2. 게시글 CRUD API 구현
3. Ollama 기반 AI 요약 기능 연결
4. SQLite + SQLAlchemy 데이터베이스 적용
5. HTTPException 기반 예외 처리
6. 역할별 디렉토리 구조 분리
7. AI 요약 스트리밍 응답 구현
8. Streamlit 기반 프론트엔드 화면 구현
```

---

## 개선 방향

- 댓글, 좋아요 기능 추가
- 사용자 로그인 및 인증 기능 추가
- 스트리밍으로 생성한 AI 요약문 DB 저장
- 요청/응답 스키마 세분화
- 테스트 코드 추가
- 프론트엔드 화면 구현

---

## 회고 및 학습 기록

이번 과제를 하면서 가장 많이 든 생각은  
“AI의 도움을 받아 만든 코드도 내가 이해하고 설명할 수 있다면 내 학습이 될 수 있을까?”였다.

특히 LLM 요청 로직과 프로젝트 구조 분리는 처음부터 혼자 힘으로 깔끔하게 풀어내기 어려웠다.  
그래서 단순히 정답 코드를 가져오기보다, 세부 과제를 달성하기 위해 어떤 사고로 접근해야 하는지, 작업 단위를 어떤 순서로 쪼개야 하는지 계속 로드맵을 세우며 진행했다.

처음에는 `main.py` 하나에 기능을 쌓아가며 FastAPI의 흐름을 익혔고, 이후 AI 요약, 데이터베이스, 예외 처리, 구조 분리를 하나씩 붙여가며 백엔드 코드가 어떻게 커지고 정리되는지 경험했다.

아래 기록은 결과물만 남기기보다, 그 과정에서 내가 어떤 고민을 했고 무엇을 배웠는지 남기기 위한 기록이다.

<details>
<summary>[2-1] 게시글 CRUD API 구현</summary>

## 1. 진행 상황

1. FastAPI 앱 생성 ✅
2. Pydantic 모델 작성 ✅
3. 인메모리 데이터 저장소 구성 ✅
4. CREATE 구현 ✅
5. READ 구현 ✅
6. UPDATE 구현 ✅
7. DELETE 구현 ✅

---

## 2. 구현 순서 설계

CRUD API를 작성할 때 어떤 기능을 먼저 구현할지 고민했다.

처음에는 `POST`와 `GET` 중 어떤 것을 더 위에 두는 것이 자연스러운지 생각했다.

결론적으로는 데이터의 생명주기를 기준으로 구현 순서를 잡는 것이 이해하기 쉽다고 판단했다.

1. CREATE: 게시글 생성
2. READ: 게시글 조회
3. UPDATE: 게시글 수정
4. DELETE: 게시글 삭제

데이터가 먼저 존재해야 조회할 수 있기 때문에, 생성 기능을 먼저 구현하는 흐름이 자연스럽다고 느꼈다.

---

## 3. 데이터 저장 방식

초기 구현에서는 데이터베이스를 사용하지 않고 인메모리 방식으로 게시글 데이터를 저장했다.

```python
posts_db = []
```

함수 내부에서 데이터를 관리하면 함수 실행이 끝난 뒤 데이터가 유지되지 않는다.  
따라서 여러 API 함수에서 같은 데이터를 사용할 수 있도록 전역 리스트를 사용했다.

### 리스트와 딕셔너리 중 리스트를 선택한 이유

초기 단계에서는 게시글이 생성된 순서대로 저장되는 흐름을 확인하고 싶었다.

- 리스트
  - 게시글 생성 순서를 유지하기 좋다.
  - 전체 목록 조회 흐름을 이해하기 쉽다.

- 딕셔너리
  - `id` 기반 조회, 수정, 삭제에 유리하다.
  - 데이터가 많아질수록 특정 게시글을 찾기 쉽다.

초기 학습 단계에서는 흐름을 눈으로 확인하기 쉬운 리스트를 먼저 사용했다.

---

## 4. 요청 데이터와 서버 데이터 구분

API를 설계할 때 사용자가 보내는 값과 서버가 만들어야 하는 값을 구분해야 한다는 점을 배웠다.

### 사용자가 보내는 값

- title
- content

### 서버가 생성하거나 관리하는 값

- id
- postdate
- likes
- summary

즉, 게시글 생성 요청에서 사용자가 모든 값을 보내는 것이 아니라, 서버가 책임져야 하는 값은 서버 내부에서 생성해야 한다.

이 관점에서 요청 모델과 응답 모델을 분리하는 것이 더 자연스럽다.

---

## 5. `def`와 `async def` 선택 기준

FastAPI에서는 일반 함수인 `def`와 비동기 함수인 `async def`를 모두 사용할 수 있다.

이번 CRUD 구현은 대부분 순수 파이썬 연산으로 이루어져 있다.

- 메모리 리스트에 데이터 추가
- 리스트에서 데이터 조회
- 리스트의 특정 값 수정
- 리스트에서 데이터 삭제

외부 API 호출, 파일 입출력, 데이터베이스 요청처럼 기다려야 하는 작업이 없기 때문에 처음에는 `def`를 사용하는 것이 더 단순하고 자연스럽다고 판단했다.

`async def`는 기다리는 작업이 있을 때 이벤트 루프를 통해 효율적으로 처리할 수 있다는 장점이 있다.  
하지만 기다릴 작업이 없는 단순 연산에서는 굳이 사용할 필요가 없다고 이해했다.

---

## 6. 조회 API 설계

조회 기능은 두 가지로 분리하는 것이 좋다고 판단했다.

1. 게시글 목록 조회
2. 게시글 상세 조회

목록 조회와 상세 조회는 목적이 다르다.

- 목록 조회는 여러 게시글의 요약된 정보를 보여주는 역할
- 상세 조회는 특정 게시글의 전체 내용을 보여주는 역할

따라서 하나의 조회 기능으로 합치기보다 분리하는 편이 API 역할을 더 명확하게 만든다.

---

## 7. 새로 배운 점

- 클래스 이름은 명사 + 파스칼 케이스를 사용한다.
  - 예: `PostCreate`, `PostResponse`

- 함수 이름은 동사 + 스네이크 케이스를 사용한다.
  - 예: `create_post`, `get_post`

- 사용자가 보내는 값과 서버가 생성하는 값을 구분해야 한다.

- API 구현 순서는 데이터의 생명주기를 기준으로 생각하면 이해하기 쉽다.

</details>


<details>
<summary>[2-2] AI 모델 서빙 기능 구현</summary>

## 1. 진행 상황

1. LLM 기능 요구사항 정의 ✅
2. AI 요청/응답 모델 작성 ✅
3. Mock AI 응답 함수 작성 ✅
4. AI 엔드포인트 설계 ✅
5. AI 엔드포인트 구현 ✅
6. 기존 게시글 API와 연결 ✅
7. 실제 LLM API 연동 ✅
8. 에러 처리 및 응답 구조 정리 ✅

---

## 2. 기능 목표 정의

AI 기능을 붙이기 전에, 먼저 어떤 데이터를 LLM에 넘기고 어떤 결과를 받을지 정리했다.

처음 고민한 기능은 다음과 같다.

- 게시글 본문 요약
- 게시글 제목 추천
- 게시글 기반 댓글 또는 피드백 생성

이 중 제목 추천은 우선 제외했다.  
게시글 제목은 이미 사용자가 입력하는 값이기 때문이다.

따라서 우선 구현할 AI 기능은 게시글 요약으로 정했다.

### AI 요약 기능의 목적

게시글 내용이 길 경우, 다른 사용자가 전체 내용을 읽기 전에 빠르게 핵심을 파악할 수 있도록 돕는 것이다.

---

## 3. 요청/응답 데이터 설계

요약 품질을 높이기 위해 게시글 본문뿐 아니라 제목도 함께 LLM에 전달하기로 했다.

### 요청 데이터

- title
- content

### 응답 데이터

- summary

요청과 응답 구조를 명확히 하기 위해 Pydantic 모델을 사용한다.

---

## 4. 이름 작성 규칙

코드를 작성하면서 클래스와 함수 이름의 기준도 함께 정리했다.

- 클래스
  - 명사형
  - 파스칼 케이스
  - 예: `AISummaryRequest`, `AISummaryResponse`

- 함수
  - 동사형
  - 스네이크 케이스
  - 예: `request_ai_summary`, `generate_summary`

이름만 보아도 역할을 추측할 수 있도록 작성하는 것이 중요하다고 느꼈다.

---

## 5. Mock 함수로 먼저 구현한 이유

처음부터 실제 LLM API를 연결하면 고려해야 할 요소가 많다.

- 외부 API 호출
- 네트워크 지연
- 응답 실패
- 예외 처리
- API key 관리
- LLM 응답 형식 변경 가능성

따라서 먼저 Mock 함수로 AI 응답을 흉내 내면서 API 전체 흐름을 잡았다.

Mock 함수로 먼저 구현하면 FastAPI 엔드포인트, 요청 모델, 응답 모델, 기존 게시글 데이터와의 연결 흐름을 먼저 확인할 수 있다.

---

## 6. 엔드포인트와 LLM 호출 로직 분리

AI 요약 기능을 구현하면서 엔드포인트 함수와 LLM 호출 함수를 분리했다.

두 함수는 책임이 다르기 때문이다.

### 엔드포인트 함수의 책임

- 클라이언트 요청 받기
- path parameter 또는 request body 처리
- 필요한 함수 호출
- 응답 반환

### LLM 호출 함수의 책임

- prompt 생성
- Ollama API 요청
- 응답 JSON 파싱
- summary 문자열 반환

이렇게 분리하면 나중에 LLM 제공자를 바꾸거나, Mock 함수를 실제 API 호출 함수로 교체할 때 수정 범위가 줄어든다.

---

## 7. Ollama 연결 흐름

Ollama와 연결하는 흐름은 다음과 같이 정리할 수 있다.

1. `title`과 `content`를 기반으로 prompt 생성
2. Ollama 로컬 API에 POST 요청
3. 응답 JSON에서 `response` 필드 추출
4. summary 문자열 반환

```text
Client
→ FastAPI
→ prompt 생성
→ Ollama API 요청
→ 응답 JSON 파싱
→ summary 반환
```

Ollama는 OpenAI API와 비슷한 형태의 호환 엔드포인트도 제공한다.

---

## 8. `httpx.AsyncClient`를 사용하는 이유

`httpx.AsyncClient`는 Python에서 비동기 HTTP 요청을 보낼 때 사용하는 라이브러리다.

외부 LLM API 호출은 응답을 기다리는 작업이다.  
따라서 FastAPI에서 비동기 방식으로 처리하면 서버가 기다리는 동안 다른 요청을 처리할 수 있다.

`requests`와 비슷한 문법을 제공하지만, `async/await` 기반으로 동작한다.

---

## 9. 요약 데이터 저장 위치 고민

AI 요약 결과를 별도의 `summary_db`에 저장할지 고민했다.

하지만 요약문은 게시글에 종속된 데이터라고 판단했다.

- 게시글이 있어야 요약문도 의미가 있다.
- 게시글이 삭제되면 요약문도 함께 사라지는 것이 자연스럽다.
- 요약문은 독립적인 데이터라기보다 게시글의 부가 정보에 가깝다.

따라서 별도의 `summary_db`를 만들기보다는 기존 `posts_db` 안에 `summary` 필드를 추가하는 방향이 더 적절하다고 판단했다.

---

## 10. 스트리밍 응답에 대한 고민

LLM 응답 방식에는 일반 응답과 스트리밍 응답이 있다.

### 일반 응답

LLM이 응답을 모두 생성한 뒤 한 번에 반환한다.

```json
{
  "stream": false
}
```

FastAPI에서는 `response.json()`으로 응답 전체를 한 번에 파싱할 수 있다.

### 스트리밍 응답

LLM이 생성 중인 토큰이나 문장을 조금씩 반환한다.

```json
{
  "stream": true
}
```

FastAPI에서는 `StreamingResponse`를 사용해 클라이언트에게 응답 조각을 전달할 수 있다.

### 스트리밍에서 고민되는 점

스트리밍으로 응답을 바로 보여줄 경우, 완성된 summary를 언제 저장할지 고민이 필요하다.

예상 흐름은 다음과 같다.

1. Ollama에서 응답 조각을 하나씩 받는다.
2. 받은 조각을 클라이언트에게 바로 전달한다.
3. 동시에 `summary_text`에 응답 조각을 누적한다.
4. 스트리밍이 끝나면 완성된 `summary_text`를 `posts_db[post_id]["summary"]`에 저장한다.

---

## 11. 새로 배운 점

### `response_model`

FastAPI의 `response_model`을 사용하면 API 응답 구조를 명확하게 제한할 수 있다.

응답으로 어떤 필드가 나가야 하는지 명확히 보여줄 수 있고, 불필요한 데이터가 응답에 포함되는 것을 막을 수 있다.

### Pydantic 모델 상속

공통 필드를 부모 모델에 정의하고, 필요한 모델에서 상속받아 사용할 수 있다.

```python
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass
```

`PostCreate`는 `PostBase`의 필드를 그대로 사용하고, 추가할 필드가 없기 때문에 `pass`를 사용한다.

### path parameter

URL 경로에 포함된 값은 함수 인자로 받아야 한다.

예를 들어 `/posts/{post_id}`와 같은 경로를 사용하면, 함수에서도 `post_id`를 인자로 받아야 한다.

### payload

payload는 API 요청이나 응답에서 주고받는 데이터 본문을 의미한다.

LLM API를 호출할 때는 prompt, model, stream 여부 등의 정보가 payload에 담긴다.

</details>


<details>
<summary>[2-3] 데이터베이스 적용</summary>

## 1. 진행 상황

1. 인메모리 저장 방식의 한계 정리 ✅
2. 사용할 데이터베이스 선택 ✅
3. 저장할 데이터 구조 설계 ✅
4. SQLAlchemy 의존성 추가 ✅
5. DB 연결 설정 작성 ✅
6. Post ORM 모델 작성 ✅
7. CREATE 로직 DB 저장 방식으로 변경 ✅
8. READ 로직 DB 조회 방식으로 변경 ✅
9. UPDATE / DELETE 로직 DB 기반으로 변경 ✅
10. AI 요약 결과 DB 저장 ✅
11. 서버 재시작 후 데이터 유지 확인 ✅

---

## 2. 인메모리 저장 방식의 한계

2-1과 2-2에서는 게시글 데이터를 전역 리스트에 저장했다.

```python
posts_db = []
```

이 방식은 CRUD 흐름을 빠르게 이해하기에는 좋았다.  
하지만 서버가 재시작되면 저장된 게시글과 AI 요약문이 모두 사라지는 한계가 있었다.

커뮤니티 서비스라면 게시글은 서버 실행 상태와 관계없이 유지되어야 한다.  
따라서 이번 단계에서는 인메모리 저장 방식에서 데이터베이스 저장 방식으로 전환했다.

---

## 3. 데이터베이스 선택

여러가지 데이터베이스 적용 방식으로 `sqlite3`, `SQLModel`, `MongoDB` 등의 선택지를 찾아볼 수 있었다.

처음에는 `sqlite3`와 `SQLAlchemy` 중 어떤 방식을 사용할지 고민했다. 중간에 `sqlite3`와 `sqlite`를 헷갈려서 찾아보기도 했었다. 😅 

### SQLite

- 파일 기반 데이터베이스
- 별도의 DB 서버 없이 사용할 수 있다.
- 학습용 프로젝트나 작은 규모의 서비스에서 시작하기 좋다.

### sqlite3

- Python 표준 라이브러리
- SQL을 직접 작성해 SQLite DB에 접근한다.
- SQL 동작을 직접 확인하기에는 직관적이다.

### SQLAlchemy

- Python ORM / DB toolkit
- 데이터베이스 테이블을 Python 클래스처럼 다룰 수 있다.
- 이후 `models.py`, `schemas.py`, `routes.py` 등으로 구조를 분리하기 좋다.

이번 프로젝트에서는 **SQLite + SQLAlchemy** 조합을 선택했다.

SQLite는 가볍게 시작할 수 있고, SQLAlchemy는 이후 구조 개선 단계에서 실무적인 코드 구조로 확장하기 좋다고 판단했기 때문이다.

---

## 4. ORM 모델 설계

SQLAlchemy를 사용하면서 게시글 테이블을 Python 클래스로 표현했다.

```python
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    post_date = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=True)
```

`Post` 클래스는 데이터베이스에 저장될 게시글의 구조를 의미한다.

### 저장하는 데이터

- `id`: 게시글 고유 번호
- `title`: 게시글 제목
- `content`: 게시글 내용
- `post_date`: 작성 또는 수정 시간
- `summary`: AI 요약 결과

AI 요약문을 별도 테이블로 분리할지도 고민했다.  
하지만 현재 단계에서는 요약문이 게시글에 종속된 부가 정보라고 판단했다.

게시글이 삭제되면 요약문도 함께 사라지는 것이 자연스럽기 때문에 `posts` 테이블의 `summary` 컬럼으로 함께 관리했다.

---

## 5. DB 연결 흐름

데이터베이스 연결을 위해 `engine`, `SessionLocal`, `Base`를 설정했다.

```python
engine = create_engine("sqlite:///./posts.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

`Base.metadata.create_all(bind=engine)`은 SQLAlchemy 모델로 정의한 클래스를 실제 SQLite 테이블로 생성하는 역할을 한다.

또한 FastAPI의 `Depends`를 사용해 API 함수에서 DB 세션을 주입받도록 구성했다.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

이 구조를 사용하면 각 요청마다 DB 세션을 열고, 요청 처리가 끝난 뒤 세션을 닫을 수 있다.

---

## 6. CRUD 로직 변경

기존에는 리스트에 직접 데이터를 추가하거나 조회했다.

DB 적용 후에는 SQLAlchemy 세션을 통해 데이터를 저장하고 조회하도록 변경했다.

### CREATE

- `Post` 객체 생성
- `db.add()`로 세션에 추가
- `db.commit()`으로 DB에 반영
- `db.refresh()`로 생성된 id 등 최신 값 반영

### READ

- `db.query(Post).all()`로 게시글 목록 조회
- `db.query(Post).filter(Post.id == post_id).first()`로 특정 게시글 조회

### UPDATE

- 기존 게시글 조회
- 제목, 내용, 수정 시간 변경
- 수정된 본문 기준으로 AI 요약문 재생성
- `db.commit()`으로 변경사항 저장

### DELETE

- 기존 게시글 조회
- `db.delete()`로 삭제
- `db.commit()`으로 반영

---

## 💡 7. 게시글 수정과 AI 요약문 갱신 고민

DB 연동 과정에서 게시글 수정 시 AI 요약문을 어떻게 처리할지 고민했다.

게시글의 `title`이나 `content`가 바뀌면 기존 `summary`는 더 이상 최신 본문을 기준으로 한 요약문이 아니다.

처음에는 수정 시 `summary = None`으로 초기화하고, 사용자가 별도로 요약 생성 API를 다시 호출하는 방식을 고민했다.

이 방식은 수정 API의 응답 속도를 빠르게 유지할 수 있지만, 사용자가 추가 동작을 해야 하고 게시글 내용과 요약문이 일시적으로 불일치할 수 있다.

따라서 현재 프로젝트에서는 게시글 수정 시 LLM을 다시 호출해 최신 본문 기준의 요약문도 함께 갱신하도록 설계했다.

다만 실제 서비스에서는 LLM 응답 지연이 발생할 수 있으므로, 백그라운드 작업이나 메시지 큐 기반의 비동기 처리도 고려할 수 있다는 점을 배웠다.

---

## 💡 8. 예외 처리 추가 관련

DB 연동 후에는 단순히 데이터를 저장하고 조회하는 것뿐 아니라, 실패 상황을 어떻게 응답할지도 고민해볼 수 있었다.

처음에는 게시글을 찾지 못했을 때 다음과 같이 메시지를 반환했다.

```python
return {"message": "게시글을 찾을 수 없습니다."}
```

하지만 이 방식은 실제로는 실패 상황인데도 HTTP 상태코드는 `200 OK`로 반환된다.  
따라서 게시글을 찾지 못한 경우에는 `HTTPException`을 사용해 `404 Not Found`를 반환하도록 변경했다.

```python
raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
```

### 게시글 목록 조회 예외 처리

게시글 목록 조회에서는 별도의 `404` 예외를 추가하지 않았다.

`db.query(Post).all()`은 게시글이 없어도 `None`이 아니라 빈 리스트 `[]`를 반환한다.  
따라서 게시글이 하나도 없는 상태는 실패가 아니라, 비어 있는 목록을 정상적으로 반환하는 상황이라고 판단했다.

### AI 요약 요청 예외 처리

AI 요약 요청은 `generate_summary()`와 `update_post()`에서 모두 사용된다.

처음에는 각 함수에서 `try-except`를 작성할 수도 있다고 생각했다.  
하지만 실제로 Ollama API를 호출하는 책임은 `request_ai_summary()` 함수에 있으므로, AI 요청 관련 예외도 해당 함수 안에서 처리하는 편이 더 자연스럽다고 피드백 받을 수 있었다.

이번 과정에서 강의 초반에는 익숙하지 않았던 `502`, `503`, `504` 상태 코드도 함께 정리했다.

- `502 Bad Gateway`: 외부 서버가 실패 응답을 반환했을 때
- `503 Service Unavailable`: 외부 서비스에 연결할 수 없을 때
- `504 Gateway Timeout`: 외부 서버 응답을 기다리다가 시간이 초과됐을 때

이번 프로젝트 기준으로는 FastAPI 서버가 Ollama 서버에 의존하고 있기 때문에, AI 요청 실패 상황을 위 상태 코드로 구분할 수 있었다.

---

## 9. 새로 배운 점

- 인메모리 저장 방식은 서버 재시작 시 데이터가 사라진다.
- SQLite는 데이터베이스 자체이고, sqlite3는 Python에서 SQLite를 직접 다루는 표준 라이브러리다.
- SQLAlchemy는 데이터베이스 테이블을 Python 객체처럼 다룰 수 있게 해주는 ORM 도구다.
- `from sqlalchemy`는 컬럼, 타입, 엔진 등 Core 영역의 도구를 가져올 때 사용한다.
- `from sqlalchemy.orm`은 세션, 모델 베이스 등 ORM 영역의 도구를 가져올 때 사용한다.
- `Depends(get_db)`를 사용하면 FastAPI 엔드포인트에서 DB 세션을 주입받을 수 있다.
- 로컬에서 생성되는 `posts.db`는 실행 결과물이므로 Git에 올리지 않고 `.gitignore`로 관리하는 것이 좋다.
- `HTTPException`을 사용하면 실패 상황에 맞는 HTTP 상태코드와 메시지를 함께 반환할 수 있다.
- 게시글 목록이 비어 있는 것은 예외가 아니라 정상 응답으로 볼 수 있다.
- 외부 AI 서버 호출 실패는 `502`, `503`, `504`처럼 상황에 맞는 상태 코드로 구분할 수 있다.
</details>


<details>
<summary>[2-4] 구조 개선</summary>

## 1. 진행 상황

1. 기존 `main.py` 역할 분석 ✅
2. 프로젝트 디렉토리 구조 설계 ✅
3. 설정값 분리 ✅
4. 데이터베이스 연결 코드 분리 ✅
5. SQLAlchemy 모델 분리 ✅
6. Pydantic 스키마 분리 ✅
7. AI 요약 서비스 로직 분리 ✅
8. 게시글 API 라우터 분리 ✅
9. `main.py`를 앱 조립 역할로 정리 ✅
10. 구조 분리 후 import 확인 ✅

---

## 2. 구조 개선 목표

2-1부터 2-3까지는 학습 흐름을 따라가기 위해 대부분의 코드를 `main.py`에 작성했다.

이 방식은 처음에는 전체 흐름을 한 파일에서 볼 수 있어 이해하기 쉽다.  
하지만 기능이 늘어나면서 `main.py` 안에 여러 책임이 섞이기 시작했다.

기존 `main.py`에서 분리 해야하는 책임을 따져봤을 때,

- FastAPI 앱 생성
- Ollama 설정값
- 데이터베이스 연결 설정
- SQLAlchemy ORM 모델
- Pydantic 요청/응답 모델
- 게시글 CRUD API
- AI 요약 API
- AI 모델 호출 로직
- 예외 처리

이러한 것들이 있었다. 따라서 2-4에서는 기존 코드를 역할별 파일과 폴더로 분리하는 것을 목표로 했다.

---

## 3. 최종 디렉토리 구조

```text
week02-fastapi-community/
├── main.py
├── core/
│   ├── __init__.py
│   └── config.py
├── database/
│   ├── __init__.py
│   ├── base.py
│   └── session.py
├── models/
│   ├── __init__.py
│   └── post.py
├── schemas/
│   ├── __init__.py
│   └── post.py
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       └── posts.py
├── services/
│   ├── __init__.py
│   └── ai_summary_service.py
├── README.md
├── pyproject.toml
├── uv.lock
└── .python-version
```

---

## 4. 폴더별 역할

### `core/`

프로젝트 전체에서 사용하는 설정값을 관리한다.

현재는 Ollama API URL, 모델명, 데이터베이스 URL을 `config.py`에 분리했다.

### `database/`

데이터베이스 연결과 세션 관리를 담당한다.

- `base.py`: SQLAlchemy ORM 모델의 부모 클래스인 `Base` 관리
- `session.py`: `engine`, `SessionLocal`, `get_db()` 관리

### `models/`

데이터베이스 테이블 구조를 정의한다.

현재는 게시글 테이블을 나타내는 `Post` 모델만 분리했다.

### `schemas/`

API 요청과 응답에 사용할 Pydantic 모델을 정의한다.

DB 테이블 구조와 API 입출력 구조는 목적이 다르기 때문에 `models`와 `schemas`를 분리했다.

### `api/routes/`

클라이언트가 호출하는 HTTP API 경로를 정의한다.

현재는 게시글 CRUD와 AI 요약 API를 `posts.py`에 분리했다.

### `services/`

비즈니스 로직이나 외부 서비스 호출을 담당한다.

Ollama에 요약 요청을 보내는 `request_ai_summary()` 함수는 API 라우터가 아니라 AI 서비스 책임이라고 판단해 `ai_summary_service.py`로 분리했다.

---

## 5. `main.py` 역할 정리

구조 분리 후 `main.py`는 전체 코드를 직접 들고 있는 파일이 아니라, 애플리케이션을 조립하는 진입점 역할만 하도록 정리했다.

```python
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(posts_router)
```

즉, `main.py`는 다음 역할만 담당한다.

- FastAPI 앱 생성
- DB 테이블 생성
- 라우터 등록
- 기본 서버 확인용 라우트 제공

---

## 6. 구조 분리 후 import 확인

구조를 여러 파일로 분리하면 import 경로가 잘못되거나 필요한 모듈을 누락하는 문제가 생길 수 있다.

서버를 실행하기 전에 다음 명령으로 `main.py`가 정상적으로 import되는지 먼저 확인했다.

```bash
.venv/bin/python -c "import main"
```

이 명령은 서버를 실행하지는 않는다.  
하지만 `main.py`를 Python 모듈로 불러오면서 연결된 모듈들의 import 오류, 문법 오류, 초기화 오류를 빠르게 확인할 수 있다.

실제 API 요청과 응답이 정상적으로 동작하는지는 이후 `uvicorn main:app --reload`로 서버를 실행하고 `/docs`에서 별도로 확인해야 한다.

---

## 7. 새로 배운 점

- 구조 분리는 파일을 나누는 작업이 아니라, 코드의 책임을 다시 나누는 작업이다.
- `main.py`는 모든 로직을 담기보다 앱을 조립하는 진입점 역할로 두는 것이 좋다.
- SQLAlchemy 모델과 Pydantic 스키마는 목적이 다르므로 분리하는 편이 명확하다.
- 라우터는 HTTP 요청을 받는 계층이고, 서비스는 실제 작업이나 외부 API 호출을 담당하는 계층이다.
- `__init__.py`는 해당 폴더를 Python 패키지로 인식하게 하는 파일이며, 현재 단계에서는 빈 파일로 두었다.
- 구조 분리 후에는 서버 실행 전에 `import main`으로 import 경로 문제를 먼저 확인할 수 있다.

</details>

---

<details>
<summary>[2-2 확장] AI 요약 스트리밍 응답 구현</summary>

## 1. 진행 상황

1. 기존 AI 요약 응답 흐름 확인 ✅
2. 스트리밍 전용 엔드포인트 설계 ✅
3. Ollama 스트리밍 응답 형식 학습 ✅
4. `httpx.AsyncClient.stream()` 사용 방식 학습 ✅
5. FastAPI `StreamingResponse` 연결 ✅
6. `curl -N`으로 스트리밍 응답 테스트 ✅
7. 생성된 요약문 DB 저장 방식은 추후 개선 사항으로 보류

## 2. 구현 목표

기존 AI 요약 API는 Ollama가 요약문을 모두 생성할 때까지 기다린 뒤, 완성된 결과를 한 번에 반환하는 방식이다.

이번 확장에서는 LLM이 응답을 생성하는 동안 결과 조각을 클라이언트에 바로 전달하는 스트리밍 응답을 구현하는 것을 목표로 한다.

이를 통해 응답 시간이 긴 AI 모델을 사용할 때도 사용자가 빈 화면에서 기다리는 것이 아니라, 생성되는 내용을 실시간으로 확인할 수 있는 구조를 경험해본다.

기존 `POST /posts/{post_id}/summary` API는 유지하고, 스트리밍 학습을 위해 별도의 엔드포인트를 추가하는 방향으로 진행한다.

## 3. 일반 응답과 스트리밍 응답 차이

기존 일반 요약 API는 Ollama가 응답을 모두 생성한 뒤 완성된 JSON을 한 번에 반환한다.

```python
result["choices"][0]["message"]["content"]
```

이 구조에서 `message.content`는 완성된 assistant 메시지의 전체 본문을 의미한다.

반면 스트리밍 응답은 완성된 답변 전체가 아니라, 생성 중인 응답 조각이 여러 번 나누어 전달된다.

```python
data["choices"][0]["delta"].get("content")
```

스트리밍 응답에서 `delta.content`는 이번에 새로 생성된 텍스트 조각을 의미한다.  
따라서 일반 응답은 `return`으로 완성된 문자열을 반환하고, 스트리밍 응답은 `yield`로 조각을 하나씩 전달한다.

## 4. FastAPI `StreamingResponse` 사용 흐름

스트리밍 응답을 위해 기존 요약 API를 수정하지 않고, 별도의 엔드포인트를 추가했다.

```text
POST /posts/{post_id}/summary/stream
```

이 API는 게시글을 조회한 뒤, `stream_ai_summary()` 함수가 생성하는 응답 조각을 `StreamingResponse`로 감싸 클라이언트에 전달한다.

```python
return StreamingResponse(
    stream_ai_summary(post.title, post.content),
    media_type="text/event-stream"
)
```

FastAPI 서버는 직접 화면에 텍스트를 보여주는 것이 아니라, 응답 조각을 HTTP 응답으로 계속 보내는 역할을 한다.  
실제로 화면에 실시간으로 보여주는 역할은 `curl -N`이나 이후 프론트엔드의 JavaScript가 담당한다.

## 5. Ollama 스트리밍 응답 처리 방식

Ollama의 OpenAI 호환 API에서 `"stream": True`로 요청하면 응답이 다음과 같은 형태의 JSON 문자열 조각으로 전달된다.

```text
data: {"id":"chatcmpl-882","object":"chat.completion.chunk","choices":[{"delta":{"content":"..."}}]}
```

이 한 줄은 최종 답변 전체가 아니라, 스트리밍 응답 한 조각을 담은 JSON 문자열이다.

따라서 그대로 클라이언트에 보내면 메타데이터까지 모두 출력된다.  
요약문 본문만 보여주기 위해 다음 순서로 처리했다.

1. `data: ` 접두어 제거
2. JSON 문자열을 Python 딕셔너리로 변환 (json.loads())
3. `choices[0].delta.content` 값 추출
4. 추출한 텍스트 조각만 `yield`

여기서 `chunk`라는 변수명은 스트리밍으로 전달되는 텍스트 조각을 의미한다.

## 6. 테스트 방법

FastAPI 문서 화면에서도 API 호출은 가능하지만, 스트리밍 응답이 실시간으로 출력되는지 확인하기에는 터미널의 `curl`이 더 적합했다.

```bash
curl -N -X POST http://127.0.0.1:8001/posts/4/summary/stream
```

`-N` 옵션은 응답을 모아서 한 번에 출력하지 않고, 서버가 보내는 대로 바로 출력하도록 하는 옵션이다.

테스트 결과, 처음에는 Ollama가 보내는 원본 JSON 조각이 그대로 출력되었다.  
이후 JSON에서 `content` 값만 추출하도록 수정해 실제 요약문만 스트리밍으로 출력되도록 개선했다.

## 7. 새로 배운 점

- `"stream": True`를 사용하면 LLM 응답을 한 번에 받지 않고 조각 단위로 받을 수 있다.
- `httpx.AsyncClient.stream()`은 HTTP 응답을 열어둔 상태에서 데이터를 조금씩 읽을 때 사용한다.
- `yield`는 값을 하나 반환하고 함수를 끝내는 것이 아니라, 다음 값이 올 때까지 함수 실행 상태를 잠시 멈춘다.
- `StreamingResponse`는 generator 또는 async generator가 만들어내는 값을 클라이언트에 계속 전달하는 FastAPI 응답 객체다.
- 일반 응답에서는 `message.content`를 사용하고, 스트리밍 응답에서는 `delta.content`를 사용한다.
- `chunk`는 스트리밍으로 전달되는 작은 데이터 조각을 표현할 때 자주 쓰는 변수명이다.
- 요약 API는 AI 기능이지만 중심 리소스가 게시글이므로, 현재 단계에서는 `posts.py`에 두는 것이 자연스럽다고 판단했다.
- 현재 스트리밍 응답은 실시간 출력에 집중했으며, 생성된 요약문을 DB에 저장하는 처리는 추후 개선 사항으로 남겼다.
</details>


<details>
<summary>[2-5] 프론트엔드 화면 구현</summary>

## 1. 진행 상황

1. Streamlit 의존성 추가 ✅
2. 게시글 목록 및 상세 조회 화면 구현 ✅
3. 새 게시글 작성 화면 구현 ✅
4. AI 요약 스트리밍 API 연결 ✅
5. 브라우저에서 실시간 요약 출력 확인 ✅
6. 게시글 수정 및 삭제 기능 연결 ✅
7. 삭제 전 확인 경고 추가 ✅
8. 상세 화면 레이아웃 개선 ✅

## 2. 구현 목표

FastAPI 문서 화면과 `curl`로 확인했던 API 기능을 사용자가 직접 조작할 수 있는 화면으로 연결한다.

프론트엔드 문법을 깊게 학습하기보다, 백엔드 API가 실제 사용자 흐름에서 어떻게 사용되는지 경험하는 데 초점을 두었다.

## 3. 화면 구성 설계

화면은 게시글 탐색과 작성을 빠르게 오갈 수 있도록 두 개의 탭으로 나누었다.

- 게시글 살펴보기
  - 전체 게시글 수와 요약 생성 상태 확인
  - 게시글 선택 및 상세 내용 조회
  - 스트리밍 방식으로 AI 요약 생성
  - 게시글 수정
  - 삭제 전 확인 절차를 거친 게시글 삭제
- 새 게시글 작성
  - 제목과 본문 입력
  - FastAPI 게시글 생성 API 호출

## 4. API 연동 흐름

Streamlit은 FastAPI 서버와 별도의 프로세스로 실행된다.

```text
사용자
→ Streamlit 화면
→ FastAPI API 요청
→ SQLite 조회 또는 Ollama 요청
→ Streamlit 화면에 결과 표시
```

FastAPI 서버는 `8001`번 포트, Streamlit 화면은 기본값인 `8501`번 포트를 사용한다.

## 5. 스트리밍 응답 표시 방식

Streamlit의 `st.write_stream()`에 FastAPI 스트리밍 응답을 읽는 generator를 전달했다.

```python
st.write_stream(stream_summary(post["id"]))
```

generator가 텍스트 조각을 하나씩 전달하면 Streamlit 화면에도 요약문이 실시간으로 이어서 표시된다.

## 6. 테스트 방법

두 개의 터미널에서 FastAPI와 Streamlit을 각각 실행했다.

```bash
uv run uvicorn main:app --reload --port 8001
uv run streamlit run streamlit_app.py
```

이후 `http://localhost:8501`에서 게시글 목록 조회와 스트리밍 요약 출력을 확인했다.

## 7. 새로 배운 점

- Streamlit은 Python 코드만으로 입력 폼, 탭, 버튼과 같은 기본 UI를 빠르게 구성할 수 있다.
- Streamlit과 FastAPI는 하나의 서버가 아니라, 서로 다른 포트에서 실행되는 별도의 애플리케이션이다.
- `st.write_stream()`은 generator가 전달하는 문자열 조각을 화면에 이어서 표시한다.
- 프론트엔드를 연결하면 백엔드 기능이 실제 사용자 흐름에서 어떻게 사용되는지 더 구체적으로 확인할 수 있다.

</details>
