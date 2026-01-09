import json
import logging
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class DemandClassifier:
    """需求分类服务"""

    def __init__(self, base_url: str, model: str):
        self.llm = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=0,
            timeout=120
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的IT需求分类专家，服务于金融机构的科技部门。

根据用户提交的需求内容，分析并返回JSON格式的分类结果：
{{
  "type": "新功能开发|Bug修复|运维支持|咨询|数据需求",
  "urgency": "紧急|一般|低",
  "department": "建议处理的部门名称",
  "reason": "分类理由（一句话说明）"
}}

分类标准：
- 新功能开发：新增功能、功能优化、界面改进等
- Bug修复：系统报错、功能异常、数据错误等
- 运维支持：权限申请、环境配置、系统维护等
- 咨询：使用咨询、方案咨询、技术咨询等
- 数据需求：数据导出、报表开发、数据修改等

紧急程度判断：
- 紧急：影响核心业务、涉及资金安全、监管要求
- 一般：有明确deadline但非紧急、影响部分用户
- 低：优化类需求、无明确时间要求

只返回JSON，不要其他内容。"""),
            ("human", "{demand}")
        ])
        self.chain = self.prompt | self.llm

    def classify(self, demand_text: str) -> dict:
        """分类需求"""
        try:
            result = self.chain.invoke({"demand": demand_text})
            content = result.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return {"error": "分类结果解析失败", "raw": result.content}
        except Exception as e:
            logger.error(f"分类服务异常: {e}")
            return {"error": str(e)}
