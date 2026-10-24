import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

DATASET_FILE = Path(__file__).resolve().parent / "dataset.jsonl"

Category = Literal[
    # Retrieval/answer categories (same as the RAG course evaluator)
    "direct_fact",
    "temporal",
    "spanning",
    "comparative",
    "numerical",
    "relationship",
    "holistic",
    # Support-bot behaviour
    "guardrail",
    "off_topic",
    "multi_question",
    "escalation",
    "booking",
]
Behavior = Literal["answer", "block", "decline", "escalate", "offer_booking", "request_call"]


class EvalCase(BaseModel):
    """One test question for the support agent."""

    id: str
    category: Category
    scenario: int | None = Field(None, ge=1, le=6, description="Brief scenario (1-6) it covers")
    language: Literal["en", "es"] = "en"
    question: str
    keywords: list[str] = Field(
        description="Must appear in the retrieved knowledge (MRR, nDCG, coverage)"
    )
    expected_sources: list[str] = Field(description="Knowledge files (stems) that hold the answer")
    reference_answer: str = Field(description="What a good reply says or does, for the judge")
    expected_behavior: Behavior
    expected_tools: list[str] = Field(description="Tools the agent must call")
    forbidden: list[str] = Field(description="Substrings that must not appear in the reply")


def load_dataset(path: Path = DATASET_FILE) -> list[EvalCase]:
    with path.open(encoding="utf-8") as f:
        return [EvalCase.model_validate(json.loads(line)) for line in f if line.strip()]
