import os

def file_navigate(file_path, steps):
    directory, filename = os.path.split(file_path)
    prefix, suffix = filename.split('_')
    file_id = int(suffix.split('.')[0])

    total_files = 10000
    file_id += steps

    if file_id < 0:
        file_id = (total_files - abs(file_id) % total_files) % total_files
    elif file_id >= total_files:
        file_id = file_id % total_files

    new_filename = f"{prefix}_{str(file_id).zfill(5)}.JPG"
    new_file_path = os.path.join(directory, new_filename)

    return new_file_path