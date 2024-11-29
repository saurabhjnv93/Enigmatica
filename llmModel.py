from groq import Groq
import os
# Set the API key for Groq (using the correct environment variable name)
os.environ["GROQ_API_KEY"] = "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"
# Initialize the client
client = Groq()

class llmModel:
    def summerise(self,input_text):
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """Summarize the provided paragraph by concentrating on its key content. Your summary should encapsulate all significant findings or insights in a concise and coherent manner, highlighting the core message of the text effectively. take care: give me only summary based on paragraph. don't add anything unnecessary. Don't tell what is wrong with given text just give me a summary."""
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,  # Disable streaming for simple output
            stop=None,
        )
        
        # Extract and return the summary
        return completion.choices[0].message.content

    def queryPrecessing(self,query):
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are an advanced language model designed to process and enhance user queries, leveraging your vast knowledge and context-aware capabilities. Your task is to:

                                    Correct Spelling Errors: Identify and rectify any spelling mistakes in the provided query, ensuring accuracy and precision.
                                    Expand Short Forms: Expand abbreviations and short forms based on contextual meaning and user search history, providing clear and concise explanations.
                                    Modify the Query: Refine the query to align with the intent or pattern inferred from the user's last two queries, anticipating their needs and concerns.
                                    Ensure the output is coherent, user-friendly, and optimised for improved understanding and search accuracy, providing relevant and reliable information to facilitate informed decision-making.
                                    ALL THE QUESTION ARE RELATED TO MACHINE LEARNING
                                    """
                    
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,  # Disable streaming for simple output
            stop=None,
        )
        
        # Extract and return the summary
        return completion.choices[0].message.content


