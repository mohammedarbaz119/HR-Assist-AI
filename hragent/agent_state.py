from typing import TypedDict, Annotated, List, Optional,Literal
from typing import BinaryIO
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
    job_description: Optional[str] # Job description text
    years_of_experience: Optional[int] # Years of experience of the candidate
    role: Optional[str] 
    # --- Resume Parsing related ---
    file_path: Optional[str] # Path to the uploaded resume file
    filename: Optional[str] # Name of the uploaded file
    file_extension: Optional[str] # File extension of the uploaded file
    parsed_resume_data: Optional[ResumeParsedData] # Data after PDF parsing
    error: Optional[str] 