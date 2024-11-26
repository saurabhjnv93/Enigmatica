import re
import fitz  # PyMuPDF
import pandas as pd

class PDFTextProcessor:
    def __init__(self, pdf_path=None, output_txt_path=None, cleaned_txt_path=None):
        """
        Initialize the PDFTextProcessor with file paths.

        Parameters:
        - pdf_path: Path to the input PDF file.
        - output_txt_path: Path to save the raw extracted text.
        - cleaned_txt_path: Path to save the cleaned text.
        """
        self.pdf_path = pdf_path
        self.output_txt_path = output_txt_path
        self.cleaned_txt_path = cleaned_txt_path

    @staticmethod
    def clean_text(text):
        """
        Clean extracted text to exclude unwanted patterns and lines.

        Parameters:
        - text: The raw extracted text.

        Returns:
        - Cleaned text as a string.
        """
        unwanted_patterns = [
            r"http\S+",                  # Remove links
            r"www\.\S+",                 # Remove links starting with www
            r"\.\.\.+\s*\d+",            # Lines with ellipses followed by numbers
            r"^\d+\.\d+\s",              # Lines starting with decimal numbers
            r"\b\d+\b",                  # Lines with isolated numbers
            r"[A-Za-z0-9]+[\^\+\-*/=<>]", # Lines with mathematical operators
            r"[A-Za-z0-9]+\s*[∈∀∃∅⊆∪∩≈∑∏∫θμϵλϕδΩ→≤≥]", # Math symbols
            r"[<>≤≥=]{2,}",              # Comparison operators
            r"^\d+$",                    # Lines with only numbers
        ]
        combined_pattern = re.compile("|".join(unwanted_patterns))
        filtered_lines = [
            line for line in text.splitlines() if not combined_pattern.search(line)
        ]
        return "\n".join(filtered_lines)

    @staticmethod
    def is_page_unwanted(page_text):
        """
        Determine if a page contains unwanted content.

        Parameters:
        - page_text: Text from a single PDF page.

        Returns:
        - True if the page is unwanted, False otherwise.
        """
        lines = page_text.splitlines()
        unwanted_headers = r"^(Contents|Index|Bibliography|Exercises)"
        if len(lines) > 0 and re.match(unwanted_headers, lines[0], re.IGNORECASE):
            return True
        if len(lines) > 1 and re.match(unwanted_headers, lines[1], re.IGNORECASE):
            return True
        return False
    def extract_text(self):
        """
        Extract and clean text from the PDF, saving it to a file.
        """
        if not self.pdf_path or not self.output_txt_path:
            print("Error: PDF path or output text path is not set.")
            return
        pdf_document = fitz.open(self.pdf_path)
        full_text = ""

        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            page_text = page.get_text("text")  # Extract only text, ignoring images.

            # Ensure no image metadata or placeholders are included
            for img in page.get_images(full=True):
                img_ref = img[0]  # Image XREF
                img_placeholder = f"Image-{img_ref}"
                page_text = page_text.replace(img_placeholder, "")  # Remove image refs

            if self.is_page_unwanted(page_text):
                continue

            cleaned_text = self.clean_text(page_text)
            full_text += cleaned_text

        with open(self.output_txt_path, "w") as txt_file:
            txt_file.write(full_text)

        pdf_document.close()
        print(f"Text extraction completed. Saved to {self.output_txt_path}")


    def clean_text_file(self):
        """
        Further cleans the raw extracted text and saves it to a new file.
        """
        if not self.output_txt_path or not self.cleaned_txt_path:
            print("Error: Input or cleaned text path is not set.")
            return

        unwanted_patterns = [
            r"=\s*m\s*X\s*xi\s*x⊤\s*i", 
            r"b\s*=\s*m\s*X\s*yixi",
            r"A\s*=\s*\(.*\)",
            r"b\s*=\s*\(",
        ]
        short_form_pattern = re.compile(r"^[A-Za-z0-9\s\+\-\*/=<>≤≥\.,!?]*$")
        combined_pattern = re.compile("|".join(unwanted_patterns))

        with open(self.output_txt_path, "r") as file:
            lines = file.readlines()

        filtered_lines = []
        for line in lines:
            line = line.strip()
            if not line or combined_pattern.search(line):
                continue
            if len(line) < 20:
                continue
            words = line.split()
            short_form_count = sum(1 for word in words if short_form_pattern.match(word) and len(word) <= 3)
            if short_form_count / len(words) > 0.5:
                continue
            filtered_lines.append(line + "\n")

        with open(self.cleaned_txt_path, "w") as file:
            file.writelines(filtered_lines)

        print(f"Text cleaning completed. Saved to {self.cleaned_txt_path}")

    @staticmethod
    def process_text_to_dataframe(file_path, output_csv_path=None):
        """
        Process cleaned text into paragraphs and optionally save to a CSV file.

        Parameters:
        - file_path: Path to the cleaned text file.
        - output_csv_path: Path to save the resulting DataFrame as a CSV file.

        Returns:
        - DataFrame containing paragraphs and paragraph numbers.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+'
            sentences = re.split(sentence_pattern, text)
            paragraphs = []
            current_para = []

            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:
                    current_para.append(sentence)
                    if len(' '.join(current_para)) > 300:
                        paragraphs.append(' '.join(current_para))
                        current_para = []

            if current_para:
                paragraphs.append(' '.join(current_para))

            df = pd.DataFrame(paragraphs, columns=['paragraph'])
            df['paragraph_number'] = range(1, len(df) + 1)
            df = df[['paragraph_number', 'paragraph']]

            if output_csv_path:
                df.to_csv(output_csv_path, index=False)
                print(f"DataFrame saved to {output_csv_path}")

            return df
        except Exception as e:
            print(f"An error occurred: {e}")
            return None



