from git import Repo # type: ignore
from rich import print as rprint # type: ignore
import logging, io, random, sys
from rich.progress import track  # type: ignore
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

def get_file_commits(repo, path):
    logging.info(f"Getting all commits for the file path: {path}")
    revlist = (
        (commit, (commit.tree / path).data_stream.read())
        for commit in repo.iter_commits(paths=path)
    )
    logging.info(f"Successfully obtained commits for the file path: {path}")
    return revlist

def get_file_content_at_commit(repo, path, commit_hash):
    logging.info(f"Getting content of file '{path}' at commit: {commit_hash}")
    target_commit = repo.commit(commit_hash)
    targetfile = target_commit.tree / path
    with io.BytesIO(targetfile.data_stream.read()) as f:
        content = f.read().decode('utf-8')
    return content

def main(repo_path, issue_number):
    console = Console()
    log = setup_logging()

    log.info('Getting the repo ...')
    repo = get_repo(repo_path)

    log.info('Finding commits related to the issue ...')
    issue_commits = get_issue_commits(repo, issue_number)
    log.error(issue_commits[0].message)
    if not issue_commits:
        log.error(f"No commits found for issue #{issue_number}")
        return
    selected_commit = random.choice(issue_commits)
    log.info(f'Selected commit for issue #{issue_number}: {selected_commit.hexsha}')

    log.info('Getting files changed in the selected commit ...')
    files = get_commit_files(repo, selected_commit.hexsha)
    console.print(files)
    if not files:
        log.error(f"No files changed in commit {selected_commit.hexsha}")
        return
    selected_file = random.choice(list(files.keys()))
    log.info(f'Selected file from commit {selected_commit.hexsha}: {selected_file}')

    log.info("Getting all commits for the selected file path ...")
    revlist = get_file_commits(repo, selected_file)
    revlist = list(revlist)  # Convert generator to list for random selection
    if not revlist:
        log.error(f"No commits found for file path: {selected_file}")
        return
    selected_file_commit, _ = random.choice(revlist)
    console.print(selected_file_commit.hexsha)
    logging.debug(f"Selected commit for file '{selected_file}': {selected_file_commit.hexsha}")

    log.info("Getting file content at the selected commit ...")
    # file_content = get_file_content_at_commit(repo, selected_file, selected_file_commit.hexsha)
    # console.print(file_content, style="italic r")

if __name__ == "__main__":
    # Example usage:
    if len(sys.argv) != 3:
        print("Usage: python IssueChangesTracker.py <repo_path> <issue_number>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    issue_number = sys.argv[2]

    main(repo_path, issue_number)
