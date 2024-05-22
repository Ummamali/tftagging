import os
import shutil


def move_files(folder1, folder2, filenames):
    """
    Move files from folder1 to folder2 if they exist in folder1.

    Parameters:
        folder1 (str): Path to the source folder.
        folder2 (str): Path to the destination folder.
        filenames (list): List of filenames to search for and move.

    Returns:
        None
    """
    for filename in filenames:
        # Construct full paths for source and destination files
        source_file = os.path.join(folder1, filename)
        destination_file = os.path.join(folder2, filename)

        # Check if file exists in folder1
        if os.path.exists(source_file):
            # Move the file to folder2
            shutil.move(source_file, destination_file)
            print(f"Moved {filename} from {folder1} to {folder2}")
        else:
            print(f"{filename} does not exist in {folder1}")


def delete_items_in_directory(directory_path, delete_files=True, delete_folders=True):
    try:
        # Get the list of items in the directory
        items_list = os.listdir(directory_path)

        # Iterate over the items and delete each based on the specified criteria
        for item_name in items_list:
            item_path = os.path.join(directory_path, item_name)

            if delete_files and os.path.isfile(item_path):
                os.remove(item_path)
                print(f"Deleted file: {item_path}")

            if delete_folders and os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Deleted folder: {item_path}")

        print(f"All items in {directory_path} have been deleted.")
    except Exception as e:
        print(f"Error: {e}")


def filter_comparison_scores(tuples_array, threshold):
    """
    Filters the tuples in the array based on the threshold score.

    Parameters:
    tuples_array (list of tuples): An array of tuples (index, score), sorted in descending order of scores.
    threshold (int or float): The threshold score.

    Returns:
    list of tuples: An array where all elements have scores greater than the threshold.
    """
    result = []
    for index, score in tuples_array:
        if score > threshold:
            result.append((index, score))
        else:
            break
    return result