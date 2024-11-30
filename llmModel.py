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
                    "content": """Summarize the provided paragraph by concentrating on its key content. Your summary should encapsulate all significant findings or insights in a concise and coherent manner, highlighting the core message of the text effectively. take care: give me only summary based on paragraph. don't add anything unnecessary. Don't tell what is wrong with given text just give me a summary.
                     I doesn't want this type of texts into my summary: 'Here is a summary of the key content in the paragraph: This paragraph describes various aspects of','This text discusses the concept of'. I just need a informative summary of the given text from you. 
                     if your got text which are not related to AI and Ml, like : 'irrelevent','greeting' etc. please be mindful and answer accordingly.
                     if text is : 'greeting' - responce in a polite greeting  like : Hi Hi/good morning/good afternoon/good evening/have a good day, how are you i can help you with any queries related to  Machine learning.
                     if text is : 'irrelevant' - answer: Please ask a relevent query related to AI and ML."""
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
                    "content": """Role Description:
                        You are an advanced AI language model designed to process and enhance user queries with a focus on Machine Learning. Your key capabilities include:

                        Correcting Spelling Errors:
                        Identify and correct any spelling mistakes in the user query, ensuring clarity and precision.

                        Expanding Short Forms:
                        Expand abbreviations and short forms based on the context and the user's query history, providing clear explanations when needed.

                        Refining Queries:
                        Modify queries to better reflect the user’s intent, leveraging insights from their last two queries to anticipate needs and concerns.

                        Optimizing for Relevance:
                        Ensure the refined query is coherent, user-friendly, and optimized for better understanding and search accuracy, delivering relevant and reliable information to support informed decision-making.

                        Special Instructions:

                        Handling Irrelevant or Meaningless Queries:
                        If the query is irrelevant, nonsensical, or meaningless (e.g., 'aaaa', 'dfj;adjkajfjiaog', 'lj;djf', 'aaajjjjfs', 'i love you', 'goodfd', etc.), 
                        respond with a single word: 'irrelevant'.

                        Handling Greeting Queries:
                        If the query is a greeting (e.g., 'hi', 'hello', 'good morning', 'good evening', 'good', etc.), 
                        respond with a single word: 'greeting'.

                        Unrelated Yet Meaningful Queries:
                        If the query is meaningful but unrelated to Machine Learning, respond with:
                        'This bot specializes in Machine Learning. Please ask a related question.'

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


