from typing import Dict, Any, List, Optional
import json
import re

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
        self.data_analysis_prompt = """Hi! I'm Octopus, an AI assistant created by DQ to help with data analysis.
Your task is to analyze this data and provide DIRECT, STRAIGHT ANSWERS based on the user's question.

IMPORTANT INSTRUCTIONS:
1. Understand what the user is asking about this data
2. Analyze the provided data to find relevant information
3. Present your findings in a clear, concise manner
4. NEVER ask follow-up questions - only provide direct answers and insights
5. If the user's intent is unclear, make your best interpretation and provide relevant information
6. ALWAYS provide a straight answer, even if you're uncertain
7. DO NOT use phrases like "Would you like me to..." or "Do you want me to..."
8. DO NOT suggest additional analyses or ask for clarification

Remember to focus on the specific aspects of the data that the user is interested in and ALWAYS provide a direct, straight answer.
dont ask follow up questions
"""
        
        # Create a data analysis prompt template
        self.analysis_prompt_template = PromptTemplate(
            input_variables=["data", "question"],
            template=f"{self.data_analysis_prompt}\n\nUser Question: {{question}}\n\nDatabase Data: {{data}}\n\nDirect Analysis:"
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
                
                # If the user is asking about collections, provide a helpful response
                if "collection" in user_message.lower() or "collections" in user_message.lower():
                    return f"The database contains the following collections: {collections_str}."
                
                # Provide information about collections without asking a question
                return f"Based on your query, the database contains these collections: {collections_str}. You can access specific data by mentioning a collection name."
            
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
                
                # Process the response to remove questions and questioning phrases
                analysis = self.remove_questions_and_suggestions(analysis)
                
                return analysis
            
            # Fallback for other data formats
            analysis_input = self.analysis_prompt_template.format(
                question=user_message,
                data=data_str
            )
            
            # Get analysis from the LLM
            analysis = self.llm.invoke(analysis_input)
            
            # Process the response to remove questions and questioning phrases
            analysis = self.remove_questions_and_suggestions(analysis)
            
            return analysis
            
        except Exception as analysis_error:
            print(f"Analysis error: {str(analysis_error)}")
            return "I encountered an error while analyzing the data. The analysis shows the data is incomplete or unavailable."
    
    def remove_questions_and_suggestions(self, text: str) -> str:
        """
        Remove questions and suggestion phrases from the text.
        
        Args:
            text: The text to process
            
        Returns:
            Processed text without questions or suggestions
        """
        # Remove sentences with question marks
        if "?" in text:
            sentences = re.split(r'(?<=[.!])\s+', text)
            filtered_sentences = [s for s in sentences if "?" not in s]
            text = " ".join(filtered_sentences)
        
        # Remove suggestion phrases
        suggestion_patterns = [
            r"Would you like .*?[.!]",
            r"Do you want .*?[.!]",
            r"If you'd like .*?[.!]",
            r"If you need .*?[.!]",
            r"Let me know if .*?[.!]",
            r"Please let me know .*?[.!]",
            r"I can help you .*?[.!]",
            r"I can provide .*?[.!]",
            r"I can analyze .*?[.!]",
            r"I can further .*?[.!]",
            r"For more information .*?[.!]",
            r"To learn more .*?[.!]"
        ]
        
        for pattern in suggestion_patterns:
            text = re.sub(pattern, "", text)
        
        # Clean up any double spaces and ensure proper ending
        text = re.sub(r'\s+', ' ', text).strip()
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text 