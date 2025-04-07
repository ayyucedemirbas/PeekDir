import os
import argparse
import json
from collections import defaultdict

def build_structure(path, truncate_limit=5):
    name = os.path.basename(os.path.normpath(path))
    node = {
        "name": name,
        "type": "directory",
        "children": []
    }
    
    try:
        entries = os.listdir(path)
    except PermissionError:
        node["error"] = "Permission denied"
        return node

    dirs, files = [], []
    for entry in entries:
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            dirs.append(entry)
        else:
            files.append(entry)


    for dir_name in sorted(dirs):
        full_dir_path = os.path.join(path, dir_name)
        node["children"].append(build_structure(full_dir_path, truncate_limit))

    file_groups = defaultdict(list)
    for file in sorted(files):
        ext = os.path.splitext(file)[1].lower()
        file_groups[ext].append(file)

    for ext in sorted(file_groups.keys()):
        group = file_groups[ext]
        if len(group) > truncate_limit:
            truncated = {
                "type": "truncation",
                "message": f"... {len(group)-truncate_limit} more {ext} files"
            }
            node["children"].extend([
                {"type": "file", "name": f} for f in group[:truncate_limit]
            ])
            node["children"].append(truncated)
        else:
            node["children"].extend([
                {"type": "file", "name": f} for f in group
            ])

    return node

def print_console_structure(node, indent=0):
    print("    " * indent + f"{node['name']}/")
    for child in node["children"]:
        if child["type"] == "directory":
            print_console_structure(child, indent + 1)
        else:
            prefix = "    " * (indent + 1)
            print(prefix + (child["name"] if child["type"] == "file" else child["message"]))

def main():
    parser = argparse.ArgumentParser(description="PeekDir - Smart directory structure visualization")
    parser.add_argument("root_dir", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "txt"], default="txt",
                      help="Output format (only if using --output)")
    parser.add_argument("--truncate", type=int, default=5,
                      help="Number of files to show before truncation")

    args = parser.parse_args()
    structure = build_structure(os.path.abspath(args.root_dir), args.truncate)

    print_console_structure(structure)

    if args.output:
        if args.format == "json":
            with open(args.output, "w") as f:
                json.dump(structure, f, indent=2)
        elif args.format == "txt":
            with open(args.output, "w") as f:
                def write_lines(node, indent=0):
                    f.write("    " * indent + f"{node['name']}/\n")
                    for child in node["children"]:
                        if child["type"] == "directory":
                            write_lines(child, indent + 1)
                        else:
                            line = "    " * (indent + 1)
                            line += child["name"] if child["type"] == "file" else child["message"]
                            f.write(line + "\n")
                write_lines(structure)

if __name__ == "__main__":
    main()
