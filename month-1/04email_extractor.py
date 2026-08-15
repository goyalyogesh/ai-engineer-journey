import instructor
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

load_dotenv()

#1. Define your target pydantic Schema for the email extraction task
class Person(BaseModel):
    name: str = Field(...,description="Full name of the individual")
    job_title: Optional[str] = Field(None, description="their professional title or corporate role")
    company:Optional[str] = Field(None, description="the organization or business they are associated with")
    email_address: str= Field(..., description ="The email address of the individual")
    skills: List[str] = Field(..., description="List of skills possessed by the individual")

    @field_validator("email_address")
    @classmethod
    def validate_email_format(cls,value: str)->str:
        """Enforce basic syntax check on the extracted email address"""
        if "@" not in value or "." not in value:
            raise ValueError(f"Extracted string '{value}' does not appear to be a valid email address.")
        return value.strip().lower()

# 2. Initialize the native Google GenAI Client and patch it with Instructor
# Ensure your GEMINI_API_KEY environment variable is exported or set in your .env file
native_client = genai.Client()
client = instructor.from_genai(native_client)

# 3. Define the unstructured input dataset
sample_email = """
Hey Team,

I wanted to introduce Yogesh Goyal who just joined our engineering division as a Senior AI Architect here at AlphaTech Solutions. 
Yogesh brings massive expertise in Python development, FastAPI, Pydantic data schemas, and agentic workflows. 
If you need help optimizing your LLM pipeline setups, reach out to him directly at yogesh@alphatech.io or find him on Slack.

Best regards,
Sarah Jenkins
Director of Operations
"""

print("🚀 Executing LLM Structured Extraction Pipeline...")

# 4. The 5-Line Core Instructor Call

extracted_person = client.chat.completions.create(
    model="gemini-2.5-flash",
    response_model=Person,
    messages=[
        {"role": "user", "content": f"Extract the primary new hire person information from this email:\n\n{sample_email}"}
    ],
    max_retries=2
)

# 5. Access your structured data natively
print("\n✅ Extraction Successful! Outputting clean Pydantic object attributes:\n")
print(f"Name:        {extracted_person.name}")
print(f"Role:        {extracted_person.job_title}")
print(f"Company:     {extracted_person.company}")
print(f"Email:       {extracted_person.email_address}")
print(f"Skills Identified: {', '.join(extracted_person.skills)}")

# Verify it acts as a genuine Pydantic instance by dumping it to standard JSON dictionary lines
print("\n📝 Complete Serialized JSON Object Context:")
print(extracted_person.model_dump_json(indent=2))