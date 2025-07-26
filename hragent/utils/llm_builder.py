import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode


# -- util file to load LLM and search tools for the agent --

# Load environment variables like GOOGLE_API_KEY from .env file
dotenv.load_dotenv()


search = TavilySearch(
        api_key=dotenv.get_key(dotenv.find_dotenv(), "TAVILY_API_KEY"),
        max_results=10,
)
tools = [search]

def build_llm(llm_name: str = "gemini-2.5-flash") -> ChatGoogleGenerativeAI:
    """
    Builds and returns a configured LLM instance.
    """
    
    llm = ChatGoogleGenerativeAI(model=llm_name)
    llm = llm.bind_tools(tools=tools)
    return llm
   

tool_node = ToolNode(
    name="search tools",
    tools=[search],
)




