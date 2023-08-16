import requests
import zipfile
import os
import shutil
import fnmatch


def download_repo(url):
    """
    Download the latest version of the repo from the given GitHub repo URL.
    """
    # Extract the user and repo name from the URL
    parts = url.split("/")
    user = parts[-2]
    repo = parts[-1]

    # Construct the URL to get the latest zip of the repo
    zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/main.zip"

    response = requests.get(zip_url, stream=True)
    response.raise_for_status()

    with open("repo.zip", "wb") as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)

    with zipfile.ZipFile("repo.zip", "r") as zip_ref:
        zip_ref.extractall("repo_folder")

    # Clean up the downloaded zip file
    os.remove("repo.zip")


def load_ignore_patterns():
    """
    Load patterns from flattenignore.txt into a list.
    """
    patterns = []
    if os.path.exists("flattenignore.txt"):
        with open("flattenignore.txt", "r") as f:
            patterns = [line.strip() for line in f.readlines()]
    return patterns


def flatten_files(
    directory, output_file, ignore_patterns, level=2, current_level=0, path_prefix=""
):
    """
    Flatten the files in the directory up to the specified level and write their contents to the output file.
    """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Check if the item matches any of the ignore patterns
        if any(fnmatch.fnmatch(item, pattern) for pattern in ignore_patterns):
            print(f"Skipped {path_prefix}{item} based on flattenignore.txt patterns")
            continue

        # If it's a file, read its contents and write to the output file
        if os.path.isfile(item_path):
            try:
                with open(item_path, "r", encoding="utf-8") as fd:
                    output_file.write(f"[{path_prefix}{item}]\n")
                    output_file.write(fd.read())
                    output_file.write("\n\n")
            except UnicodeDecodeError:
                print(f"Skipped non-text file: {path_prefix}{item}")

        # If it's a directory and we're not at the max depth, recurse into it
        elif os.path.isdir(item_path) and current_level < level:
            flatten_files(
                item_path,
                output_file,
                ignore_patterns,
                level,
                current_level + 1,
                path_prefix=f"{item}/",
            )


def main():
    url = input("Enter the GitHub repository URL: ")
    X = int(input("Enter the flattening level (X): "))

    download_repo(url)

    ignore_patterns = load_ignore_patterns()

    with open("flattened.txt", "w") as output:
        repo_name = url.split("/")[-1]  # Extract repo name from URL
        flatten_files(f"repo_folder/{repo_name}-main", output, ignore_patterns, X)

    # Clean up the extracted repo folder
    shutil.rmtree("repo_folder")


if __name__ == "__main__":
    main()
