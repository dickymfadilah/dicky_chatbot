from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

class GeneralAgent:
    """
    Agent responsible for handling general (non-database) questions.
    """
    
    def __init__(self, llm: Ollama, memory: ConversationBufferMemory = None):
        """
        Initialize the general agent.
        
        Args:
            llm: The language model to use for answering questions
            memory: Optional conversation memory to maintain context
        """
        self.llm = llm
        self.memory = memory if memory else ConversationBufferMemory(return_messages=True)
        
        # Define system prompt for general questions
        self.system_prompt = """Hi! I'm Elephant, an AI assistant created by DQ to help with general questions.
Your task is to provide helpful, accurate, and concise responses to user queries.

You should:
- Answer questions based on your knowledge
- Provide explanations when necessary
- Be conversational and friendly
- Admit when you don't know something

Think step by step to determine the best way to respond to the user's query.
"""
        
        # Create a custom prompt template for the conversation chain
        self.conversation_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=f"{self.system_prompt}\n\nConversation History:\n{{history}}\nHuman: {{input}}\nAI:"
        )
        
        # Initialize a regular conversation chain with the custom prompt
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.conversation_prompt,
            verbose=True
        )
    
    def answer_question(self, user_message: str) -> str:
        """
        Answer a general question from the user.
        
        Args:
            user_message: The user's message/question
            
        Returns:
            The agent's response
        """
        response = self.conversation.predict(input=user_message)
        return response 