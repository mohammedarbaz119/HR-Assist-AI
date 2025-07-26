from typing import TypedDict, Annotated, List, Optional,Literal
from fastapi import UploadFile
from langchain_core.messages import BaseMessage
import operator

class ResumeParsedData(TypedDict):
    full_text: str
    sections: Optional[dict] # e.g., {"Experience": [...], "Education": [...], "Skills": [...]}
    keywords: Optional[List[str]]
    summary: Optional[str]

class AgentState(TypedDict):
    # Conversation history with the user
    messages: Annotated[List[BaseMessage], operator.add]
    purpose: Literal["score","general"] # Purpose of the conversation (e.g., "resume evaluation", "job search")
    next_action: Optional[str] # What the router decided ('search', 'parse_resume', 'end')
    response: Optional[str] # Response from the LLM 
    role: Optional[str] # Role of the user (e.g., "job seeker", "recruiter")
    # --- Resume Parsing related ---
    file: Optional[UploadFile] # Path to the temporarily saved resume file
    parsed_resume_data: Optional[ResumeParsedData] # Data after PDF parsing
    error: Optional[str] 