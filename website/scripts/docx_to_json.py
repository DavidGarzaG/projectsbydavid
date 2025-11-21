import json
import os

from docx import Document


def docx_to_json(path_to_document: str, metadata: dict = None):
    """
    Converts a single docx file into a JSON file.
    """

    doc = Document(path_to_document)

    data = {
        "file_name": os.path.basename(path_to_document),
        "content": [],
    }

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            data["content"].append(text)

    if metadata:
        data["metadata"] = metadata.copy()

    return data


# Helper functions to get files and directories.
def get_files_in_directory(path: str):
    return [
        os.path.join(path, file)
        for file in os.listdir(path)
        if os.path.isfile(os.path.join(path, file))
    ]


def get_dirs_in_directory(path: str):
    return [
        file
        for file in os.listdir(path)
        if not os.path.isfile(os.path.join(path, file))
    ]


# In the case of having more levels within the directory like things/type/model/etc...this should be modified to have more metadata categories.
# But for now, it works with two levels only selling elevators.
# Let's get crazy with recursion.
def recursive_docx_to_json_with_metadata(
    path_to_documents: str, metadata: dict = None, converted_list: list = None
):  # Great name
    """ """

    # Create list if there is None
    if converted_list is None:
        converted_list = []

    # First process the files that are here.
    files = get_files_in_directory(path=path_to_documents)
    for file in files:
        converted_list.append(docx_to_json(path_to_document=file, metadata=metadata))

    # Find what are the next directories.
    directories = get_dirs_in_directory(path=path_to_documents)

    # Go to the next directory.
    for directory in directories:
        metadata = {"Elevator": directory}
        recursive_docx_to_json_with_metadata(
            path_to_documents=os.path.join(path_to_documents, directory),
            metadata=metadata,
            converted_list=converted_list,
        )

    return converted_list


if __name__ == "__main__":
    # Harcoded because its just an example. Won't be using this for now.
    path_to_documents = os.path.join(
        os.getcwd(), "../../eco_elevadores/Eco_Elevadores_PVE/"
    )
    path = "info.json"

    data = recursive_docx_to_json_with_metadata(path_to_documents=path_to_documents)

    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
