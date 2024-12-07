import json
import os

from embeddings import generate_code_embedding, generate_issue_description_embedding
from gitcodes import get_codebase_before_commit, get_codebase_after_commit, get_commit_files, get_issue_commits, get_issue_description
from metrics import get_all_metrics  # Importing the metrics function


def create_issue_dataset(repo, issue_numbers, tokenizer, model, owner, repo_name, logger, output_file='data/issue_dataset.jsonl', repo_path=''):
    """
    Create a dataset with specified columns for given issues and save it in JSON Lines format.

    Parameters:
    - repo: Git repository object.
    - issue_numbers (iterable): Iterable of issue numbers to process.
    - tokenizer: Tokenizer for CodeBERT.
    - model: Pre-trained CodeBERT model.
    - owner (str): Repository owner.
    - repo_name (str): Repository name.
    - logger: Logger instance for logging.
    - output_file (str): Path to the output JSONL file.
    - repo_path (str): Path to the Git repository for duplication metrics.

    Returns:
    - None
    """
    logger.info(f"Creating dataset for issues: {list(issue_numbers)}")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for issue_number in issue_numbers:
                logger.info(f"Processing issue #{issue_number}")
                issue_commits = get_issue_commits(repo, issue_number, logger)
                if not issue_commits:
                    logger.warning(f"No commits found for issue #{issue_number}, skipping...")
                    continue

                issue_description = get_issue_description(issue_number, owner, repo_name, logger)

                # Generate embedding for issue description
                issue_description_embedding = generate_issue_description_embedding(issue_description, model, tokenizer, logger)

                # Sort commits by commit date to find the first commit
                sorted_commits = sorted(issue_commits, key=lambda c: c.committed_date)
                first_commit = sorted_commits[0]
                first_commit_hash = first_commit.hexsha
                logger.info(f"First commit for issue #{issue_number}: {first_commit_hash}")

                last_commit = sorted_commits[-1]
                last_commit_hash = last_commit.hexsha
                logger.info(f"Last commit for issue #{issue_number}: {last_commit_hash}")

                # Get codebase before the first commit
                codebase_before = get_codebase_before_commit(repo, first_commit, logger)
                codebase_after = get_codebase_after_commit(repo, last_commit, logger)


                # Generate embedding for codebase before first commit
                codebase_embedding_before = generate_code_embedding(codebase_before, tokenizer, model, logger)

                # Generate embedding for codebase after last commit
                codebase_embedding_after = generate_code_embedding(codebase_after, tokenizer, model, logger)
                
                # Calculate NOC, NOCF, NOI, NOD
                noc = len(issue_commits)
                nocf = 0
                nod = 0
                noi = 0

                for commit in issue_commits:
                    files = get_commit_files(repo, commit.hexsha, logger)
                    nocf += len(files)
                    for file, stats in files.items():
                        nod += stats.get('deletions', 0)
                        noi += stats.get('insertions', 0)

                # Calculate additional code metrics
                logger.info(f"Calculating code metrics for issue #{issue_number}")
                metrics_before = get_all_metrics(codebase_before, repo_path)
                metrics_after = get_all_metrics(codebase_after, repo_path)


                # Prepare the data record
                record = {
                    'issue_id': issue_number,
                    'issue_description': issue_description,
                    'issue_description_embedding': issue_description_embedding if issue_description_embedding else [],
                    'first_commit': first_commit_hash,
                    'last_commit': last_commit_hash,
                    'codebase_embedding_before_first_commit': codebase_embedding_before if codebase_embedding_before else [],
                    'codebase_embedding_after_last_commit': codebase_embedding_after if codebase_embedding_after else [],

                    'NOC': noc,
                    'NOCF': nocf,
                    'NOI': noi,
                    'NOD': nod,

                    'LOC_before': metrics_before.get('LOC'),
                    'Comments_before': metrics_before.get('comments'),
                    'CyclomaticComplexity_before': metrics_before.get('CyclomaticComplexity'),
                    'HalsteadMetrics_before': metrics_before.get('HalsteadMetrics'),
                    'MaintainabilityIndex_before': metrics_before.get('MaintainabilityIndex'),
                    'CodeDuplication_before': metrics_before.get('CodeDuplication'),
                    'Coupling_before': metrics_before.get('coupling'),
                    'Cohesion_before': metrics_before.get('cohesion'),

                    'LOC_after': metrics_after.get('LOC'),
                    'Comments_after': metrics_after.get('comments'),
                    'CyclomaticComplexity_after': metrics_after.get('CyclomaticComplexity'),
                    'HalsteadMetrics_after': metrics_after.get('HalsteadMetrics'),
                    'MaintainabilityIndex_after': metrics_after.get('MaintainabilityIndex'),
                    'CodeDuplication_after': metrics_after.get('CodeDuplication'),
                    'Coupling_after': metrics_after.get('coupling'),
                    'Cohesion_after': metrics_after.get('cohesion')
                }

                # Write the JSON object as a single line
                f.write(json.dumps(record) + '\n')

                logger.debug(f"Written data for issue #{issue_number} to {output_file}")

        logger.info(f"Dataset successfully saved to '{output_file}'")
    except Exception as e:
        logger.error(f"Error during dataset creation: {e}")
