# Abstracts Python's JSON module.

import json  # should be compatible with simplejson as well, can theoretically be replaced with "import simplejson as json" without breaking anything.

# constants
DEFAULT_FILE_NAME = (
    ".tasks.json"  # the file name used by the functions if no file name is passed
)
DEFAULT_FILE_CONTENT = '{"To Do": [], "In Progress": [], "Done": []}'  # the content written to a newly created file if no content is passed


def get_data(filename: str = DEFAULT_FILE_NAME) -> any:
    """Load JSON data from a file to a Python object

    Keyword Arguments:
        filename -- The name of the file to load from (default: {DEFAULT_FILE_NAME})

    Returns:
        any: The python object created from the JSON data.
    """
    with open(filename, "r") as tasks:
        return json.load(tasks)


def write_data(data: any, filename: str = DEFAULT_FILE_NAME) -> None:
    """Convert a Python object to a JSON string and write this to a file.  Note any existing content will be overwritten.

    Arguments:
        data -- The Python object to convert to a JSON string and store

    Keyword Arguments:
        filename -- The name of the file to write to (default: {DEFAULT_FILE_NAME})
    """
    with open(filename, "w") as tasks:
        json.dump(data, tasks)


def create_file(
    filename: str = DEFAULT_FILE_NAME, file_content: str = DEFAULT_FILE_CONTENT
) -> None:
    """Create a new file (note that if the file exists it will be overwritten)

    Keyword Arguments:
        filename -- The name of the file to create/overwrite (default: {DEFAULT_FILE_NAME})
        file_content -- The content to write to the file (default: {DEFAULT_FILE_CONTENT})
    """
    with open(filename, "w") as tasks:
        tasks.write(
            file_content
        )  # more efficient than loading the string to a JSON object and then dumping the JSON object to a file.
