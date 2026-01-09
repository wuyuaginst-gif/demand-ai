import logging
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class DemandSummarizer:
    """需求摘要服务"""

    def __init__(self, base_url: str, model: str):
        self.llm = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=0.3,
            timeout=120
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位资深需求分析师，请用简洁的语言概括需求要点。

输出格式（3句话以内）：
1. 【背景】为什么提这个需求
2. 【诉求】具体要做什么
3. 【预期】期望达到什么效果

注意：简洁明了，每点不超过30字"""),
            ("human", "{demand}")
        ])
        self.chain = self.prompt | self.llm

    def summarize(self, demand_text: str) -> str:
        """生成需求摘要"""
        try:
            result = self.chain.invoke({"demand": demand_text})
            return result.content.strip()
        except Exception as e:
            logger.error(f"摘要服务异常: {e}")
            raise
