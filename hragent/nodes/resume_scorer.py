from datetime import date
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate
from hragent.utils.llm_builder import build_llm
from langchain_tavily import TavilySearch
from hragent.agent_state import AgentState
import dotenv
dotenv.load_dotenv()

llm = build_llm("gemini-2.5-flash")

def resume_scorer(state: AgentState):
    print("--- SCORING RESUME NODE ---")
    
    
    parsed_data = state.get("parsed_resume_data")
    role = state.get("role", "job seeker")
    if not parsed_data:
        return {"error": "No parsed resume data available.", "messages": [AIMessage("No resume data to score. Please parse a resume first.")], "next_action": "end"}
  

    resume_review_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a top-tier HR professional and AI-powered career strategist specializing in resume evaluation, keyword optimization, and ATS (Applicant Tracking System) alignment.\n\n"
                "You have access to a **search tool** called **search tools** that lets you find role descriptions, industry benchmarks, and keyword standards to inform your analysis. "
                "You may use this tool by sending a response in the format:\n\n"
                "today's date is {date} \n"
                "tool_call search with arguments like description of the role, industry standards, or keywords relevant to the role.\n\n"

                "**Your responsibilities include:**\n"
                "- Scoring resumes for clarity, impact, and alignment with the specified role\n"
                "- Identifying keyword relevance and missing skills for ATS optimization\n"
                "- Providing highly specific, structured improvement suggestions\n\n"

                "### Review Instructions:\n"
                "1. **JSON-only output**: Provide a single, valid JSON object — no markdown, commentary, or text outside the JSON.\n\n"
                "2. **Score (1 to 100)**: Evaluate overall quality and alignment with the target role.\n"
                "   - 1–20: Very Poor — disorganized, irrelevant\n"
                "   - 21–40: Poor — weak impact and clarity\n"
                "   - 41–60: Fair — basic baseline, partially relevant\n"
                "   - 61–80: Good — solid content, mostly aligned\n"
                "   - 81–90: Very Good — strong, few improvements needed\n"
                "   - 91–100: Excellent — outstanding, highly optimized\n\n"
                
                "3. **Strengths**: List 3–5 role-specific strengths, including:\n"
                "   - Keyword usage aligned with the job\n"
                "   - Use of quantifiable achievements\n"
                "   - Clean formatting and layout\n"
                "   - Action verbs and measurable results\n"
                "   - Relevant tools, tech stacks, certifications\n\n"

                "4. **Improvements**: Provide 5–7 specific suggestions under these categories:\n"
                "   - **Relevance** — Add/remove keywords, match role terminology\n"
                "   - **ATS optimization** — Improve formatting or structure for parsing\n"
                "   - **Quantifiable impact** — Use metrics to show outcomes\n"
                "   - **Keyword matching** — Align better with job description keywords\n"
                "   - **Clarity & conciseness** — Remove filler phrases or vague content\n"
                "   - **Formatting & readability** — Fix visual layout issues\n"
                "   - **Missing content** — Include certifications, projects, achievements\n"
                "   - **Action verbs** — Replace weak verbs with strong ones\n\n"

                "5. **Bonus Insight (Optional)** — If relevant, point out:\n"
                "   - Gaps in employment or skills\n"
                "   - Inconsistencies in formatting or tense\n\n"

                "### Output JSON schema:\n"
                "{\n"
                '  "score": 0,\n'
                '  "strengths": ["string"],\n'
                '  "improvements": ["string"]\n'
                "}\n\n"

                "**Important**: Do NOT include markdown formatting like ```json. Do NOT include text before or after the JSON. Begin output with a valid JSON object immediately."
            )
        ),
        ("placeholder", "{messages}"),
        (
            "human",
            "**Target Role:** {target_role}\n\n**Resume Content:**\n{resume_text}"
        )
    ]
)
    
    scorer_chain = resume_review_prompt | llm  
   
    return {
        "messages": [scorer_chain.invoke({
        "target_role": role,
        "date":date.today().strftime("%Y-%m-%d"),
        "resume_text": parsed_data.get("full_text", ""),"messages": state.get("messages", [])
    })],
        "next_action": "end",
    }



   