import os
import PyPDF2
from pdf2image import convert_from_path
import pytesseract


# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    try:
        # Attempt to read as a text-based PDF
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() or ""
            if text.strip():  # Return if text is found
                return text
    except Exception as e:
        print(f"Error reading text-based PDF: {e}")

    # If no text is found, treat it as a scanned PDF (image-based)
    print(f"Processing scanned PDF: {pdf_path}")
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text


# Function to save text to a .txt file
def save_text_to_file(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as text_file:
        text_file.write(text)


# Main function to process PDFs
def process_pdfs(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            print(f"Extracting text from: {filename}")
            text = extract_text_from_pdf(pdf_path)

            if text.strip():  # Save only if some text is found
                output_filename = os.path.splitext(filename)[0] + ".txt"
                output_path = os.path.join(output_dir, output_filename)
                save_text_to_file(text, output_path)
                print(f"Text saved to: {output_path}")
            else:
                print(f"No text extracted from: {filename}")


# Usage
input_directory = "/Users/it/desktop/PDF_Correct"
output_directory = "/Users/it/desktop/PDF_Correct/text_files"
process_pdfs(input_directory, output_directory)
