import radon.complexity as radon_complexity # type: ignore
import radon.metrics as radon_metrics # type: ignore
import radon.raw as radon_raw # type: ignore
import subprocess
import tempfile
import os
import json

def calculate_loc(codebase):
    """
    Calculate Lines of Code (LOC) excluding comments and blank lines.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - loc (int): Number of lines of code.
    """
    try:
        raw_metrics = radon_raw.analyze(codebase)
        return raw_metrics.loc
    except Exception as e:
        return None

def calculate_cyclomatic_complexity(codebase):
    """
    Calculate Cyclomatic Complexity using Radon.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - cyclomatic_complexity (float): Average cyclomatic complexity.
    """
    try:
        complexities = radon_complexity.cc_visit(codebase)
        if not complexities:
            return 0
        total = sum(block.complexity for block in complexities)
        average = total / len(complexities)
        return round(average, 2)
    except Exception as e:
        return None

def calculate_halstead_metrics(codebase):
    """
    Calculate Halstead Metrics using Radon.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - halstead_metrics (dict): Dictionary containing Halstead metrics.
    """
    try:
        metrics = radon_metrics.h_visit(codebase)
        if not metrics:
            return {}
        # Assuming one module, get the first metrics object
        h = metrics[0]
        return {
            'halstead_length': h.length,
            'halstead_vocabulary': h.vocabulary,
            'halstead_volume': round(h.volume, 2),
            'halstead_difficulty': round(h.difficulty, 2),
            'halstead_effort': round(h.effort, 2)
        }
    except Exception as e:
        return {}

def calculate_maintainability_index(codebase):
    """
    Calculate Maintainability Index using Radon.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - maintainability_index (float): Maintainability Index score.
    """
    try:
        mi = radon_metrics.mi_visit(codebase)
        if not mi:
            return None
        # Assuming one module, get the first MI score
        return round(mi[0].mi, 2)
    except Exception as e:
        return None

def calculate_code_duplication(repo_path):
    """
    Calculate Code Duplication using Flake8 with flake8-duplicates.

    Parameters:
    - repo_path (str): Path to the Git repository.

    Returns:
    - duplication (int): Number of duplicated blocks.
    """
    try:
        # Create a temporary file to store flake8 output
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmpfile:
            result = subprocess.run(
                ['flake8', '--select=D', repo_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            tmpfile.write(result.stdout)
            tmpfile_path = tmpfile.name

        # Parse the output to count duplicated blocks
        duplication_count = 0
        with open(tmpfile_path, 'r') as f:
            for line in f:
                if 'D' in line:
                    duplication_count += 1

        os.remove(tmpfile_path)
        return duplication_count
    except Exception as e:
        return None

def calculate_coupling_cohesion(codebase):
    """
    Placeholder for Coupling and Cohesion metrics.
    Implementing these metrics requires deeper static analysis which is beyond this scope.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - coupling (float): Coupling metric.
    - cohesion (float): Cohesion metric.
    """
    # Implementing actual coupling and cohesion metrics would require
    # detailed static analysis possibly using other specialized tools.
    # For simplicity, we'll return dummy values.
    return {
        'coupling': None,
        'cohesion': None
    }

def get_all_metrics(codebase, repo_path):
    """
    Compute all metrics for the given codebase.

    Parameters:
    - codebase (str): The entire codebase as a single string.
    - repo_path (str): Path to the Git repository.

    Returns:
    - metrics (dict): Dictionary containing all computed metrics.
    """
    metrics = {}
    metrics['LOC'] = calculate_loc(codebase)
    metrics['CyclomaticComplexity'] = calculate_cyclomatic_complexity(codebase)
    metrics['HalsteadMetrics'] = calculate_halstead_metrics(codebase)
    metrics['MaintainabilityIndex'] = calculate_maintainability_index(codebase)
    metrics['CodeDuplication'] = calculate_code_duplication(repo_path)
    coupling_cohesion = calculate_coupling_cohesion(codebase)
    metrics.update(coupling_cohesion)
    return metrics
