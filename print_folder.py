import os
import argparse
from collections import defaultdict

def print_directory(path, indent_level):
    base_name = os.path.basename(os.path.normpath(path))
    print('    ' * indent_level + f"{base_name}/")
    
    try:
        entries = os.listdir(path)
    except PermissionError:
        print('    ' * (indent_level + 1) + "[Permission denied]")
        return

    dirs = []
    files = []
    for entry in entries:
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            dirs.append(entry)
        else:
            files.append(entry)
    
    dirs.sort()
    files.sort()
    
    file_groups = defaultdict(list)
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        file_groups[ext].append(file)
    
    processed_files = []
    for ext in sorted(file_groups.keys()):
        group = file_groups[ext]
        if len(group) > 5:
            processed_files.extend(group[:5])
            remaining = len(group) - 5
            message = f"... {remaining} more {ext} files" if ext else f"... {remaining} more files"
            processed_files.append(message)
        else:
            processed_files.extend(group)
    
    for dir_name in dirs:
        full_dir_path = os.path.join(path, dir_name)
        print_directory(full_dir_path, indent_level + 1)
    
    for file_entry in processed_files:
        print('    ' * (indent_level + 1) + file_entry)

def main():
    parser = argparse.ArgumentParser(description='Print folder structure with file truncation.')
    parser.add_argument('root_dir', nargs='?', default='.', help='Root directory to start from')
    args = parser.parse_args()
    root_dir = os.path.abspath(args.root_dir)
    print_directory(root_dir, 0)

if __name__ == "__main__":
    main()
