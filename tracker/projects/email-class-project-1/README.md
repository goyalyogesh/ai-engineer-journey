# Fintech Email Classifier

Paste a support/operations email, get back structured JSON — `category`, `urgency`, `sentiment`, `action_items`, `summary` — powered by Gemini + [Instructor](https://python.useinstructor.com/) + Pydantic.

Built as Day 5 of a 90-day .NET → AI Engineer transition (Phase 1 warmup project).

## Demo

![demo](demo.gif)
<!-- Record with kap.app, save as demo.gif in this folder — GitHub will render it above automatically. -->

**Live app:** _add your Streamlit Cloud URL here once deployed_

## What it does

Given raw email text, the classifier returns:

```json
{
  "category": "Fraud Alert",
  "urgency": "Critical",
  "sentiment": "Negative",
  "action_items": ["Freeze the account", "Call the customer back"],
  "summary": "Customer reports an unauthorized $499 charge and requests an immediate callback."
}
```

## Stack

- **Streamlit** — UI
- **Instructor** — turns LLM calls into validated Pydantic objects, no manual JSON parsing
- **Pydantic v2** — the `EmailClassification` schema (`Literal` types constrain the model to a fixed set of categories/urgency/sentiment values instead of free-text)
- **Gemini 2.5 Flash** (via `google-genai`) — the underlying LLM

## Architecture

Two files, one clean split: `app.py` owns the UI, `email_classifier.py` owns everything about talking to the LLM. Neither imports Streamlit-specific things into the logic module, so `email_classifier.py` can be tested and run standalone (`python email_classifier.py`) with no browser involved.

```
User pastes email text
        │
        ▼
┌─────────────────────┐
│  app.py (Streamlit)  │  UI only — text area, sample picker, results rendering
└──────────┬───────────┘
           │ calls classify_email(email_text, client)
           ▼
┌───────────────────────────┐
│  email_classifier.py       │
│                             │
│  1. genai.Client()          │──▶ authenticates to Gemini using GOOGLE_API_KEY
│  2. instructor.from_genai() │──▶ "patches" the raw client so it understands
│                             │    response_model=<a Pydantic class>
│  3. client.chat.completions │
│     .create(                │──▶ sends the email text + the EmailClassification
│       model=...,            │    schema (as a function-call spec) to Gemini
│       response_model=       │
│         EmailClassification,│
│       messages=[...],       │
│     )                       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   Gemini 2.5 Flash            │  returns a structured function-call response
└──────────┬─────────────────────┘  matching the schema's fields (not free text)
           │
           ▼
┌─────────────────────────────┐
│  Instructor validation loop   │  parses the model's output against
│  (up to max_retries=2)        │  EmailClassification — if a field is malformed
│                                │  or missing, it automatically re-prompts
│                                │  Gemini with the validation error and retries
└──────────┬─────────────────────┘
           │  a validated EmailClassification instance, guaranteed
           ▼  to match the schema — no manual json.loads() or try/except
┌───────────────────────┐
│  app.py renders it      │  st.metric() for category/urgency/sentiment,
│                          │  bullet list for action_items, st.json() for raw output
└───────────────────────┘
```

**Why this split matters, not just style:** the same `email_classifier.py` module could be dropped into a FastAPI endpoint, a CLI script, or a batch job tomorrow with zero changes — it has no idea Streamlit exists. That's the same "business logic vs. framework glue" separation you'd reach for in a C# solution (a service/domain layer that doesn't reference `Microsoft.AspNetCore` directly). `app.py`'s `@st.cache_resource`-wrapped client also avoids reconnecting to Gemini on every single Streamlit rerun (Streamlit reruns the whole script top-to-bottom on every interaction — without caching, every button click would rebuild the client from scratch).

**Where validation actually happens:** Instructor doesn't just parse Gemini's response — it retries automatically. If Gemini returns `"urgency": "very high"` (not one of the `Literal["Low","Medium","High","Critical"]` values), Pydantic's validation fails, and Instructor feeds that exact validation error back to Gemini as a follow-up message, asking it to correct the output — up to `max_retries=2` times — before ever handing control back to `app.py`. This is why the UI code never has a "what if the JSON is malformed" branch: by the time `classify_email()` returns, the result is either a valid `EmailClassification` or the call raised an exception (caught by `app.py`'s `try/except`).

## Files

| File | Purpose |
|---|---|
| `email_classifier.py` | Pydantic schema + the Instructor call — the actual logic, framework-agnostic and independently testable (`python email_classifier.py` runs a smoke test) |
| `app.py` | Streamlit UI — imports from `email_classifier.py`, adds sample emails, client caching, and error handling |
| `requirements.txt` | Dependencies for this project specifically — kept separate from the rest of the repo since Streamlit Cloud needs its own `requirements.txt` to install from |
| `.env.example` | Template for the required `GOOGLE_API_KEY` — copy to `.env` locally, never commit the real one |

## Run it locally

```bash
python3 -m venv env
source env/bin/activate          # Windows: env\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste in your real GOOGLE_API_KEY

streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this folder to its own GitHub repo (`fintech-email-classifier`, per the plan) — or point Streamlit Cloud at this path if deploying straight from the monorepo.
2. [share.streamlit.io](https://share.streamlit.io) → New app → point at `app.py`.
3. App settings → Secrets → add:
   ```toml
   GOOGLE_API_KEY = "your-real-key"
   ```
   (`app.py` already bridges `st.secrets` into `os.environ` — no code changes needed for deployment.)
4. Deploy, grab the live URL, and paste it above and into `tracker/projects/README.md`.

## Day 5 checklist (from `daily-plans/day-005.md`)

- [x] Project scaffolded (schema, classification logic, Streamlit UI)
- [x] Email → JSON classification (category, urgency, sentiment, action_items, summary)
- [x] Streamlit UI
- [ ] Deploy to Streamlit Cloud
- [ ] Demo GIF recorded (kap.app) and embedded above
- [ ] LinkedIn post #2 — "First AI project shipped"
