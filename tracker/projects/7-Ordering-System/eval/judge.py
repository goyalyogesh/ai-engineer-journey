"""LLM-as-judge for root-cause accuracy grading (03-EVALUATION.md Section
3). Deliberately a separate model call from the agent's own reasoning --
grading your own homework with the identical context window is a real
bias risk worth naming, not ignoring.
"""
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

_JUDGE_PROMPT = """Given:
- The scenario's expected root cause: {expected_root_cause}
- The agent's actual diagnosis: {actual_root_cause}

Question: does the agent's diagnosis identify the same underlying root cause,
even if worded differently? Set passed=true if yes (PASS), false if no (FAIL),
and give one sentence of reasoning either way."""


class JudgeVerdict(BaseModel):
    passed: bool
    reasoning: str


async def judge_root_cause(
    expected_root_cause: str, actual_root_cause: str, llm: BaseChatModel | None = None
) -> JudgeVerdict:
    llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(JudgeVerdict)
    prompt = _JUDGE_PROMPT.format(
        expected_root_cause=expected_root_cause, actual_root_cause=actual_root_cause
    )
    return await structured_llm.ainvoke(prompt)
