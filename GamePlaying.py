from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings
import numpy as np

app = FastAPI()
origins = ["*"] # 또는 필요한 경우 허용할 원본을 지정합니다.

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def levenshtein_distance(s1, s2):
    """
    Compute the Levenshtein distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

class Query(BaseModel):
    input: str

@app.get('/hello')
async def hello(query: Query):
    try:
        data1 = '정답 쿼리문..'
        data2 = query.input
        
        # 레벤슈타인 거리 계산
        levenshtein_dist = levenshtein_distance(data1, data2)
        
        # 문자열 길이에 대한 유사성 계산
        max_len = max(len(data1), len(data2))
        similarity_percentage = ((max_len - levenshtein_dist) / max_len) * 100
        
        return {'message': similarity_percentage, 'data': data2}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
