import json
from typing import Literal
from fastapi.params import Depends
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import RunnableConfig
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END,START
from langgraph.prebuilt import create_react_agent,ToolNode,tools_condition
from langchain_core.messages import BaseMessage, HumanMessage,SystemMessage,AIMessage
from hragent.agent_state import AgentState
from .nodes import parse_and_extract_resume, resume_scorer
from .utils.llm_builder import build_llm,tool_node,tools
from hragent.nodes.general_question import general_question
from fastapi import FastAPI,Form,UploadFile, HTTPException,Response
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import os

UPLOAD_DIR = Path("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(file: UploadFile,filename: str) -> str:
    file_location = os.path.join(UPLOAD_DIR, filename)

    # Save the file contents
    with open(file_location, "wb") as f:
        contents = await file.read()
        f.write(contents)

    return file_location

llm= build_llm("gemini-2.5-flash")

def router(state:AgentState):
    print("--- ROUTER NODE ---")
    if state.get("file_path"):
        return {"next_action": "parse_resume"}
    
    if state["purpose"] == "general":
        return {"next_action": "general"}
    
    

    




# 3. Build the Graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("parse", parse_and_extract_resume)
workflow.add_node("score", resume_scorer)
workflow.add_node("router", router)
workflow.add_node("general", general_question)
workflow.add_node("tools",tool_node)


# Set the entry point
workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    lambda state: state["next_action"], 
    {
        "parse_resume": "parse",  
        "general": "general",
    },
)
workflow.add_edge(
    "general",
    END
)
workflow.add_conditional_edges(
    "parse",
    lambda state: state["next_action"],
    {
        "score_resume": "score",
        "end": END,
    },
)

workflow.add_conditional_edges("score", tools_condition)
workflow.add_edge("tools", "score")
workflow.add_edge("score", END)


checkpointer = InMemorySaver()
# Compile the graph
agent = workflow.compile(checkpointer=checkpointer)

app = FastAPI()

# @app.post("/chat")
# async def chat(message: str | None = Form(None), role: str | None = Form(None) ,file: UploadFile | None=None):
#     suffix = Path(file.filename).suffix if file else None
#     if file and suffix not in ['.txt', '.pdf', '.docx']:
#         raise HTTPException(422,detail="Unsupported file type. Please upload a .txt, .pdf, or .docx file.")
#     if file and not role:
#         raise HTTPException(422, detail="Role is required when uploading a resume file ")
#     if not file and not message:
#         raise HTTPException(422, detail="Either a message or a file must be provided.")
    
#     if not message:
#         message = "score this resume for the role: " + role
#     response = agent.invoke({
#         "messages": [HumanMessage(content=message)] if message else [],"purpose": "general" if message is None else "score","file": file, "role": role})
    
#     if "error" in response:
#         error_message = response.get("messages", [AIMessage("An error occurred.")])[-1].content
#         print(response["error"])
#         return Response(content=error_message, media_type="text/plain", status_code=500)
#     else:
#         print(response["messages"])
#         if response.get("purpose") == "score":
#             return JSONResponse(content={"parsed_resume_data": response.get("parsed_resume_data"),
#                 "repsonse": response.get("messages", [AIMessage("No response available.")])[-1].content,
#                 },status_code=200, media_type="application/json")
#         else:
#             return Response(content=response.get("messages",[AIMessage("No response available.")])[-1].content, media_type="text/plain")
        
@app.post("/chat")
async def chat(message: str = Form(...),thread_id: str | None = Form(None)):
    if not message.strip():
        raise HTTPException(422, detail="Message cannot be empty.")
 
    if thread_id is not None:
       config = RunnableConfig(configurable={"thread_id": thread_id })
       state = agent.get_state(config=config).values.get("messages", [])
    else:
       thread_id = str(uuid.uuid4())
       config = RunnableConfig(configurable={"thread_id": thread_id })
       state = []
    
    response = agent.invoke({
        "messages": [HumanMessage(content=message)]+state,
        "purpose": "general"
    },config=config)

    if "error" in response:
        error_message = response.get("messages", [AIMessage("An error occurred.")])[-1].content
        print(response["error"])
        return Response(content=error_message, media_type="text/plain", status_code=500)

    return JSONResponse(
        content={"response": response.get("messages", [AIMessage("No response available.")])[-1].content,"thread_id": thread_id},
        media_type="application/json",
        status_code=200
    )

@app.post("/score-resume")
async def score_resume(file: UploadFile, role: str = Form(...), yoe: int = Form(...),job_description: str = Form("")):
    suffix = Path(file.filename).suffix
    if suffix not in ['.txt', '.pdf', '.docx']:
        raise HTTPException(422, detail="Unsupported file type. Please upload a .txt, .pdf, or .docx file.")

    if role is None or yoe is None:
        raise HTTPException(422, detail="Role and years of experience are required.")
    message = f"score this resume for the role: {role}"
    filename = str(uuid.uuid4()) + file.filename
    file_location = await save_upload_file(file, filename=filename)

    response = agent.invoke({
        "messages": [HumanMessage(content=message)],
        "purpose": "score",
        "file_path": file_location,
        "file_extension": suffix,
        "filename": filename,
        "role": role,
        "years_of_experience": yoe,
        "job_description": job_description
    },config=RunnableConfig(configurable={"thread_id": str(uuid.uuid4())}))

    if "error" in response:
        error_message = response.get("messages", [AIMessage("An error occurred.")])[-1].content
        print(response["error"])
        return Response(content=error_message, media_type="text/plain", status_code=500)

    return JSONResponse(
        content={
            "parsed_resume_data": response.get("parsed_resume_data"),
            "response": response.get("messages", [AIMessage("No response available.")])[-1].content,
        },
        status_code=200,
        media_type="application/json"
    )
    
    
    
 
