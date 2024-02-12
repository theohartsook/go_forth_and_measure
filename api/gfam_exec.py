import argparse, sys
from .project_management import importJSON, processVideo
from .validation import validateArguments

def main(json_path):
    data = importJSON(json_path)
    data = validateArguments(data)
    processVideo(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help='path to JSON settings', type=str)
    args = parser.parse_args()

    if args.i is None:
        parser.print_help()
        sys.exit(1) 
    main(args.i)