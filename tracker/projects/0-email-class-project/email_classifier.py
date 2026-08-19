"""
Core classification logic — framework-agnostic, no Streamlit imports here so
it stays independently testable (run this file directly for a smoke test).

Reuses the same load_dotenv + genai.Client + instructor.from_genai pattern
already debugged in month-1/04email_extractor.py.
"""

from __future__ import annotations

from typing import List, Literal, Optional

import instructor
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"


class EmailClassification(BaseModel):
    """Structured classification result for a single email."""

    category: Literal[
        "Fraud Alert",
        "Payment Issue",
        "Account Access",
        "Billing Inquiry",
        "Compliance/Legal",
        "Customer Complaint",
        "General Inquiry",
        "Other",
    ] = Field(..., description="The primary category this email falls under.")
    urgency: Literal["Low", "Medium", "High", "Critical"] = Field(
        ..., description="How urgently this email needs a response."
    )
    sentiment: Literal["Positive", "Neutral", "Negative"] = Field(
        ..., description="The overall emotional tone of the sender."
    )
    action_items: List[str] = Field(
        default_factory=list,
        description="Concrete follow-up actions implied by the email, if any.",
    )
    summary: str = Field(..., description="A one- to two-sentence summary of the email.")


def get_client() -> instructor.Instructor:
    """Create an Instructor-patched Gemini client. Callers should build this
    once and reuse it — see app.py's @st.cache_resource usage."""
    native_client = genai.Client()
    return instructor.from_genai(native_client)


def classify_email(
    email_text: str, client: Optional[instructor.Instructor] = None
) -> EmailClassification:
    """Classify a raw email string into category/urgency/sentiment/action_items/summary."""
    client = client or get_client()
    return client.chat.completions.create(
        model=MODEL_NAME,
        response_model=EmailClassification,
        messages=[
            {
                "role": "user",
                "content": (
                    "Classify the following email for a fintech support/operations "
                    "team. Be concise and precise.\n\n"
                    f"{email_text}"
                ),
            }
        ],
        max_retries=2,
    )


if __name__ == "__main__":
    # Quick manual smoke test: python email_classifier.py
    sample = """Subject: Urgent - unauthorized charge on my account

Hi team,

I just noticed a $499 charge on my account that I did not authorize. This
looks like fraud. Please freeze my account and call me back immediately at
555-0134.

Frustrated,
Alex Rivera"""

    result = classify_email(sample)
    print(result.model_dump_json(indent=2))
