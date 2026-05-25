from fastapi import HTTPException
import httpx

from core.config import OLLAMA_MODEL, OLLAMA_URL


async def request_ai_summary(title: str, content: str) -> str:
    prompt = (
        "다음 게시글을 2~3문장으로 요약해줘.\n\n"
        f"제목: {title}\n\n"
        f"내용:\n{content}"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "너는 커뮤니티 게시글을 간결하게 요약하는 한국어 AI 도우미야. 답변은 최대한 간결하게 해.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI 요약 요청 시간이 초과되었습니다.")

    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="AI 모델 서버 응답에 실패했습니다.")

    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="AI 모델 서버에 연결할 수 없습니다.")