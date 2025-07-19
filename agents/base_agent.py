"""
Base agent class for the Agentic News Workflow System
Defines the foundation for all specialized agents
"""

from typing import Dict, List, Any, Optional, Union
from langchain.agents import AgentExecutor, BaseSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

class BaseNewsAgent:
    """Base class for all specialized news workflow agents"""
    
    def __init__(
        self,
        name: str,
        description: str,
        tools: List[BaseTool],
        llm_model: str = "gpt-3.5-turbo",
        memory: Optional[ConversationBufferMemory] = None,
        verbose: bool = False
    ):
        """Initialize the agent with necessary components"""
        self.name = name
        self.description = description
        self.tools = tools
        self.verbose = verbose
        
        # Initialize LLM
        self.llm = ChatOpenAI(model_name=llm_model, temperature=0.2)
        
        # Initialize memory if not provided
        self.memory = memory or ConversationBufferMemory(memory_key="chat_history")
        
        # Agent will be initialized in subclasses
        self.agent = None
        self.agent_executor = None
    
    def run(self, input_text: str) -> str:
        """Run the agent with the given input"""
        if not self.agent_executor:
            raise ValueError("Agent executor not initialized. Call initialize_agent() first.")
        
        return self.agent_executor.run(input_text)
    
    def initialize_agent(self):
        """Initialize the agent - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement initialize_agent method")
