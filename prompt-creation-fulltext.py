import json
import os
import sys
sys.path.append('/Users/it/Desktop/section_formatting/')
import



# Global paths to your files for the "prompt-creation-fulltext" project
Data_path = "/Users/it/Desktop/prompt-creation-fulltext/prompt-creation-fulltext/data.json"
TXT_Directory = "/Users/it/desktop/PDF_Correct/text_files"
Output_JSON_path = "/Users/it/Desktop/prompt-creation-fulltext/prompt-creation-fulltext/output_data_grouped.json"  # Path to save the grouped result JSON
Prompt_Completion_JSON_path = "/Users/it/Desktop/prompt-creation-fulltext/prompt-creation-fulltext/output_prompt_completion.json"  # Path for prompt-completion JSON

def load_file(file_path):
    """Loads a JSON file from the specified path."""
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_full_text_from_txt(file_path):
    """
    Extracts the full text from a .txt file.
    :param file_path: The path to the .txt file.
    :return: A string containing the full text of the file.
    """
    with open(file_path, 'r') as file:
        return file.read()

def create_json_objects(questions, full_text_content, filename):
    """
    Constructs a list of JSON objects for the full text content.
    :param questions: A list of questions from the first file.
    :param full_text_content: The full text content from the .txt file.
    :param filename: The name of the file being processed.
    :return: A list of JSON objects for the full text content.
    """
    json_object = {
        "questions": questions,
        "full_text_content": full_text_content,
        "source_filename": filename
    }
    return [json_object]

def process_files(file1_data, full_text_content, filename):
    """
    Processes the data from the first file and full text from the .txt file.
    :param file1_data: Data from the first JSON file.
    :param full_text_content: The full text content from the .txt file.
    :param filename: The name of the file being processed (to include in the JSON objects).
    :return: A dictionary with 'data' as keys and lists of JSON objects as values.
    """
    grouped_results = {}  # Dictionary to group results by the 'data' field

    # Iterate over entries in file 1
    for entry in file1_data:
        data_value = entry.get("data", "")
        questions = entry.get("questions", [])

        # Formulate the JSON objects using the full text
        result_json_objects = create_json_objects(questions, full_text_content, filename)

        # Group the result JSON objects by the 'data' field
        if data_value in grouped_results:
            grouped_results[data_value].extend(result_json_objects)
        else:
            grouped_results[data_value] = result_json_objects

    return grouped_results

def process_multiple_txt_files(file1_data, txt_directory):
    """
    Processes multiple .txt files in the specified directory along with the data from the first file.
    :param file1_data: Data from the first JSON file.
    :param txt_directory: Directory containing .txt files to process.
    :return: A dictionary that groups results from all processed files.
    """
    combined_results = {}

    # Ensure that the directory exists and contains files
    if not os.path.exists(txt_directory):
        print(f"Directory {txt_directory} does not exist.")
        return combined_results

    if not os.listdir(txt_directory):
        print(f"No files found in {txt_directory}.")
        return combined_results

    # Loop through all files in the directory
    for filename in os.listdir(txt_directory):
        if filename.endswith(".txt"):  # Process only .txt files
            file_path = os.path.join(txt_directory, filename)
            print(f"Processing file: {file_path}")

            # Extract the full text from the .txt file
            try:
                full_text_content = extract_full_text_from_txt(file_path)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue

            # Process the files and get grouped results, passing the filename
            results = process_files(file1_data, full_text_content, filename)

            # Merge the results into the combined results, grouped by data_value
            for data_value, result_json_objects in results.items():
                if data_value in combined_results:
                    combined_results[data_value].extend(result_json_objects)
                else:
                    combined_results[data_value] = result_json_objects

    return combined_results


def create_prompt_completion_json(grouped_data):
    """
    Creates JSON objects in the format {"prompt": "", "completion": ""} from the grouped data.
    :param grouped_data: The grouped data generated from the process_files function.
    :return: A list of JSON objects where 'prompt' contains the formatted string and 'completion' is empty.
    """
    prompt_completion_data = []

    for data_value, json_objects in grouped_data.items():
        for obj in json_objects:
            questions_string = " ".join(obj['questions'])  # Join the questions without brackets

            # Detect the language of the full text content
            detected_language = tokenization.detect_language(obj['full_text_content'])

            # Use the detected language when cleaning the text
            cleaned_text = tokenization.clean_text_with_preserved_entities(obj['full_text_content'], detected_language)

            # Construct the prompt string
            prompt_string = f"{data_value}: {questions_string} from the following text: {cleaned_text}"

            # Create the prompt-completion object
            prompt_completion_obj = {
                "prompt": prompt_string,
                "completion": ""
            }
            prompt_completion_data.append(prompt_completion_obj)

    return prompt_completion_data


def save_results_to_json(result_data, output_path):
    """
    Saves the processed results to a JSON file.
    :param result_data: The final processed data to be saved.
    :param output_path: The path where the result JSON file will be saved.
    """
    try:
        with open(output_path, 'w') as outfile:
            json.dump(result_data, outfile, indent=4)
        print(f"Results saved to {output_path}")
    except Exception as e:
        print(f"Error saving results to {output_path}: {e}")

def main():
    # Load data from the first file
    try:
        file1_data = load_file(Data_path)
    except Exception as e:
        print(f"Error loading data file: {e}")
        return

    # Process multiple .txt files from the specified directory
    grouped_results = process_multiple_txt_files(file1_data, TXT_Directory)

    # Save the grouped results to a new JSON file
    if not grouped_results:
        print("No results to display.")
    else:
        save_results_to_json(grouped_results, Output_JSON_path)

    # Create and save the prompt-completion JSON file
    prompt_completion_data = create_prompt_completion_json(grouped_results)
    save_results_to_json(prompt_completion_data, Prompt_Completion_JSON_path)

if __name__ == "__main__":
    main()
