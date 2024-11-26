import inspect
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class AnsweringClass:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the AnsweringClass with a specified sentence transformer model.
        
        Parameters:
            model_name (str): Name of the pre-trained sentence transformer model.
        """
        self.model = SentenceTransformer(model_name)
    
    def get_sentence_embedding(self, sentence):
        """
        Generates a sentence embedding for a given input sentence.
        
        Parameters:
            sentence (str): The input sentence to generate an embedding for.
        
        Returns:
            np.array: A vector representing the embedding of the sentence.
        """
        try:
            return self.model.encode(sentence)
        except Exception as e:
            print(f"An error occurred while generating the embedding: {e}")
            return None
    
    def get_top_matches(self, sentence, df, text_column='paragraph', embedding_column='sent_embd', top_n=5):
        """
        Finds the most similar paragraphs to a given sentence based on vector embeddings.

        Parameters:
            sentence (str): The input sentence to compare.
            df (pd.DataFrame): DataFrame containing text data and embeddings.
            text_column (str): The column name in the DataFrame containing text data.
            embedding_column (str): The column name containing vector embeddings.
            top_n (int): Number of top matches to return.

        Returns:
            list of tuples: List of top matches as (paragraph, similarity_score).
        """
        try:
            # Encode the input sentence to get its embedding
            sentence_embedding = self.get_sentence_embedding(sentence)

            # Ensure embeddings in DataFrame are numpy arrays
            df[embedding_column] = df[embedding_column].apply(lambda x: np.array(x) if isinstance(x, list) else x)

            # Compute cosine similarity between the input sentence and all embeddings in the DataFrame
            similarities = cosine_similarity([sentence_embedding], list(df[embedding_column]))

            # Get the top N matches
            top_indices = np.argsort(similarities[0])[::-1][:top_n]
            top_matches = [
                (df.iloc[i][text_column].replace("\n", " "), similarities[0][i])
                for i in top_indices
            ]

            return top_matches
        except Exception as e:
            print(f"An error occurred while finding top matches: {e}")
            return []


    