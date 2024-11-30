from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import psycopg2
import pandas as pd
from PDFTextProcessor import PDFTextProcessor
from AnsweringClass import AnsweringClass
from llmModel import *

from database import database
import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Initialize objects
ans = AnsweringClass()
myDb = database()
llm = llmModel()
myDb.connect_to_db()
cache = {}  # In-memory cache for questions and answers


@app.route("/")
def home():
    books_dir = "/home/saurabh/Desktop/Enigmatica /books"
    processed_file_path = os.path.join(os.getcwd(), 'processed_files.txt')  # Path for the processed files record

    # Load the list of already processed PDF files (if the file exists)
    if os.path.exists(processed_file_path):
        with open(processed_file_path, 'r') as file:
            processed_files = set(file.read().splitlines())  # Read the lines and store in a set for quick lookup
    else:
        processed_files = set()

    all_books_df = pd.DataFrame()

    # Iterate over all files in the directory
    for file_name in os.listdir(books_dir):
        if file_name.endswith(".pdf") and file_name not in processed_files:  # Process only PDFs that have not been processed
            pdf_path = os.path.join(books_dir, file_name)
            base_name = os.path.splitext(file_name)[0]  # Get the base name without extension
            
            # Define file paths for output and cleaned text
            output_txt_path = "output_text.txt"
            cleaned_txt_path = "cleaned_text.txt"

            # Initialize PDFTextProcessor for each book
            processor = PDFTextProcessor(
                pdf_path=pdf_path,
                output_txt_path=output_txt_path,
                cleaned_txt_path=cleaned_txt_path
            )

            # Step 1: Extract and clean text from the PDF
            processor.extract_text()
            processor.clean_text_file()

            # Step 2: Process the cleaned text into paragraphs and create a DataFrame
            df = processor.process_text_to_dataframe(cleaned_txt_path, output_csv_path="paragraphs.csv")
        
            # Step 3: Add embeddings for the paragraphs
            df["embedding"] = df["paragraph"].apply(lambda x: ans.get_sentence_embedding(x))
            myDb.create_table_and_insert_data(df)

            # # Append the data from this book to the overall DataFrame
            all_books_df = pd.concat([all_books_df, df], ignore_index=True)
            
            # Mark the PDF as processed by adding its name to the processed_files.txt
            with open(processed_file_path, 'a') as file:
                file.write(f"{file_name}\n")
  
    all_books_df.to_csv("Enigmatica/all_books_paragraphs.csv")

    if 'conversation' not in session:
        session['conversation'] = []
    return render_template("index1.html", conversation=session['conversation'])


    

# Endpoint to process PDF and store data in the database
@app.route("/search_query", methods=["POST","GET"])
def process_pdf():
    # Step 1: Extract and clean text
    question = request.form.get("question")
    try:
        processed_question = llm.queryPrecessing(question)
    except:
        processed_question = question
    # Check cache
    if question in cache:
        summarized_answer = cache[question]
    else:
        if processed_question in ['irrelevant','greeting']:
            raw_answer = processed_question
        else:
        # Generate embedding for the question
            ques_emb = ans.get_sentence_embedding(processed_question)
            lst = [float(i) for i in ques_emb]

            
        try:
            # Fetch data from the database and summarize
            raw_answer = myDb.fetch_data(lst,10)
            summarized_answer = llm.summerise(raw_answer)
        except:
            
            summarized_answer = myDb.fetch_data(lst,3)
        # Cache the answer
        cache[question] = summarized_answer

    # Update conversation in session
    conversation = session.get('conversation', [])
    conversation.append({'user': question, 'bot': summarized_answer})
    session['conversation'] = conversation

    return render_template("index1.html", conversation=conversation)
@app.route("/submit_review", methods=["POST"])
def submit_review():
    """
    Handles user reviews of answers and stores them in the database.
    """
    rating = request.form.get("rating", 2)  # Default rating is 2
    query = request.form.get("query", "")
    answer = request.form.get("answer", "")

    try:
        rating = int(rating)
        store_review_data(rating, query, answer)
    except ValueError:
        pass  # Handle invalid ratings gracefully

    return redirect(url_for("home"))


def store_review_data(rating, query, answer):
    """
    Stores review data in either `good_data` or `bad_data` tables based on the rating.
    """
    try:
        connection,cursor = myDb.connect_to_db()

        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bad_data (
                id SERIAL PRIMARY KEY,
                rating INT NOT NULL,
                query TEXT NOT NULL,
                answer TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS good_data (
                id SERIAL PRIMARY KEY,
                rating INT NOT NULL,
                query TEXT NOT NULL,
                answer TEXT NOT NULL
            );
        """)

        # Insert into appropriate table
        if rating in [1, 2, 3]:
            cursor.execute("INSERT INTO bad_data (rating, query, answer) VALUES (%s, %s, %s)", (rating, query, answer))
        elif rating in [4, 5]:
            cursor.execute("INSERT INTO good_data (rating, query, answer) VALUES (%s, %s, %s)", (rating, query, answer))
        else:
            raise ValueError("Rating must be between 1 and 5.")
        cursor.close()
        connection.commit()
    except Exception as e:
        print(f"Error storing review data: {e}")
    finally:
        cursor.close()
        connection.close()

    
if __name__ == "__main__":
    app.run(debug=True)
