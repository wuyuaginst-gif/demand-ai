import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import (
    DemandRequest, ClassifyResponse, SummaryResponse, 
    SimilarResponse, StoreResponse, SimilarDemand
)
from app.services import DemandClassifier, DemandSummarizer, DemandRetriever

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

classifier: DemandClassifier = None
summarizer: DemandSummarizer = None
retriever: DemandRetriever = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global classifier, summarizer, retriever
    logger.info("正在初始化 AI 服务...")
    logger.info(f"Ollama: {settings.ollama_base_url}, Model: {settings.model_name}")
    
    classifier = DemandClassifier(settings.ollama_base_url, settings.model_name)
    summarizer = DemandSummarizer(settings.ollama_base_url, settings.model_name)
    retriever = DemandRetriever(
        settings.ollama_base_url,
        settings.embedding_model,
        settings.chroma_persist_dir,
        settings.chroma_collection_name
    )
    logger.info("AI 服务初始化完成")
    yield
    logger.info("应用关闭")


app = FastAPI(
    title="需求管理 AI 服务",
    description="智能需求分类、摘要、检索服务",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "demand-ai"}


@app.get("/stats")
async def get_stats():
    return {"vector_db": retriever.get_stats() if retriever else None, "model": settings.model_name}


@app.post("/classify", response_model=ClassifyResponse)
async def classify_demand(req: DemandRequest):
    try:
        result = classifier.classify(req.content)
        if "error" in result:
            return ClassifyResponse(success=False, error=result.get("error"))
        return ClassifyResponse(success=True, data=result)
    except Exception as e:
        logger.exception("分类失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize", response_model=SummaryResponse)
async def summarize_demand(req: DemandRequest):
    try:
        summary = summarizer.summarize(req.content)
        return SummaryResponse(success=True, summary=summary)
    except Exception as e:
        logger.exception("摘要生成失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/similar", response_model=SimilarResponse)
async def find_similar(req: DemandRequest):
    try:
        results = retriever.find_similar(req.content)
        return SimilarResponse(
            success=True,
            similar_demands=[SimilarDemand(**r) for r in results]
        )
    except Exception as e:
        logger.exception("检索失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/store", response_model=StoreResponse)
async def store_demand(req: DemandRequest):
    if not req.demand_id:
        raise HTTPException(status_code=400, detail="demand_id 必填")
    try:
        retriever.add_demand(req.demand_id, req.content)
        return StoreResponse(success=True, message=f"需求 {req.demand_id} 已存储")
    except Exception as e:
        logger.exception("存储失败")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
