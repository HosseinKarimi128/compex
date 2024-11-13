import git # type: ignore

def get_selected_commits(repo, selected_commit_hashes):
    """
    Retrieve commit objects for the selected commit hashes.

    Parameters:
    - repo: Git repository object.
    - selected_commit_hashes (list): List of commit hashes to include.

    Returns:
    - List of commit objects.
    """
    commits = []
    for commit_hash in selected_commit_hashes:
        try:
            commit = repo.commit(commit_hash)
            commits.append(commit)
        except git.exc.BadName:
            print(f"Warning: Commit {commit_hash} not found in the repository.")
    return commits

def get_codebase_at_commit(repo, commit):
    """
    Extract the entire codebase as a single string from the specified commit.

    Parameters:
    - repo: Git repository object.
    - commit: Git commit object.

    Returns:
    - String containing the concatenated contents of all text-based files.
    """
    codebase = ""
    tree = commit.tree
    for blob in tree.traverse():
        if blob.type == 'blob':
            try:
                # Filter for specific file types if necessary
                # For example, only include .py, .js files, etc.
                if not blob.path.endswith(('.py', '.js', '.java', '.cpp', '.c', '.rb', '.go', '.ts')):
                    continue
                
                # Decode the blob content as UTF-8 text
                content = blob.data_stream.read().decode('utf-8')
                codebase += content + "\n"
            except UnicodeDecodeError:
                # Skip binary files or files with decoding issues
                continue
    return codebase
