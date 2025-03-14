from typing import Dict, Any, List, Optional
import json

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

class AnalysisAgent:
    """
    Agent responsible for analyzing data from the database and providing insights.
    """
    
    def __init__(self, llm: Ollama):
        """
        Initialize the analysis agent.
        
        Args:
            llm: The language model to use for data analysis
        """
        self.llm = llm
        
        # Define data analysis prompt
        self.data_analysis_prompt = """Hi! I'm Monkey, an AI assistant created by DQ to help with data analysis questions.
Your task is to analyze this data and provide insights based on the user's question.

The data has been retrieved from the database based on the user's query. Now you need to:
1. Understand what the user is asking about this data
2. Analyze the provided data to find relevant information
3. Present your findings in a clear, concise manner
4. If appropriate, suggest further queries or analyses that might be helpful

Remember to focus on the specific aspects of the data that the user is interested in.
"""
        
        # Create a data analysis prompt template
        self.analysis_prompt_template = PromptTemplate(
            input_variables=["data", "question"],
            template=f"{self.data_analysis_prompt}\n\nUser Question: {{question}}\n\nDatabase Data: {{data}}\n\nAnalysis:"
        )
    
    def analyze_data(self, user_message: str, db_data: Dict[str, Any]) -> str:
        """
        Analyze database data and provide insights based on the user's question.
        
        Args:
            user_message: The user's message/question
            db_data: Dictionary with database data
            
        Returns:
            Analysis of the data
        """
        try:
            # Format the data for analysis
            data_str = json.dumps(db_data, indent=2, default=str)
            
            # Check if there's an error in the data
            if "error" in db_data:
                return f"I couldn't analyze the data because: {db_data['error']}"
            
            # Check if we have collection data
            if "collections" in db_data:
                collections = db_data["collections"]
                if not collections:
                    return "The database doesn't have any collections yet."
                
                # Format collections for the prompt
                collections_str = ", ".join(collections)
                analysis_input = f"The database has the following collections: {collections_str}. What collection would you like to query?"
                
                # If the user is asking about collections, provide a helpful response
                if "collection" in user_message.lower() or "collections" in user_message.lower():
                    return f"The database contains the following collections: {collections_str}. You can ask questions about any of these collections."
                
                return analysis_input
            
            # Check if we have data from a specific collection
            if "collection" in db_data and "data" in db_data:
                collection_name = db_data["collection"]
                data = db_data["data"]
                
                if not data:
                    return f"The collection '{collection_name}' doesn't have any documents yet."
                
                # Generate the analysis using the prompt template
                analysis_input = self.analysis_prompt_template.format(
                    question=user_message,
                    data=data_str
                )
                
                # Get analysis from the LLM
                analysis = self.llm.invoke(analysis_input)
                return analysis
            
            # Fallback for other data formats
            analysis_input = self.analysis_prompt_template.format(
                question=user_message,
                data=data_str
            )
            
            # Get analysis from the LLM
            analysis = self.llm.invoke(analysis_input)
            return analysis
            
        except Exception as analysis_error:
            print(f"Analysis error: {str(analysis_error)}")
            return "I encountered an error while analyzing the data. Please try a different question." 