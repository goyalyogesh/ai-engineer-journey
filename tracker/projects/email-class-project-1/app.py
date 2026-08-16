import os

import streamlit as st

from email_classifier import EmailClassification, classify_email, get_client

# Streamlit Cloud exposes secrets via st.secrets, not real environment
# variables — bridge it into os.environ so genai.Client() (which only reads
# os.environ) can find it. Locally, .env + load_dotenv() already covers this,
# so this is a no-op on your machine.
if "GOOGLE_API_KEY" not in os.environ and "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

st.set_page_config(page_title="Fintech Email Classifier", page_icon="📧")


@st.cache_resource
def cached_client():
    """Reuse one Instructor-patched client across Streamlit reruns instead
    of reconnecting on every interaction."""
    return get_client()


SAMPLE_EMAILS = {
    "Fraud alert": """Subject: Urgent - unauthorized charge on my account

Hi team,

I just noticed a $499 charge on my account that I did not authorize. This
looks like fraud. Please freeze my account and call me back immediately at
555-0134.

Frustrated,
Alex Rivera""",
    "Billing question": """Subject: Question about last month's invoice

Hello,

Could you clarify the $12.99 "platform fee" on my March statement? I don't
remember seeing this line item before. No rush, just want to understand it.

Thanks,
Priya Nair""",
    "General inquiry": """Subject: Do you support recurring international transfers?

Hi there,

I'm considering your platform for monthly transfers to family abroad. Does
it support recurring international wire transfers, and what are the fees?

Best,
Daniel Osei""",
}

st.title("📧 Fintech Email Classifier")
st.caption(
    "Paste a support/operations email → get category, urgency, sentiment, "
    "action items, and a summary."
)

with st.sidebar:
    st.subheader("Try a sample")
    choice = st.selectbox("Sample email", ["— pick one —"] + list(SAMPLE_EMAILS.keys()))

default_text = SAMPLE_EMAILS.get(choice, "") if choice != "— pick one —" else ""
email_text = st.text_area(
    "Email content", value=default_text, height=220, placeholder="Paste an email here..."
)

if st.button("Classify Email", type="primary", disabled=not email_text.strip()):
    with st.spinner("Classifying..."):
        try:
            result: EmailClassification = classify_email(email_text, client=cached_client())
        except Exception as exc:  # surfaced to the UI, not swallowed
            st.error(f"Classification failed: {exc}")
        else:
            urgency_color = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
            sentiment_emoji = {"Positive": "🙂", "Neutral": "😐", "Negative": "🙁"}

            col1, col2, col3 = st.columns(3)
            col1.metric("Category", result.category)
            col2.metric("Urgency", f"{urgency_color.get(result.urgency, '')} {result.urgency}")
            col3.metric(
                "Sentiment", f"{sentiment_emoji.get(result.sentiment, '')} {result.sentiment}"
            )

            st.subheader("Summary")
            st.write(result.summary)

            st.subheader("Action Items")
            if result.action_items:
                for item in result.action_items:
                    st.markdown(f"- {item}")
            else:
                st.caption("No specific action items identified.")

            with st.expander("Raw JSON"):
                st.json(result.model_dump())
