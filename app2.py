import os
from flask import Flask, request, render_template
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
from PDFTextProcessor import PDFTextProcessor
from AnsweringClass import AnsweringClass

app = Flask(__name__)

# Directory to watch
BOOKS_DIR = "/home/saurabh/Desktop/Enigmatica/books"

# Verify if the directory exists
if not os.path.exists(BOOKS_DIR):
    print(f"Error: Directory {BOOKS_DIR} does not exist. Creating it now.")
    os.makedirs(BOOKS_DIR)

# Define a processor variable to be updated dynamically
processor = None
ans = AnsweringClass()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search_query", methods=["POST", "GET"])
def process_pdf():
    global processor
    if processor is None:
        return render_template("index.html", ansHtml="No file has been processed yet.")

    question = request.form.get("question")

    # Step 1: Extract and clean text
    processor.extract_text()
    processor.clean_text_file()

    # Step 2: Process the cleaned text into paragraphs
    df = processor.process_text_to_dataframe(
        processor.cleaned_txt_path,
        output_csv_path="paragraphs.csv",
    )
    df["embedding"] = df["paragraph"].apply(lambda x: ans.get_sentence_embedding(x))

    # Generate the embedding for the question
    ansList = ans.get_top_matches(question, df, embedding_column="embedding")
    answer = "".join([tup[0] for tup in ansList])

    return render_template("index.html", ansHtml=answer)


# Watchdog EventHandler for detecting new files
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        global processor
        if not event.is_directory and event.src_path.endswith(".pdf"):
            # Extract the base name of the new file (e.g., "AI_Russell_Norvig.pdf")
            file_name = os.path.basename(event.src_path)
            base_name, _ = os.path.splitext(file_name)

            # Dynamically create paths for output and cleaned text
            output_txt_path = f"output_text_{base_name}.txt"
            cleaned_txt_path = f"cleaned_text_{base_name}.txt"

            # Update the processor for the new file
            processor = PDFTextProcessor(
                pdf_path=event.src_path,
                output_txt_path=output_txt_path,
                cleaned_txt_path=cleaned_txt_path,
            )
            print(f"New file detected and processor initialized: {event.src_path}")
            print(f"Output paths updated: {output_txt_path}, {cleaned_txt_path}")


# Start the file watcher in a separate thread
def start_watcher():
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, BOOKS_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    # Start the watcher thread
    watcher_thread = threading.Thread(target=start_watcher, daemon=True)
    watcher_thread.start()

    # Run the Flask app
    app.run(debug=True)
