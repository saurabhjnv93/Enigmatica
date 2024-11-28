import psycopg2
import pandas as pd
import numpy as np
class database():
    def convertList(self,emb):
        a = emb.strip("'[")
        a = a.strip("]'")
        pr = a.split()
        lst = []
        for i in pr:
            
            lst.append(float(i))
        return str(lst)
    def connect_to_db(self):
        """
        Establish a connection to the PostgreSQL database and return the connection and cursor.

        Returns:
        conn (psycopg2.extensions.connection): The database connection.
        cursor (psycopg2.extensions.cursor): The database cursor.
        """
        try:
            # PostgreSQL configuration
            DATABASE_CONFIG = {
                "host": "localhost",
                "database": "mydatabase",
                "user": "postgres",
                "password": "Saurabh@1"
            }

            # Connect to the PostgreSQL database
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()

            return conn, cursor

        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None, None
    


    def create_table_and_insert_data(self, df):
        """
        Create the 'AI_ML_Data' table if it doesn't exist and insert data from the given DataFrame.

        Args:
        df (pandas.DataFrame): DataFrame containing columns 'paragraph' and 'embedding' (as vectors).
        """
        
        try:
            # Connect to the database
            conn, cursor = self.connect_to_db()
            if conn is None:
                return  # If connection fails, exit the method

            # SQL to create the table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS AI_ML_Data (
                paragraph TEXT NOT NULL,
                embedding vector(384) NOT NULL
);
            """
            cursor.execute(create_table_query)

            # SQL to insert data into the table
            insert_query = """
            INSERT INTO AI_ML_DATA (paragraph, embedding)
            VALUES (%s, %s);
            """
            
            # Iterate through the DataFrame and insert data
            for _, row in df.iterrows():
                embedding_vector = row["embedding"]  # Assuming it's a numpy array or list
                vect = self.convertList(str(embedding_vector))
                
                cursor.execute(insert_query, (row["paragraph"], vect))

            # Commit changes
            conn.commit()
            print("Data inserted successfully.")

            # Close the connection
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error creating table or inserting data: {e}")

    def fetch_data(self, lst):
        """
        Fetch data from the 'AI_ML_Data' table and return it as a pandas DataFrame.

        Parameters:
        ques_emb (list or array): Input vector for similarity comparison.

        Returns:
        list: List of rows containing columns 'paragraph' and 'cosine_similarity'.
        """
        try:
            # Connect to the database
            conn, cursor = self.connect_to_db()
            if conn is None:
                return None  # If connection fails, return None

            # Assuming `lst` is a Python list like [3, 1, 2]
            select_query = """
                SELECT paragraph, 
                    1 - (embedding <=> %s::VECTOR) AS cosine_similarity
                FROM AI_ML_Data
                ORDER BY cosine_similarity DESC
                LIMIT 5;
            """

            # Convert Python list to a PostgreSQL-compatible array string
            vector_str = f"[{', '.join(map(str, lst))}]"  # Convert list [3, 1, 2] to "[3, 1, 2]"
            # Pass the vector string as a parameter
            cursor.execute(select_query, (vector_str,))


            # Fetch all rows from the result of the query
            rows = cursor.fetchall()
            ans = ''
            for i in rows:
                ans = ans+i[0]
            ans = ans.replace("\n"," ")
            return ans
        except Exception as e:
            print(e)
            print(f"Error fetching data from the database: {e}")
        return None
