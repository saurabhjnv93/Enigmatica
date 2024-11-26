import psycopg2
import pandas as pd

class database():

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
        Create the 'rawBookData' table if it doesn't exist and insert data from the given DataFrame.

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
            CREATE TABLE IF NOT EXISTS rawBookData (
                paragraph_number SERIAL PRIMARY KEY,
                paragraph TEXT NOT NULL,
                embedding VECTOR(384));
            """
            cursor.execute(create_table_query)

            # SQL to insert data into the table
            insert_query = """
            INSERT INTO rawBookData (paragraph, embedding)
            VALUES (%s, %s)
            ON CONFLICT (paragraph) DO NOTHING;
            """

            # Iterate through the DataFrame and insert data
            for _, row in df.iterrows():
                embedding_vector = row["embedding"]  # Assuming it's a list or numpy array
                embedding_str = f"{{{', '.join(map(str, embedding_vector))}}}"  # Convert to PostgreSQL array format
                cursor.execute(insert_query, (row["paragraph"], embedding_str))

            # Commit changes
            conn.commit()
            print("Data inserted successfully.")

            # Close the connection
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error creating table or inserting data: {e}")
    
    def fetch_data(self):
        """
        Fetch data from the 'rawBookData' table and return it as a pandas DataFrame.

        Returns:
        pandas.DataFrame: DataFrame containing columns 'paragraph_number', 'paragraph', and 'embedding'.
        """
        try:
            # Connect to the database
            conn, cursor = self.connect_to_db()
            if conn is None:
                return None  # If connection fails, return None

            # SQL to fetch data from the table
            select_query = "SELECT paragraph_number, paragraph, embedding FROM rawBookData;"

            # Execute the query
            cursor.execute(select_query)

            # Fetch all rows from the result of the query
            rows = cursor.fetchall()

            # Convert the fetched rows into a pandas DataFrame
            df = pd.DataFrame(rows, columns=["paragraph_number", "paragraph", "embedding"])

            # Close the connection
            cursor.close()
            conn.close()

            return df

        except Exception as e:
            print(f"Error fetching data from the database: {e}")
            return None
