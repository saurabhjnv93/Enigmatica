from flask import Flask, request, jsonify, render_template
import psycopg2
import pandas as pd
from PDFTextProcessor import PDFTextProcessor
from AnsweringClass import AnsweringClass

from database import database
import numpy as np
import os

app = Flask(__name__)


# Initialize objects
ans = AnsweringClass()
myDb = database()
myDb.connect_to_db()
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

            # Append the data from this book to the overall DataFrame
            all_books_df = pd.concat([all_book
                                      
                                      
                                      s_df, df], ignore_index=True)
            all_books_df.to_csv("Enigmatica/all_books_paragraphs.csv")

            # Mark the PDF as processed by adding its name to the processed_files.txt
            with open(processed_file_path, 'a') as file:
                file.write(f"{file_name}\n")
    all_books_df = pd.read_csv("Enigmatica/all_books_paragraphs.csv")
    # Insert the data into the database
    myDb.create_table_and_insert_data(all_books_df)

    return render_template("index.html")

# Endpoint to process PDF and store data in the database
@app.route("/search_query", methods=["POST","GET"])
def process_pdf():
    # Step 1: Extract and clean text
    question = request.form.get("question")
    # df = myDb.fetch_data()

    quesEmb = ans.get_sentence_embedding(question)
    lst = [float(i) for i in quesEmb]

    answer = myDb.fetch_data(lst)
    
    
    return render_template("index.html",ansHtml = answer)
        
    
if __name__ == "__main__":
    app.run(debug=True)
