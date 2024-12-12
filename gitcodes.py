import os
import sys
import git  # type: ignore
import requests  # type: ignore

class GitCodes:

    def __init__(self):
        self.TOKEN_COUNTER = 0

    def get_repo(self, path, logger):
        """
        Get the Git repository at the specified path.

        Parameters:
        - path (str): Path to the cloned Git repository.
        - logger: Logger instance for logging.

        Returns:
        - repo: Git repository object.
        """
        logger.info(f"Attempting to get repository at path: {path}")
        try:
            repo = git.Repo(path)
            logger.info(f"Successfully obtained repository: {repo.working_tree_dir}")
            return repo
        except git.exc.InvalidGitRepositoryError:
            logger.error(f"Invalid Git repository at path: {path}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error accessing repository: {e}")
            sys.exit(1)

    def get_issue_commits(self, repo, issue_number, logger):
        """
        Retrieve commits related to a specific issue.

        Parameters:
        - repo: Git repository object.
        - issue_number (int): Issue number to search for.
        - logger: Logger instance for logging.

        Returns:
        - issue_commits (list): List of commit objects related to the issue.
        """
        logger.info(f"Searching for commits related to issue number: {issue_number}")
        issue_commits = []
        try:
            for commit in repo.iter_commits():
                if f'#{issue_number}' in commit.message:
                    logger.debug(f"Found commit related to issue #{issue_number}: {commit.hexsha}")
                    issue_commits.append(commit)
            logger.info(f"Total commits found for issue #{issue_number}: {len(issue_commits)}")
            return issue_commits
        except Exception as e:
            logger.error(f"Error while fetching commits for issue #{issue_number}: {e}")
            return issue_commits

    def get_commit_files(self, repo, commit_hash, logger):
        """
        Get files changed in a specific commit.

        Parameters:
        - repo: Git repository object.
        - commit_hash (str): SHA hash of the commit.
        - logger: Logger instance for logging.

        Returns:
        - files (dict): Dictionary of files changed in the commit with stats.
        """
        logger.info(f"Getting files changed in commit: {commit_hash}")
        try:
            commit_to_check = repo.commit(commit_hash)
            files = commit_to_check.stats.files
            logger.debug(f"Files changed in commit {commit_hash}: {files}")
            return files
        except Exception as e:
            logger.error(f"Error fetching files for commit {commit_hash}: {e}")
            return {}

    def get_issue_description(self, issue_number, owner, repo_name, logger):
        """
        Fetch the description of a GitHub issue.

        Parameters:
        - issue_number (int): Issue number.
        - owner (str): Repository owner.
        - repo_name (str): Repository name.
        - logger: Logger instance for logging.

        Returns:
        - description (str): Description of the issue.
        """
        token = os.environ.get(f'GITHUB_TOKEN{self.TOKEN_COUNTER}')
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}"
        headers = {"Authorization": f"token {token}"} if token else {}
        logger.info(f"Fetching description for issue #{issue_number}")
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                description = response.json().get('body', f"Issue #{issue_number}")
                logger.debug(f"Issue #{issue_number} description fetched successfully.")
                return description
            elif response.status_code == 403:
                self.TOKEN_COUNTER  = (self.TOKEN_COUNTER + 1) % 10
                token = os.environ.get(f'GITHUB_TOKEN{self.TOKEN_COUNTER}')
                headers = {"Authorization": f"token {token}"} if token else {}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    description = response.json().get('body', f"Issue #{issue_number}")
                    logger.debug(f"Issue #{issue_number} description fetched successfully.")
                    return description
                else:
                    logger.warning(f"Last issue not found or access denied. Status Code: {response.status_code}")
                    return -1
            else:
                logger.warning(f"Issue #{issue_number} not found or access denied. Status Code: {response.status_code}")
                return f"Issue #{issue_number} (not found)"
        except Exception as e:
            logger.error(f"Error fetching issue description for #{issue_number}: {e}")
            return f"Issue #{issue_number} (error fetching description)"

    def get_last_closed_issue(self, repo, owner, repo_name, logger):
        """
        Fetch the description of a GitHub issue.

        Parameters:
        - issue_number (int): Issue number.
        - owner (str): Repository owner.
        - repo_name (str): Repository name.
        - logger: Logger instance for logging.

        Returns:
        - description (str): Description of the issue.
        """
        token = os.environ.get(f'GITHUB_TOKEN{self.TOKEN_COUNTER}')
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
        headers = {"Authorization": f"token {token}"} if token else {}
        params = {
            "state": "closed",
            "per_page": "1",
            "direction": "desc"
        }
        logger.info(f"Fetching the last close issue.")
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                last_issue = response.json()[0]["number"]
                return last_issue
            elif response.status_code == 403:
                self.TOKEN_COUNTER  = (self.TOKEN_COUNTER + 1) % 10
                token = os.environ.get(f'GITHUB_TOKEN{self.TOKEN_COUNTER}')
                headers = {"Authorization": f"token {token}"} if token else {}
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    last_issue = response.json()[0]["number"]
                    return last_issue
                else:
                    logger.warning(f"Last issue not found or access denied. Status Code: {response.status_code}")
                    return -1
            else:
                logger.warning(f"Last issue not found or access denied. Status Code: {response.status_code}")
                return -1
        except Exception as e:
            logger.error(f"Error fetching last issue: {e}")
            return -1




    def get_codebase_before_commit(self, repo, commit, logger):
        """
        Extract the codebase right before the specified commit.

        Parameters:
        - repo: Git repository object.
        - commit: Git commit object.
        - logger: Logger instance for logging.

        Returns:
        - codebase (str): Concatenated contents of all relevant files before the commit.
        """
        logger.info(f"Extracting codebase before commit: {commit.hexsha}")
        try:
            parents = commit.parents
            if not parents:
                logger.warning(f"Commit {commit.hexsha} has no parents. Returning empty codebase.")
                return {}
            parent_commit = parents[0]
            codebase = {}
            tree = parent_commit.tree
            total_len = 0
            for blob in tree.traverse():
                if blob.type == 'blob':
                    try:
                        # Filter for specific file types if necessary
                        if not blob.path.endswith(('.py', '.js', '.java', '.cpp', '.c', '.rb', '.go', '.ts', '.dart', '.html')):
                            continue

                        # Decode the blob content as UTF-8 text
                        content = blob.data_stream.read().decode('utf-8')
                        total_len += len(content)
                        codebase[blob.path] = content
                    except UnicodeDecodeError:
                        # Skip binary files or files with decoding issues
                        logger.debug(f"Skipping non-text file: {blob.path}")
                        continue
            # print('='*10)
            # print(total_len)
            # print('='*10)

            logger.info(f"Extracted codebase before commit {commit.hexsha}")
            return codebase
        except Exception as e:
            logger.error(f"Error extracting codebase before commit {commit.hexsha}: {e}")
            return {}

    def get_codebase_after_commit(self, repo, commit, logger):
        """
        Extract the codebase right after the specified commit.

        Parameters:
        - repo: Git repository object.
        - commit: Git commit object.
        - logger: Logger instance for logging.

        Returns:
        - codebase (str): Concatenated contents of all relevant files before the commit.
        """
        logger.info(f"Extracting codebase after commit: {commit.hexsha}")
        try:
        
            codebase = {}
            tree = commit.tree
            if not tree:
                logger.warning(f"Commit {commit.hexsha} has no tree. Returning empty codebase.")
                return {}
            total_len = 0
            for blob in tree.traverse():
                if blob.type == 'blob':
                    try:
                        # Filter for specific file types if necessary
                        if not blob.path.endswith(('.py', '.js', '.java', '.cpp', '.c', '.rb', '.go', '.ts')):
                            continue

                        # Decode the blob content as UTF-8 text
                        content = blob.data_stream.read().decode('utf-8')
                        total_len += len(content)
                        codebase[blob.path] = content
                    except UnicodeDecodeError:
                        # Skip binary files or files with decoding issues
                        logger.debug(f"Skipping non-text file: {blob.path}")
                        continue

            logger.info(f"Extracted codebase after commit {commit.hexsha}")
            return codebase
        except Exception as e:
            logger.error(f"Error extracting codebase after commit {commit.hexsha}: {e}")
            return {}

