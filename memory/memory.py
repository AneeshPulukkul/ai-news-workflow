"""
Memory module for the Agentic News Workflow System
Provides memory implementations for agent conversations
"""

from typing import Dict, List, Any, Optional, Union
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory
)
from langchain_openai import ChatOpenAI

class NewsWorkflowMemory:
    """Memory factory for the news workflow agents"""
    
    @staticmethod
    def get_buffer_memory(memory_key: str = "chat_history") -> ConversationBufferMemory:
        """
        Get a simple buffer memory that stores all conversation
        
        Args:
            memory_key: Key to store the memory under
            
        Returns:
            ConversationBufferMemory instance
        """
        return ConversationBufferMemory(memory_key=memory_key)
    
    @staticmethod
    def get_window_memory(k: int = 5, memory_key: str = "chat_history") -> ConversationBufferWindowMemory:
        """
        Get a window memory that stores only the last k interactions
        
        Args:
            k: Number of interactions to remember
            memory_key: Key to store the memory under
            
        Returns:
            ConversationBufferWindowMemory instance
        """
        return ConversationBufferWindowMemory(k=k, memory_key=memory_key)
    
    @staticmethod
    def get_summary_memory(
        llm_model: str = "gpt-3.5-turbo",
        memory_key: str = "chat_history"
    ) -> ConversationSummaryMemory:
        """
        Get a summary memory that summarizes the conversation
        
        Args:
            llm_model: Model to use for summarization
            memory_key: Key to store the memory under
            
        Returns:
            ConversationSummaryMemory instance
        """
        llm = ChatOpenAI(model_name=llm_model, temperature=0)
        return ConversationSummaryMemory(llm=llm, memory_key=memory_key)
