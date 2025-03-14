import json
import re
from typing import Dict, Any

from langchain_community.llms import Ollama

class ClassifierAgent:
    """
    Agent responsible for classifying user queries as database-related or general questions.
    """
    
    def __init__(self, llm: Ollama):
        """
        Initialize the classifier agent.
        
        Args:
            llm: The language model to use for classification
        """
        self.llm = llm
    
    def classify_query(self, user_message: str) -> Dict[str, Any]:
        """
        Classify a user query as database-related or general.
        
        Args:
            user_message: The user's message to classify
            
        Returns:
            Dictionary with classification results:
            {
                "is_database_question": bool,
                "collection": str or None,
                "query_type": str
            }
        """
        # Define the analysis prompt
        analysis_prompt = f"""
        Hi! I'm Lion, an AI assistant created by DQ to help with classification questions.
        
        I'll analyze your message to determine:
        1. Is this a database-related question? (yes/no)
        2. If yes, which collection might it be referring to? (If collection name doesn't end with 's', add 's')
        3. What type of query is needed? (list collections, query documents, get document by id, text search)
        
        IMPORTANT NOTES ABOUT MONGODB COLLECTIONS:
        - MongoDB collection names typically end with 's' (e.g., users, products, orders, transactions)
        - Collections store multiple related documents of the same type
        - Look for plural nouns in the user's message as they likely refer to collections
        - Common collection naming patterns: 
          * Plural nouns (users, products, orders)
          * Entity + action (userLogins, productViews)
          * Domain-specific terms (transactions, analytics, metrics)
        
        User message: "{user_message}"
        
        Provide your analysis in VALID JSON format with the following structure:
        {{
            "is_database_question": true/false,
            "collection": "collection_name_or_null",
            "query_type": "list_collections/query_documents/get_document/text_search"
        }}
                
        DO NOT include comments, explanations, or any non-JSON content in your response.
        Ensure all property names are in double quotes and follow standard JSON format.
        If you detect a potential collection name that doesn't end with 's', add 's' to make it plural.
        """
        
        # Get the analysis response from the LLM
        analysis_response = self.llm.invoke(analysis_prompt)
        
        # Extract JSON from the response if possible
        try:
            # Try to find JSON-like content in the response
            json_match = re.search(r'\{.*\}', analysis_response, re.DOTALL)
            if json_match:
                # Clean up the JSON string to remove comments and ensure valid format
                json_str = json_match.group(0)
                # Replace single quotes with double quotes for JSON compliance
                json_str = json_str.replace("'", '"')
                # Ensure boolean values are lowercase
                json_str = json_str.replace("True", "true").replace("False", "false")
                
                analysis_json = json.loads(json_str)
            else:
                # Fallback: create a simple analysis based on keywords
                is_db_query = any(keyword in user_message.lower() for keyword in 
                    ["database", "mongodb", "collection", "data", "query", "find", "search", "list"])
                
                # Try to extract collection name from the message
                collection_name = None
                words = user_message.lower().split()
                for i, word in enumerate(words):
                    # Look for nouns that might be collections
                    if len(word) > 3 and i > 0:  # Skip short words and first word
                        # Check if it's a potential collection name (not a common verb or preposition)
                        if word not in ["from", "where", "what", "when", "how", "show", "get", "find", "query"]:
                            # Make sure it ends with 's'
                            if not word.endswith('s'):
                                word = word + 's'
                            collection_name = word
                            break
                
                analysis_json = {
                    "is_database_question": is_db_query,
                    "collection": collection_name,
                    "query_type": "list_collections" if "list" in user_message.lower() else "query_documents"
                }
        except Exception as json_error:
            print(f"Error parsing analysis JSON: {str(json_error)}")
            # Fallback analysis
            is_db_query = any(keyword in user_message.lower() for keyword in 
                ["database", "mongodb", "collection", "data", "query", "find", "search", "list"])
            analysis_json = {
                "is_database_question": is_db_query,
                "collection": None,
                "query_type": "list_collections" if "list" in user_message.lower() else "query_documents"
            }
        
        print(f"Classification result: {analysis_json}")
        return analysis_json 