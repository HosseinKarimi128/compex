import argparse
import sys

from _logging import setup_logging
from dataset import create_issue_dataset
from embeddings import load_codebert_model
from gitcodes import GitCodes
from _globals import OWNER, REPO_NAME


def main():
    """
    Main function to create the issue dataset.

    Parses command-line arguments, sets up logging, loads the models, accesses the repository,
    and initiates dataset creation based on the provided issue range.
    """
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        description='Create a dataset of GitHub issues with related commit information and codebase embeddings.',
        epilog='Example usage: python IssueDatasetCreator.py /path/to/repo 1 100',
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Define positional arguments
    parser.add_argument(
        'repo_path',
        type=str,
        help='Path to the cloned GitHub repository.'
    )
    parser.add_argument(
        '--start_issue_number',
        type=int,
        default=1,
        help='Starting issue number (inclusive).'
    )
    parser.add_argument(
        '--end_issue_number',
        type=int,
        default=1,
        help='Ending issue number (inclusive).'
    )

    # Define optional arguments
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/issue_dataset.jsonl',
        help='Path to the output JSON Lines (.jsonl) file. Default: data/issue_dataset.jsonl'
    )
    parser.add_argument(
        '-l', '--log',
        type=str,
        default='dataset_creation.log',
        help='Path to the log file. Default: dataset_creation.log'
    )
    parser.add_argument(
        '--owner',
        type=str,
        default=OWNER,
        help=f"Repository owner. Default: '{OWNER}'"
    )
    parser.add_argument(
        '--repo',
        type=str,
        default=REPO_NAME,
        help=f"Repository name. Default: '{REPO_NAME}'"
    )
    parser.add_argument(
        '--description-embedder',
        type=str,
        default='sentence-transformers/all-MiniLM-L6-v2',
        help="Sentence-BERT model for embedding issue descriptions. Default: 'sentence-transformers/all-MiniLM-L6-v2'"
    )

    # Parse arguments
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(log_file=args.log)

    # Log script start
    logger.info("Starting Issue Dataset Creation Script.")

    # Creating GitCode object
    gitcode = GitCodes()

    # Validate issue range
    if args.start_issue_number > args.end_issue_number:
        logger.error("Start issue number must be less than or equal to end issue number.")
        sys.exit(1)

    # Load CodeBERT model and tokenizer
    logger.info("Loading CodeBERT model and tokenizer...")
    try:
        tokenizer, model = load_codebert_model()
        logger.info("CodeBERT model and tokenizer loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading CodeBERT model: {e}")
        sys.exit(1)


    # Get Git repository
    repo = gitcode.get_repo(args.repo_path, logger)

    # Define issue numbers
    if args.end_issue_number == 1:
        last_issue = gitcode.get_last_closed_issue(repo, args.owner, args.repo, logger)
        issue_numbers = range(args.start_issue_number, last_issue + 1)
    else:
        issue_numbers = range(args.start_issue_number, args.end_issue_number + 1)

    # Create dataset
    create_issue_dataset(
        repo=repo,
        issue_numbers=issue_numbers,
        tokenizer=tokenizer,
        model=model,
        owner=args.owner,
        repo_name=args.repo,
        logger=logger,
        output_file=args.output,
        repo_path=args.repo_path  # Passing the repository path
    )

    logger.info("Issue Dataset Creation Script finished.")


if __name__ == "__main__":
    main()