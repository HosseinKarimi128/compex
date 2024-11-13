from git import Repo # type: ignore
from rich import print as rprint # type: ignore
import logging, io, random, sys, os, requests # type: ignore
import pandas as pd # type: ignore
from rich.progress import track # type: ignore
from rich.console import Console # type: ignore
from rich.logging import RichHandler # type: ignore


def setup_logging():
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
    return logging.getLogger("rich")

def get_repo(path):
    logging.info(f"Attempting to get repository at path: {path}")
    repo = Repo(path)
    logging.info(f"Successfully obtained repository: {repo}")
    return repo

def get_issue_commits(repo, issue_number):
    logging.info(f"Searching for commits related to issue number: {issue_number}")
    issue_commits = []
    for commit in track(repo.iter_commits(), description="Iterating over all commits..."):
        if f'#{issue_number}' in commit.message:
            logging.debug(f"Found commit related to issue #{issue_number}: {commit.hexsha}")
            issue_commits.append(commit)
    logging.info(f"Total commits found for issue #{issue_number}: {len(issue_commits)}")
    return issue_commits

def get_commit_files(repo, commit_hash):
    logging.info(f"Getting files changed in commit: {commit_hash}")
    commit_to_check = repo.commit(commit_hash)
    files = commit_to_check.stats.files
    logging.debug(f"Files changed in commit {commit_hash}: {files}")
    return files

def get_issue_description(issue_number):
    token = os.environ.get('GITHUB_TOKEN')
    owner = OWNER
    repo_name = REPO_NAME
    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}"
    headers = {"Authorization": f"token {token}"} if token else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('body', f"Issue #{issue_number}")
    else:
        return f"Issue #{issue_number} (not found)"

def create_issue_dataset(repo, issue_numbers):
    log = setup_logging()
    log.info(f"Creating dataset for issues: {issue_numbers}")

    data = {
        'issue_id': [],
        'issue_description': [],
        'NOC': [],
        'NOCF': [],
        'NOD': [],
        'NOI': []
    }

    for issue_number in issue_numbers:
        log.info(f"Processing issue #{issue_number}")
        issue_commits = get_issue_commits(repo, issue_number)
        if not issue_commits:
            log.warning(f"No commits found for issue #{issue_number}, skipping...")
            continue

        issue_description = get_issue_description(issue_number)
        logging.critical(issue_description)
        noc = len(issue_commits)
        nocf = 0
        nod = 0
        noi = 0

        for commit in issue_commits:
            files = get_commit_files(repo, commit.hexsha)
            nocf += len(files)
            for file, stats in files.items():
                nod += stats.get('deletions', 0)
                noi += stats.get('insertions', 0)

        data['issue_id'].append(issue_number)
        data['issue_description'].append(issue_description)
        data['NOC'].append(noc)
        data['NOCF'].append(nocf)
        data['NOD'].append(nod)
        data['NOI'].append(noi)

    df = pd.DataFrame(data)
    df.to_csv(f'data/issue_dataset_{issue_numbers[0]}_to_{issue_numbers[-1]}.csv', index=False)
    return df

def main(repo_path, issue_range):
    console = Console()
    log = setup_logging()
    log.info('Getting the repo ...')
    repo = get_repo(repo_path)

    log.info('Generating dataset for the issues ...')
    issue_numbers = range(int(issue_range[0]), int(issue_range[1]) + 1)
    dataset = create_issue_dataset(repo, issue_numbers)
    if not dataset.empty:
        console.print(dataset)
        log.info(f"Dataset saved to data/issue_dataset_{issue_range[0]}_to_{issue_range[1]}.csv")
    else:
        log.warning("No data available for the provided issue range.")

if __name__ == "__main__":
    OWNER = 'pytest-dev'
    REPO_NAME = 'pytest'
    # Example usage:
    if len(sys.argv) != 4:
        print("Usage: python IssueChangesTracker.py <repo_path> <start_issue_number> <end_issue_number>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    start_issue_number = sys.argv[2]
    end_issue_number = sys.argv[3]

    main(repo_path, (start_issue_number, end_issue_number))
