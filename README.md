# 💼 HR Assist AI

**HR Assist AI** is an intelligent, A agent exposed as API powered by FastAPI,using LangGraph, and Google's Gemini models. It serves as a comprehensive Human Resources agent, providing two key functionalities: advanced resume analysis and interactive career guidance.

This solution is designed to streamline HR workflows and empower both candidates and employees with data-driven insights.

---

## ✨ Features

-   📄 **Multi-Format Resume Parsing**: Seamlessly processes resumes from `.pdf`, `.docx`, and `.txt` files.
-   🎯 **Intelligent Resume Scoring**: Provides a quantitative score and qualitative feedback by analyzing a resume's relevance against a specific job description.
-   💬 **Conversational AI Chat**: Engages in contextual conversations about career growth, interview strategies, HR policies, and more.
-   🧠 **Persistent Memory**: Maintains conversation history using thread IDs for continuous and coherent user interactions.
-   🚀 **Scalable & Modern Stack**: Built with a high-performance, asynchronous framework suitable for demanding applications.

---

## 🛠️ Tech Stack

-   **Backend**: **FastAPI** – A high-performance Python web framework for building robust APIs.
-   **Agent Framework**: **LangGraph** – A declarative state-machine library for building complex, stateful LLM agents.
-   **LLM & Orchestration**: **LangChain** – The core framework for tool routing, data handling, and LLM integration.
-   **AI Model**: **Gemini 2.5 Flash** – Google's fast and powerful multimodal model for reasoning and analysis.
-   **Search**: **Tavily** – For agents that need to access real-time web information.

---

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/mohammedarbaz119/HR-Assist-AI.git
cd hragent
```

### 2\. Create and Activate a Virtual Environment

```bash
# Create the environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
.\venv\Scripts\activate
```

### 3\. Install Dependencies

Install all required packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4\. Configure Environment Variables

Create a `.env` file in the root directory and add your API keys.

```env
GOOGLE_API_KEY="your_google_gemini_api_key"
TAVILY_API_KEY="your_tavily_api_key" 
```

### 5\. Run the Application

Launch the FastAPI server using Uvicorn. The `--reload` flag will automatically restart the server on code changes.

```bash
uvicorn hragent.app:app --reload
```

The API will be available at `http://localhost:8000`. You can access the auto-generated OpenAPI documentation at `http://localhost:8000/docs`.

-----

## 📬 API Endpoints

### ➤ `POST /score-resume`

Analyzes and scores a resume against a target job role.

| Parameter          | Type   | Description                                    |
| :--------          | :----- | :------------------------------------------    |
| `file`             | `file` | The resume file (`.pdf`, `.docx`, or `.txt`).  |
| `role`             | `str`  | The target job title (e.g., "Data Scientist"). |
| `yoe`              | `str`  | years of experience of candidate               | 
| `job_description`  | `str`  | the description of the job to compare with     |

**Example Response:**

```json
{
  "score": "88/100",
  "strengths": "Excellent alignment with key skills such as Python, SQL, and machine learning frameworks. Strong project experience in data visualization.",
  "improvements": "Consider adding more quantifiable results to your project descriptions to demonstrate impact. The summary could be more tailored to the Data Scientist role.",
  "parsed_resume_text": "John Doe\n(123) 456-7890 | john.doe@email.com\n..."
}
```

### ➤ `POST /chat`

Initiates or continues a conversation with the HR Assistant.

| Parameter   | Type   | Description                                                      |
| :---------- | :----- | :--------------------------------------------------------------- |
| `message`   | `str`  | The user's question or message.                                  |
| `thread_id` | `str`  | **(Optional)** The UUID of a previous session to maintain context. |

**Example Response:**

```json
{
  "response": "To prepare for a performance review, I recommend a three-step approach. First, compile a list of your key accomplishments from the past cycle, focusing on quantifiable results. Second, review your job description and goals to assess your performance against expectations. Finally, think about your career aspirations and be prepared to discuss them with your manager.",
  "thread_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
}
```

-----

## 📂 Project Structure

```
hragent/
│
├── hragent.py          # Main application file: FastAPI routes & LangGraph agent logic
├── agent_state.py      # Defines the state schema for the LangGraph agent
├── .env                # Securely stores environment variables (API keys)
├── requirements.txt    # Lists all Python project dependencies
└── README.md           # Project documentation (You are here!)
```

-----

## 🤖 Use Cases

  - **For Candidates**: Get instant feedback on a resume before applying to a job.
  - **For HR Teams**: Pre-screen resumes to identify top candidates more efficiently.
  - **For Employees**: Ask questions about internal mobility, promotion criteria, or performance reviews.
  - **For Managers**: Practice interview questions or get guidance on writing effective job descriptions.

-----

## 📬 Contact

For issues, feature requests, or contributions, please open an issue on the GitHub repository or contact [mohammedarbazq16@gmail.com].
