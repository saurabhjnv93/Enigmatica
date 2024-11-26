from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import Json
import pandas as pd
from torch import cosine_similarity
from PDFTextProcessor import PDFTextProcessor
from AnsweringClass import AnsweringClass
import numpy as np
import json

app = Flask(__name__)


# Initialize objects
ans = AnsweringClass()
processor = PDFTextProcessor(
    pdf_path="/home/saurabh/Desktop/Enigmatica /books/AI_Russell_Norvig.pdf",
    output_txt_path="output_text_russell.txt",
    cleaned_txt_path="cleaned_text_russell.txt"
)

@app.route("/")
def home():
    return render_template("index.html")

# Endpoint to process PDF and store data in the database
@app.route("/search_query", methods=["POST","GET"])
def process_pdf():
    # Step 1: Extract and clean text
    question = request.form.get("question")

    processor.extract_text()
    processor.clean_text_file()

    # Step 2: Process the cleaned text into paragraphs
    df = processor.process_text_to_dataframe(
        "cleaned_text_russell.txt", output_csv_path="paragraphs.csv"
    )
    
    df["embedding"] = df["paragraph"].apply(lambda x: ans.get_sentence_embedding(x))


    # Generate the embedding for the question
    question_embedding = ans.get_sentence_embedding(question)

    ansList = ans.get_top_matches(question,df,embedding_column="embedding")
    answer = ""
    for tup in ansList:
        answer = answer+tup[0]
    return render_template("index.html",ansHtml = answer)
        
    
if __name__ == "__main__":
    app.run(debug=True)
