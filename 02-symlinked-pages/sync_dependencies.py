#!/usr/bin/env python3

"""
sync_dependencies.py

Usage:
    1. Place this script in the same directory that contains multiple subdirectories,
       each potentially representing a Logseq graph (i.e., each has a `logseq/` folder).
    2. When run, this script will:
       - Find all subdirectories that contain a `logseq/` folder.
       - For each such subdirectory (call it a 'graph'):
         * If that 'graph' has a `dependencies.json`, parse it.
         * Build an internal dependency graph to detect cycles.
       - If no cycles are detected, for each 'graph' that has dependencies:
         * Symlink files from the dependent graphs’ pages/ folder into this graph’s pages/ folder
           according to the rules in `dependencies.json` (matching prefixes, etc.).

Example `dependencies.json` structure:
{
  "dependent-graphs": [
    {
      "local-graph-path": "../python",
      "local-folder": "python",
      "only-files-beginning-with": "Python"
    }
  ]
}

Explanation of fields:
- local-graph-path: Relative path from the current graph's directory to another Logseq graph's directory.
- local-folder: (not strictly necessary if you only rely on path) A descriptive name of that remote graph folder.
- only-files-beginning-with: A string prefix (or could be multiple if extended in the future) for files to be symlinked.

Cycle detection:
- If graph A references graph B, and graph B references graph A (directly or transitively), we have a cycle.
- In that case, this script raises an Exception and aborts.

NOTE: This script is intentionally cautious about symlinks:
    - If a symlink with the same name already exists and points to the correct source, we leave it.
    - If a file or symlink with the same name exists but points elsewhere, we remove it and create a new symlink.
"""

import json
import os
import sys


def find_logseq_graphs(root_dir):
    """
    Return a list of absolute paths to subdirectories of root_dir that
    contain a `logseq/` folder (indicating a Logseq graph).
    """
    graphs = []
    for entry in os.listdir(root_dir):
        full_path = os.path.join(root_dir, entry)
        if os.path.isdir(full_path):
            logseq_path = os.path.join(full_path, "logseq")
            if os.path.isdir(logseq_path):
                graphs.append(full_path)
    return graphs


def load_dependencies(graph_folder):
    """
    If `dependencies.json` exists in graph_folder, parse and return the list of
    dependent-graphs. Otherwise, return an empty list.
    """
    dep_file = os.path.join(graph_folder, "dependencies.json")
    if not os.path.isfile(dep_file):
        return []
    with open(dep_file, "r") as f:
        data = json.load(f)
    return data.get("dependent-graphs", [])


def build_dependency_graph(graphs):
    """
    Build an adjacency list representing the dependencies of each graph.

    Returns:
        adj_list: dict where adj_list[graph_folder] = list of (dep_graph_folder, prefix)
                  for all dependent graphs discovered.
    """
    adj_list = {}
    for g in graphs:
        adj_list[g] = []  # Initialize adjacency list
        dep_specs = load_dependencies(g)
        for spec in dep_specs:
            local_graph_path = spec.get("local-graph-path")
            # We only care about the final location of the dependent graph:
            if not local_graph_path:
                continue
            # Convert to absolute path:
            dep_graph_path = os.path.normpath(os.path.join(g, local_graph_path))
            adj_list[g].append((dep_graph_path, spec))
    return adj_list


def detect_cycle_dfs(adj_list):
    """
    Detect cycles in the dependency graph using DFS.

    Raises:
        Exception if a cycle is found.
    """
    visited = set()
    rec_stack = set()  # nodes currently in recursion stack

    def dfs(v):
        visited.add(v)
        rec_stack.add(v)
        if v in adj_list:
            for neighbor, _ in adj_list[v]:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    raise Exception(
                        f"Cycle detected: {neighbor} is referenced cyclically."
                    )
        rec_stack.remove(v)

    for node in adj_list:
        if node not in visited:
            dfs(node)


def ensure_dir_exists(path):
    """Create the directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def link_files_with_prefix(source_dir, target_dir, prefix):
    """
    For each file in source_dir that starts with `prefix`, create/update symlink in target_dir.
    """
    if not os.path.isdir(source_dir):
        return  # Nothing to do if no source/pages folder
    ensure_dir_exists(target_dir)

    for fname in os.listdir(source_dir):
        if fname.startswith(prefix):
            source_path = os.path.join(source_dir, fname)
            target_path = os.path.join(target_dir, fname)
            # If target_path already exists, check if it is the correct symlink
            if os.path.islink(target_path):
                current_link = os.readlink(target_path)
                if os.path.abspath(current_link) == os.path.abspath(source_path):
                    # Already the correct symlink; do nothing
                    continue
                else:
                    # Remove incorrect link
                    os.remove(target_path)
            elif os.path.exists(target_path):
                # It's a real file or folder, not a link; remove it
                if os.path.isdir(target_path):
                    # If it's a folder, either skip or remove. Let's remove to keep it consistent.
                    # But be cautious with destructive actions in your environment.
                    # For a safer approach, you could rename or skip. Here we remove for clarity.
                    import shutil

                    shutil.rmtree(target_path)
                else:
                    os.remove(target_path)
            # Create the symlink
            os.symlink(os.path.abspath(source_path), target_path)


def sync_dependencies(adj_list):
    """
    For each graph, read its dependencies again (or reuse) and perform symlinking
    of matching files from the dependent graph's pages folder.
    """
    for graph_folder, deps in adj_list.items():
        # graph_folder is the 'target' graph
        pages_folder = os.path.join(graph_folder, "pages")
        for dep_graph_path, spec in deps:
            only_prefix = spec.get("only-files-beginning-with", "")
            # The "source" is the dependent graph's pages folder
            source_pages = os.path.join(dep_graph_path, "pages")
            link_files_with_prefix(source_pages, pages_folder, only_prefix)


def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    # 1. Find all subdirectories that are Logseq graphs
    graphs = find_logseq_graphs(root_dir)
    if not graphs:
        print("No Logseq graphs found.")
        sys.exit(0)

    # 2. Build adjacency list from dependencies.json
    adj_list = build_dependency_graph(graphs)

    # 3. Detect cycles
    try:
        detect_cycle_dfs(adj_list)
    except Exception as e:
        print("Dependency cycle detected:", e)
        sys.exit(1)

    # 4. Perform symlinking for all dependencies
    sync_dependencies(adj_list)
    print("Sync complete.")


if __name__ == "__main__":
    main()
