from pydantic import BaseModel, Field
from typing import Optional


class DemandRequest(BaseModel):
    """需求请求"""
    content: str = Field(..., min_length=1, description="需求内容")
    demand_id: Optional[str] = Field(None, description="需求ID")


class ClassifyResult(BaseModel):
    """分类结果"""
    type: str = Field(..., description="需求类型")
    urgency: str = Field(..., description="紧急程度")
    department: str = Field(..., description="建议处理部门")
    reason: str = Field(..., description="分类理由")


class ClassifyResponse(BaseModel):
    """分类响应"""
    success: bool
    data: Optional[ClassifyResult] = None
    error: Optional[str] = None


class SummaryResponse(BaseModel):
    """摘要响应"""
    success: bool
    summary: Optional[str] = None
    error: Optional[str] = None


class SimilarDemand(BaseModel):
    """相似需求"""
    demand_id: Optional[str]
    content: str
    score: float


class SimilarResponse(BaseModel):
    """相似需求响应"""
    success: bool
    similar_demands: list[SimilarDemand] = []
    error: Optional[str] = None


class StoreResponse(BaseModel):
    """存储响应"""
    success: bool
    message: str
