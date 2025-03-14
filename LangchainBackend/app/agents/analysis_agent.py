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
        self.data_analysis_prompt = """You are Octopus, a data analysis assistant. Analyze the provided data and give DIRECT ANSWERS to the user's question.

ANALYSIS INSTRUCTIONS:
1. Identify the specific analysis requested (max/min, first/last, average, trends, schema details, etc.)
2. Extract relevant data points from the provided dataset
3. Perform calculations accurately (sums, averages, comparisons, etc.)
4. Present findings directly without questions or suggestions
5. Format numerical results clearly with appropriate units

HANDLE THESE ANALYSIS TYPES:
- MAX/HIGHEST: Find maximum values in specified fields
- MIN/LOWEST: Find minimum values in specified fields
- FIRST/EARLIEST: Return chronologically first entries
- LAST/RECENT: Return chronologically last entries
- AVERAGE/MEAN: Calculate averages of specified fields
- TRENDS: Identify patterns or changes over time
- COMPARE: Analyze differences between specified values
- COUNT/TOTAL: Calculate exact counts or sums
- OUTLIERS: Identify statistically significant deviations
- SCHEMA/STRUCTURE: Analyze and describe the data structure in detail

WHEN ANALYZING SCHEMA/STRUCTURE:
- List all fields/keys present in the collection documents
- Identify the data type of each field (string, number, boolean, array, object, etc.)
- Describe nested structures if present
- Highlight required vs optional fields if determinable
- Provide examples of data formats for complex fields
- Format the schema information in a clear, structured way

RESPONSE FORMAT:
1. Direct answer with specific values first
2. Brief explanation of findings (1-2 sentences)
3. Use bullet points for multiple data points
4. Include exact numbers with appropriate precision
5. For schema analysis, use a structured format with field names, types, and examples

NEVER ask follow-up questions or make suggestions. Always provide a complete, direct answer.
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
            # Format the data for analysis - optimize for Ollama 3
            data_str = self._prepare_data_for_analysis(db_data, user_message)
            
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
    
    def _prepare_data_for_analysis(self, db_data: Dict[str, Any], user_message: str) -> str:
        """
        Prepare and optimize data for analysis based on the user's query.
        
        Args:
            db_data: Dictionary with database data
            user_message: The user's message/question
            
        Returns:
            Formatted data string optimized for the analysis
        """
        # Check if we need to limit data size for efficiency
        if "data" in db_data and isinstance(db_data["data"], list) and len(db_data["data"]) > 50:
            # For large datasets, we might want to sample or summarize
            # But first check if user is asking for specific analysis that needs all data
            
            # Keywords that might indicate need for full dataset analysis
            full_data_keywords = ["all", "every", "each", "complete", "entire", "total"]
            needs_full_data = any(keyword in user_message.lower() for keyword in full_data_keywords)
            
            # Analysis types that typically need the full dataset
            if any(term in user_message.lower() for term in ["average", "mean", "trend", "pattern", "outlier"]):
                needs_full_data = True
                
            # If we don't need full data and it's a large dataset, sample it
            if not needs_full_data and len(db_data["data"]) > 100:
                # Keep first and last 25 items for context
                sampled_data = db_data["data"][:25] + db_data["data"][-25:]
                db_data["data"] = sampled_data
                db_data["note"] = f"Data sampled from {len(db_data['data'])} records for efficiency."
        
        # Detect specific analysis types from user message
        analysis_type = self._detect_analysis_type(user_message)
        
        # Add metadata to help the model understand the data structure
        if "data" in db_data and isinstance(db_data["data"], list) and len(db_data["data"]) > 0:
            # Add data structure info
            sample_item = db_data["data"][0]
            if isinstance(sample_item, dict):
                db_data["structure"] = {
                    "fields": list(sample_item.keys()),
                    "count": len(db_data["data"]),
                    "analysis_type": analysis_type
                }
        
        # Convert to string with appropriate formatting
        return json.dumps(db_data, indent=2, default=str)
    
    def _detect_analysis_type(self, user_message: str) -> str:
        """
        Detect the type of analysis requested in the user message.
        
        Args:
            user_message: The user's message/question
            
        Returns:
            The detected analysis type
        """
        user_message = user_message.lower()
        
        if any(term in user_message for term in ["highest", "maximum", "max", "top", "largest"]):
            return "maximum"
        elif any(term in user_message for term in ["lowest", "minimum", "min", "bottom", "smallest"]):
            return "minimum"
        elif any(term in user_message for term in ["first", "earliest", "initial", "beginning"]):
            return "first"
        elif any(term in user_message for term in ["last", "latest", "most recent", "newest"]):
            return "last"
        elif any(term in user_message for term in ["average", "mean", "typical"]):
            return "average"
        elif any(term in user_message for term in ["trend", "pattern", "over time", "change"]):
            return "trend"
        elif any(term in user_message for term in ["compare", "difference", "versus", "vs"]):
            return "comparison"
        elif any(term in user_message for term in ["count", "total", "sum", "how many"]):
            return "count"
        elif any(term in user_message for term in ["outlier", "anomaly", "unusual", "abnormal"]):
            return "outlier"
        elif any(term in user_message for term in ["schema", "structure", "fields", "keys", "data types", "format"]):
            return "schema"
        else:
            return "general"
    
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