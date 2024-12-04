import os
import shutil
import json
from datetime import datetime

def organize_files_by_extension(path, files, exceptions):
    move_log = {}  # Dictionary to store move operations for undo
    created_dirs = []  # List to store newly created directories

    # Generate a timestamp for the current organization session
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    move_log[timestamp] = {}

    for file in files:
        # Skip directories and files in the exceptions list
        if os.path.isdir(os.path.join(path, file)) or file in exceptions:
            continue
        
        # Get file extension
        _, extension = os.path.splitext(file)
        extension = extension.lstrip('.').lower()  # Remove the dot and convert to lowercase
        
        if extension:  # Only proceed if there's an extension
            # Create a directory for the extension if it doesn't exist
            extension_dir = os.path.join(path, extension)
            if not os.path.exists(extension_dir):
                os.makedirs(extension_dir, exist_ok=True)
                created_dirs.append(extension_dir)  # Track newly created directories
            
            # Move the file into the respective directory
            source = os.path.join(path, file)
            destination = os.path.join(extension_dir, file)
            shutil.move(source, destination)
            print(f"Moved {file} to {extension}/")

            # Log the move operation
            move_log[timestamp][file] = [source, destination]

    # Load existing move log or create a new one
    log_file_path = os.path.join(path, 'move_log.json')
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            data = json.load(log_file)
    else:
        data = {'moves': {}, 'created_dirs': {}}

    # Add the move log and created directories to the log
    data['moves'][timestamp] = move_log[timestamp]
    data['created_dirs'][timestamp] = created_dirs

    # Save the updated move log
    with open(log_file_path, 'w') as log_file:
        json.dump(data, log_file)
