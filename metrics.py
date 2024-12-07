import radon.complexity as radon_complexity # type: ignore
import radon.metrics as radon_metrics # type: ignore
import radon.raw as radon_raw # type: ignore
import subprocess
import tempfile
import os
import math
import re
import json

def calculate_loc(codebase):
    """
    Calculate Lines of Code (LOC) excluding comments and blank lines.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - loc (int): Number of lines of code.
    """
    comment_pattern = r"""
        ^\s*//.*$              |  # Single-line comments (e.g., Java, C, C++)
        ^\s*\#.*$              |  # Single-line comments (e.g., Python, Ruby)
        ^\s*$                  |  # Blank lines
        ^\s*/\*[\s\S]*?\*/\s*$ |  # Multi-line comments (e.g., Java, C, Go)
        \s*(\"\"\"|\'\'\')[\s\S]*?(\"\"\"|\'\'\')   # Docstrings for Python
    """
    
    combined_pattern = re.compile(comment_pattern, re.MULTILINE | re.VERBOSE)
    
    loc = 0
    for code in codebase.values():
    
        filtered_code = re.sub(combined_pattern, '', code)
        loc += sum(1 for line in filtered_code.splitlines() if line.strip())
    
    return loc

def calculate_cyclomatic_complexity(codebase):
    """
    Calculate Cyclomatic Complexity using Radon.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - cyclomatic_complexity (float): Average cyclomatic complexity.
    """

    total_files = len(codebase)
    syntax_errors = 0
    complexity = []

    for code in codebase.values():
    
        try:
            
            complexities = radon_complexity.cc_visit(code)

            total = sum(block.complexity for block in complexities)
            average = total / len(complexities)
            complexity.append(round(average, 2))
    
        except Exception as e:
            syntax_errors += 1
            continue
        
    if syntax_errors == total_files:
        print("all codes are broken!")
        return {}
    
    print(f"broken files percentage for complexity: {100 * syntax_errors / total_files}%")
    average = sum(complexity) / len(complexity)
    return average


def calculate_halstead_metrics(codebase):
    """
    Calculate Halstead Metrics using Radon.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - halstead_metrics (dict): Dictionary containing Halstead metrics.
    """
    total_files = len(codebase)
    syntax_errors = 0
    halstead_length = 0
    halstead_vocabulary = 0
    halstead_volume = 0
    halstead_difficulty = 0
    halstead_effort = 0

    for code in codebase.values():
    
        try:
            
            metrics = radon_metrics.h_visit(code)

            h = metrics[0]
            halstead_length += int(h.length)
            halstead_vocabulary += int(h.vocabulary)
            halstead_volume += int(round(h.volume, 2))
            halstead_difficulty += int(round(h.difficulty, 2))
            halstead_effort += int(round(h.effort, 2))
    
        except Exception as e:
            syntax_errors += 1
            continue
        
    if syntax_errors == total_files:
        print("all codes are broken!")
        return {}
    
    print(f"broken files percentage for halstead: {100 * syntax_errors / total_files}%")
    output = {
        "halstead_length" : halstead_length,
        "halstead_vocabulary" : halstead_vocabulary,
        "halstead_volume" : halstead_volume,
        "halstead_difficulty" : halstead_difficulty,
        "halstead_effort" : halstead_effort
    }
    return output

def calculate_maintainability_index(halstead_volume, complexity, sloc, comments):
    """
    Calculate Maintainability Index using Radon.

    Parameters:
    - codebase (str): The entire codebase as a single string.

    Returns:
    - maintainability_index (float): Maintainability Index score.
    """
    if halstead_volume is None:
        return None
    if any(metric <= 0 for metric in (halstead_volume, sloc)):
        return 100.0
    sloc_scale = math.log(sloc)
    volume_scale = math.log(halstead_volume)
    comments_scale = math.sqrt(2.46 * math.radians(comments))
    # Non-normalized MI
    nn_mi = (
        171 * 2
        - 5.2 * volume_scale
        - 0.23 * complexity
        - 16.2 * sloc_scale
        + 50 * math.sin(comments_scale)
    )
    return min(max(0.0, nn_mi * 100 / 171.0), 100.0)


def calculate_comment_count(codebase):
    """
    Count the number of comment lines in a codebase for a specific language.
    
    Parameters:
        code (str): The source code as a string.
        language (str): The programming language (e.g., "python", "java", "c").
    
    Returns:
        int: The number of comment lines.
    """
    comment_pattern = r"""
        (?://.*)          |
        (?:\#.*)          |
        (?:/\*[\s\S]*?\*/)
    """
    
    combined_pattern = re.compile(comment_pattern, re.VERBOSE)
    splitted_matches = []

    for code in codebase.values():
        
        matches = re.findall(combined_pattern, code)
        
        for m in matches:
            if "\n" in m:
                splitted_matches.extend(m.split("\n"))
            else:
                splitted_matches.append(m)
    return len(splitted_matches)

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

    metrics["comments"] = calculate_comment_count(codebase)
    halstead_volume = metrics['HalsteadMetrics']["halstead_volume"] if "halstead_volume" in metrics['HalsteadMetrics'] else None
    metrics['MaintainabilityIndex'] = calculate_maintainability_index(halstead_volume,
                                                                      metrics['CyclomaticComplexity'],
                                                                      metrics['LOC'],
                                                                      metrics["comments"])
    metrics['CodeDuplication'] = calculate_code_duplication(repo_path)
    coupling_cohesion = calculate_coupling_cohesion(codebase)
    metrics.update(coupling_cohesion)
    return metrics
