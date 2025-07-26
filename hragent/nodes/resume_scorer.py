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
    years_of_experience = state.get("years_of_experience", 0)
    job_description = state.get("job_description", "")
    if not parsed_data:
        return {"error": "No parsed resume data available.", "messages": [AIMessage("No resume data to score. Please parse a resume first.")], "next_action": "end"}
  

    resume_review_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
               """
You are a top-tier HR professional and AI-powered career strategist specializing in resume evaluation, keyword optimization, and ATS (Applicant Tracking System) alignment.

provide a detailed, structured analysis of the resume content provided, focusing on scoring, strengths, and specific improvement suggestions tailored to the target role and candidate's experience level.

Today's date is {date}

You have access to a **search tool** called **search tools** that lets you find role descriptions, industry benchmarks, and keyword standards to inform your analysis. You may use this tool by sending a response in the format:

tool_call search with arguments like description of the role, industry standards, or keywords relevant to the role.

**Your responsibilities include:**
- Scoring resumes for clarity, impact, and alignment with the specified role
- Identifying keyword relevance and missing skills for ATS optimization
- Providing highly specific, structured improvement suggestions
- Evaluating candidate experience level against role requirements

### Input Context:
You will receive:
- **Resume text** to evaluate
- **Target role** (e.g., "Software Engineer", "Data Scientist")
- **Years of experience** the candidate has
- **Job description** (may or may not be provided)

**If no job description is provided:** Use your knowledge of the role or search for current industry standards, typical responsibilities, and required skills for that position. Consider the candidate's experience level when setting expectations.

**Experience Level Evaluation:**
- **0-2 years**: Focus on foundational skills, learning ability, relevant projects, internships
- **3-5 years**: Expect solid technical skills, some leadership/mentoring, measurable impact
- **6-10 years**: Look for senior technical expertise, project leadership, strategic thinking
- **10+ years**: Expect architectural decisions, team leadership, business impact, mentoring

### Review Instructions:
1. **JSON-only output**: Provide a single, valid JSON object — no markdown, commentary, or text outside the JSON.

2. **Score (1 to 100)**: Evaluate overall quality and alignment with the target role **considering experience level**.
   - 1–20: Very Poor — disorganized, irrelevant, far below experience expectations
   - 21–40: Poor — weak impact and clarity, below experience level
   - 41–60: Fair — basic baseline, partially relevant, meets minimum experience expectations
   - 61–80: Good — solid content, mostly aligned, appropriate for experience level
   - 81–90: Very Good — strong, few improvements needed, exceeds experience expectations
   - 91–100: Excellent — outstanding, highly optimized, exceptional for experience level

3. **Strengths**: List 3–5 role-specific strengths **relative to experience level**, including:
   - Keyword usage aligned with the job
   - Use of quantifiable achievements appropriate for experience level
   - Clean formatting and layout
   - Action verbs and measurable results
   - Relevant tools, tech stacks, certifications for the role and experience level
   - Leadership/mentoring evidence (for senior levels)
   - Strategic impact (for senior levels)

4. **Improvements**: Provide 5–7 specific suggestions under these categories **tailored to experience level**:
   - **Relevance** — Add/remove keywords, match role terminology for experience level
   - **ATS optimization** — Improve formatting or structure for parsing
   - **Quantifiable impact** — Use metrics appropriate for experience level (projects for junior, business impact for senior)
   - **Keyword matching** — Align better with job description or industry standard keywords
   - **Clarity & conciseness** — Remove filler phrases or vague content
   - **Formatting & readability** — Fix visual layout issues
   - **Missing content** — Include certifications, projects, achievements expected at this experience level
   - **Action verbs** — Replace weak verbs with strong ones appropriate for seniority
   - **Experience alignment** — Address gaps between current level and role expectations

5. **Bonus Insight (Optional)** — If relevant, point out:
   - Gaps in employment or skills relative to experience level
   - Inconsistencies in formatting or tense
   - Over/under-qualification concerns
   - Experience level misalignment with role complexity

### Output JSON schema:
{{
  "score": 0,
  "strengths": ["string"],
  "improvements": ["string"]
}}\n

**Important**: Do NOT include markdown formatting like ```json. Do NOT include text before or after the JSON. Begin output with a valid JSON object immediately.
"""
            )
        ),
        ("placeholder", "{messages}"),
        (
            "human",
            """
**Target Role:** {target_role}

**Years of Experience:** {years_of_experience}

**Job Description:** {job_description}

**Resume Content:**
{resume_text}
"""
        )
    ]
)
    
    scorer_chain = resume_review_prompt | llm  
   
    return {
        "messages": [scorer_chain.invoke({
        "target_role": role,
        "date": date.today().strftime("%Y-%m-%d"),
        "resume_text": parsed_data.get("full_text", ""),"messages": state.get("messages", []),
        "years_of_experience": years_of_experience,
        "job_description": job_description 
    })],
        "next_action": "end",
    }



   