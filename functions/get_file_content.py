import os


def get_file_content(working_directory, file_path):
    absolute_working_directory = os.path.abspath(working_directory)
    target_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file_path.startswith(absolute_working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file_path):
        return f'Error: File not found or is not a a regular file: "{file_path}"'

    MAX_CHARS = 10000

    try:
        with open(target_file_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            truncated = f.read(1) != ""
    except Exception as e:
        return f"Error reading file contents: {e}"

    if truncated:
        file_content_string += f'[...File "{file_path}" truncated at 10000 characters]'
    return file_content_string
