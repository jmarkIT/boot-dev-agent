import os
import subprocess


def run_python_file(working_directory, file_path):
    absolute_working_directory = os.path.abspath(working_directory)
    target_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file_path.startswith(absolute_working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file_path):
        return f'Error: File "{file_path}" not found.'
    if not target_file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a python file.'

    try:
        process = subprocess.run(
            ["python", target_file_path],
            capture_output=True,
            timeout=30,
            cwd=absolute_working_directory,
            check=True,
        )
    except Exception as e:
        return f"Error: executing Python file: {e}"

    cmd_stdout = process.stdout.decode("utf-8")
    cmd_stderr = process.stderr.decode("utf-8")

    if not cmd_stdout and not cmd_stderr:
        return "No output produced"

    output = ""
    if cmd_stdout:
        output += f"STDOUT: {cmd_stdout}"
    if cmd_stderr:
        output += f"STDERR: {cmd_stderr}"
    if process.returncode != 0:
        output += f"Process exited with code {process.returncode}"

    return output
