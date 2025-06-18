import os


def get_files_info(working_directory, directory=None):
    absolute_working_directory = os.path.abspath(working_directory)
    target_directory = absolute_working_directory
    if directory:
        target_directory = os.path.abspath(os.path.join(working_directory, directory))

        if not target_directory.startswith(absolute_working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(target_directory):
            return f'Error: {directory}" is not a directory'
    try:
        files_info = []
        for filename in os.listdir(target_directory):
            filepath = os.path.join(target_directory, filename)
            file_size = 0
            is_dir = os.path.isdir(filepath)
            file_size = os.path.getsize(filepath)
            files_info.append(
                f"- {filename}: file_size={file_size} bytes, is_dir={is_dir}"
            )
        return "\n".join(files_info)
    except Exception as e:
        return f"Error listing files: {e}"
