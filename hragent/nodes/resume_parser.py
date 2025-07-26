from pathlib import Path
from hragent.agent_state import AgentState, ResumeParsedData
from ..utils.filereader import read_document_content
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from hragent.utils.llm_builder import build_llm
import json
import dotenv
dotenv.load_dotenv()

llm = build_llm("gemini-2.5-flash")
def parse_and_extract_resume(state: AgentState):
    print("--- PARSING RESUME NODE ---")
    file = state["file_path"]
    
    if not file:
        return {"error": "No resume file path provided.", "messages": [AIMessage("No resume file was uploaded.")],"next_action": "end"}

    raw_text: str  = read_document_content(file,file_extension=state.get("file_extension", "pdf"), filename=state.get("filename", "resume"))

    if raw_text.startswith("Error:"):
        return {"error": raw_text, "messages": [AIMessage(f"Failed to parse resume: {raw_text}")],"next_action": "end"}
    


    structuring_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume parser. Extract the following sections from the resume text provided:
        - Experience (job titles, companies, dates, responsibilities/achievements)
        - Education (degrees, institutions, dates)
        - Skills (technical, soft skills, languages)
        - Contact Information (email, phone, LinkedIn - if present, but do NOT make up or share real personal info)
        - Summary/Objective
        
        Provide the output as a JSON string with these keys. If a section is not found, an empty list or string.
        Also, provide a one-sentence summary of the resume's core focus and a list of key keywords.
        Example JSON structure:
        {{
            "sections": {{
                "Experience": [...],
                "Education": [...],
                "Skills": [...]
                "Contact Information": {{...}}
            }},
            "summary": "...",
            "keywords": ["...", "..."]
        }}
        """),
        ("user", "Resume Text:\n{resume_text}")
    ])
    
    structuring_chain = structuring_prompt | llm
    
    try:
        llm_output_str = structuring_chain.invoke({"resume_text": raw_text}).content
        # Attempt to parse the LLM's output as JSON
        structured_data = json.loads(llm_output_str.strip().replace("```json", "").replace("```", "").strip())

        parsed_data: ResumeParsedData = {
            "full_text": raw_text,
            "sections": structured_data.get("sections"),
            "keywords": structured_data.get("keywords"),
            "summary": structured_data.get("summary")
        }
                
        return {
            "parsed_resume_data": parsed_data,
            "next_action": "score_resume",
        }
    
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse LLM's structured output from resume: {e}. Raw LLM output: {llm_output_str[:500]}..."
        return {"error": error_msg, "messages": [AIMessage("I had trouble understanding the resume content. Can you try a different file or format?")], "next_action": "end"}
    except Exception as e:
        error_msg = f"An unexpected error occurred during resume structuring: {e}"
        print(error_msg)
        return {"error": error_msg, "messages": [AIMessage("An unexpected error occurred while processing your resume.")], "next_action": "end"}