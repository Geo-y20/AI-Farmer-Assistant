import ast
import re

def extract_imports_with_versions(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            print("File Content:")
            print(file_content)

            tree = ast.parse(file_content)

    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    imports_with_versions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports_with_versions.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            version = get_version_from_import(node, file_content)
            if version:
                imports_with_versions.append(f"{module_name}={version}")
            else:
                imports_with_versions.append(module_name)

    return imports_with_versions

def get_version_from_import(import_node, file_content):
    start = import_node.lineno - 1
    end = start + 1
    lines = file_content.split('\n')[start:end]

    for line in lines:
        version_match = re.search(r'(\d+(\.\d+)*)', line)
        if version_match:
            return version_match.group(1)
    return None

def export_to_txt_with_versions(imports_with_versions, output_file):
    try:
        with open(output_file, 'w') as file:
            for statement in imports_with_versions:
                file.write(statement + '\n')
        print(f"Export successful. {len(imports_with_versions)} import statements written to {output_file}.")
    except Exception as e:
        print(f"Error exporting to file: {e}")

if __name__ == "__main__":
    python_file_path = r"G:\Work\Project Capstone\Project ISEF\Version Website\appf.py"
    output_txt_file = r"G:\Work\Project Capstone\Project ISEF\Version Website\output_packages.txt"

    imports_with_versions = extract_imports_with_versions(python_file_path)

    # Print all import statements with versions to check if any were found
    print("All Import Statements with Versions:", imports_with_versions)

    export_to_txt_with_versions(imports_with_versions, output_txt_file)
