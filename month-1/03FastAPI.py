import warnings
from datetime import datetime
from typing import Optional,Dict
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel,Field, field_validator, computed_field

# Suppress the underlying Google GenAI/FastAPI dependency warning lookups if needed
warnings.filterwarnings("ignore", message=".*automatic function calling.*")

app = FastAPI(
    title="FastAPI with LLMs",
    description="A FastAPI application that integrates multiple LLMs (OpenAI, Google GenAI, Anthropic) to answer questions.",
    version="1.0.0",
    contact={
        "name": "Yogesh",
        "email": "yogesh@example.com"
    }
)

# ----------------------------------------------------
# 💾 IN-MEMORY STORAGE DATABASE
# ----------------------------------------------------
# Simulation dictionary acting as our persistent database storage block

TODO_DATABASE : Dict[int, dict] = {}  # In-memory database to store TODO items
id_counter: int = 1  # Counter to generate unique IDs for TODO items

# ----------------------------------------------------
# 🛡️ PYDANTIC V2 SCHEMAS (DATA Blueprints)
# ----------------------------------------------------

class TodoRequest(BaseModel):
     """Schema representing incoming user registration data."""
     title: str = Field(...,min_length=1, max_length=100, description="Title of the task")
     description: Optional[str] = Field(None, description="Detailed notes of the task")
     priority: int= Field(default=1, ge=1,le=5, description="Priority rating ranging from 1 (lowest) to 5 (highest).")

     @field_validator("title")
     @classmethod
     def clean_and_validate_title(cls, value: str) -> str:
          """Field validator guaranteeing text string is not entirely empty whitespace."""
          cleaned_value = value.strip()
          if not cleaned_value:
               raise ValueError("Title must contain non-whitespace characters.")
          return cleaned_value


class TodoResponse(BaseModel):
     """Schema representing structured data outbound payloads to the user client."""
     id: int = Field(..., description = "Unique auto-incrementing ID identifier.")
     title: str
     description: Optional[str]
     priority: int
     completed: bool
     created_at: datetime

     @computed_field
     def task_urgency(self) ->str:
          """Computed field generating context metadata on serialization pipelines."""
          if self.completed:
               return "DONE"
          return "HIGH_URGENCY" if self.priority >= 4 else "NORMAL"

# ----------------------------------------------------
# 🛣️ FASTAPI ENDPOINTS (CRUD ENGINE)
# ----------------------------------------------------

@app.post(
     "/todos",
     response_model=TodoResponse,
     status_code=status.HTTP_201_CREATED,
     summary="Create a new task Item"
)

def create_todo(payload: TodoRequest):
     """Endpoint to create a new TODO item in the in-memory database."""
     global id_counter
     # Store raw attributes in a base dictionary configuration
     new_todo = {
        "id": id_counter,
        "title": payload.title,
        "description": payload.description,
        "priority": payload.priority,
        "completed": False,
        "created_at": datetime.utcnow()
     }

     TODO_DATABASE[id_counter] = new_todo
     id_counter += 1
     return new_todo

@app.get(
     "/todos",
     response_model=list[TodoResponse],
     status_code=status.HTTP_200_OK,
     summary="Retrieve all task items"
)

def get_all_todos():
     """Endpoint to fetch all TODO items from the in-memory database."""
     return list(TODO_DATABASE.values())

@app.get(
     "/todos/{todo_id}",
     response_model=TodoResponse,
     status_code=status.HTTP_200_OK,
     summary="Fetch an isolated item via ID lookup"
)

def get_single_todo(todo_id: int):
     if todo_id not in TODO_DATABASE:
          raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Todo item with ID {todo_id} not found."
          )
     return TODO_DATABASE[todo_id]

@app.put(
     "/todos/{todo_id}",
     response_model=TodoResponse,
     status_code=status.HTTP_200_OK,
     summary="Updates attributes on an existing task"
)

def update_todo(todo_id: int, payload:TodoRequest):
     if todo_id not in TODO_DATABASE:
          raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Todo item with ID {todo_id} not found."
          )
     # Fetch historical item to maintain persistent context states like completion and timestamp
     historical_item = TODO_DATABASE[todo_id]

     # Update the existing record with new values
     updated_todo = {
          
          "id": todo_id,
          "title": payload.title,
          "description": payload.description,
          "priority": payload.priority,
          "completed": historical_item["completed"],
          "created_at": historical_item["created_at"]
     }
     TODO_DATABASE[todo_id] = updated_todo
     return updated_todo

@app.patch(
     "/todos/{todo_id}/toggle",
     response_model=TodoResponse,
     status_code=status.HTTP_200_OK,
     summary="Toggle task status metrics"
)

def toggle_todo_status(todo_id: int):
    if todo_id not in TODO_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Todo item with ID {todo_id} does not exist."
        )
    
    TODO_DATABASE[todo_id]["completed"] = not TODO_DATABASE[todo_id]["completed"]
    return TODO_DATABASE[todo_id]

@app.delete(
    "/todos/{todo_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently purge an item from registry records"
)
def delete_todo(todo_id: int):
    if todo_id not in TODO_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Todo item with ID {todo_id} does not exist."
        )
    del TODO_DATABASE[todo_id]
    return None