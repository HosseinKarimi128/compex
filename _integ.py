import argparse
from pathlib import Path

def combine_python_files(source_dir, output_file):
    """
    Combines all Python (.py) files in the specified directory into a single Python file.

    Parameters:
    - source_dir (str or Path): The directory containing Python files to combine.
    - output_file (str or Path): The path to the output Python file.

    Raises:
    - FileNotFoundError: If the source directory does not exist.
    - IOError: If there are issues reading or writing files.
    """
    source_path = Path(source_dir)
    output_path = Path(output_file)

    if not source_path.is_dir():
        raise FileNotFoundError(f"The directory {source_dir} does not exist.")

    # Get all .py files in the directory, sorted alphabetically
    python_files = sorted(source_path.glob("*.py"))

    if not python_files:
        print(f"No Python files found in directory: {source_dir}")
        return

    try:
        with output_path.open('w', encoding='utf-8') as outfile:
            outfile.write("# Combined Python File\n")
            outfile.write("# This file is autogenerated by combine_python_files function\n\n")
            
            for py_file in python_files:
                outfile.write(f"# ----- Begin {py_file.name} -----\n")
                with py_file.open('r', encoding='utf-8') as infile:
                    contents = infile.read()
                    outfile.write(contents)
                    outfile.write("\n\n")
                outfile.write(f"# ----- End {py_file.name} -----\n\n")
        
        print(f"Successfully combined {len(python_files)} files into {output_file}")
    
    except IOError as e:
        print(f"An error occurred while reading or writing files: {e}")

def main():
    """
    Main function to parse command-line arguments and invoke the combine function.
    """
    parser = argparse.ArgumentParser(
        description="Combine all Python (.py) files in a directory into a single Python file."
    )
    parser.add_argument(
        "source_dir",
        type=str,
        help="Path to the source directory containing Python files."
    )
    parser.add_argument(
        "output_file",
        nargs='?',
        default="combined.py",
        help="Path to the output Python file. Defaults to 'combined.py' in the current directory."
    )
    
    args = parser.parse_args()
    
    combine_python_files(args.source_dir, args.output_file)

if __name__ == "__main__":
    main()
