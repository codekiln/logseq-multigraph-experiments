#!/usr/bin/env python3
"""
sync_dependencies.py

For each subdirectory in the current directory that contains a dependencies.json,
parse it and sync the specified namespaces from the specified source graphs.

Example Directory Structure:
.
├── python
│   ├── pages
│   │   ├── Python.md
│   │   ├── Python___pathlib.md
│   │   ...
│   └── logseq
│       ├── config.edn
│       └── custom.css
├── work
│   ├── dependencies.json
│   ├── pages
│   │   ├── contents.md
│   │   └── work.md
│   └── logseq
│       ├── config.edn
│       └── custom.css
└── sync_dependencies.py

After running, for example, the 'work' graph might have pulled in the 'Python' namespace
pages from the 'python' graph, subject to the JSON config in 'work/dependencies.json'.
"""

import json
import os


def copy_file_if_needed(
    source_file_path: str, target_file_path: str, overwrite_if_newer: bool
) -> None:
    """
    Copy source_file_path to target_file_path if:
      - the target file doesn't exist, OR
      - overwrite_if_newer is True AND the source is strictly newer than target.

    Uses binary read/write (works fine for text as well).
    """
    if not os.path.exists(source_file_path):
        # Shouldn't happen in normal usage, but just in case.
        print(f"Source file does not exist: {source_file_path}")
        return

    # If the target does NOT exist, always copy
    if not os.path.exists(target_file_path):
        print(f"Copying new file:\n  {source_file_path}\n-> {target_file_path}")
        _do_copy(source_file_path, target_file_path)
        return

    # If the target exists and we don't allow overwrites, do nothing
    if not overwrite_if_newer:
        print(f"Skipping file (overwrite_if_newer=False): {target_file_path}")
        return

    # If the target exists and we do allow overwrites, compare mtimes
    source_mtime = os.path.getmtime(source_file_path)
    target_mtime = os.path.getmtime(target_file_path)
    if source_mtime > target_mtime:
        print(f"Overwriting older file:\n  {source_file_path}\n-> {target_file_path}")
        _do_copy(source_file_path, target_file_path)
    else:
        print(f"Target is up to date, skipping: {target_file_path}")


def _do_copy(src_path: str, dst_path: str) -> None:
    """Helper function that actually does the file copy."""
    # Ensure parent dir exists
    dst_dir = os.path.dirname(dst_path)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)

    # Binary copy
    with open(src_path, "rb") as src_f, open(dst_path, "wb") as dst_f:
        dst_f.write(src_f.read())


def sync_graph_dependencies(target_graph_dir: str) -> None:
    """
    Given a path to a target graph directory (which presumably has a dependencies.json),
    read that dependencies file and carry out the specified file sync logic.
    """
    dependencies_path = os.path.join(target_graph_dir, "dependencies.json")
    if not os.path.isfile(dependencies_path):
        return  # No dependencies.json here; do nothing

    try:
        with open(dependencies_path, "r", encoding="utf-8") as f:
            deps_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading/parsing {dependencies_path}: {e}")
        return

    if "dependent-graphs" not in deps_data:
        print(f"No 'dependent-graphs' key found in {dependencies_path}; skipping.")
        return

    # For each dependent-graph config in the JSON, sync the namespaces
    for dependent_graph in deps_data["dependent-graphs"]:
        local_graph_path = dependent_graph.get("local-graph-path")
        namespaces_to_sync = dependent_graph.get("namespaces-to-sync", [])

        if not local_graph_path:
            print("No local-graph-path provided; skipping this entry.")
            continue

        # Construct the absolute path to the source graph
        source_graph_dir = os.path.abspath(
            os.path.join(target_graph_dir, local_graph_path)
        )
        # The target graph is the one that holds the dependencies.json
        target_graph_pages_dir = os.path.join(target_graph_dir, "pages")
        source_graph_pages_dir = os.path.join(source_graph_dir, "pages")

        # If source doesn't have a pages folder, there's nothing to sync
        if not os.path.isdir(source_graph_pages_dir):
            print(f"No pages directory in source graph: {source_graph_pages_dir}")
            continue

        for namespace_config in namespaces_to_sync:
            source_namespace = namespace_config["source-namespace-name"]
            target_namespace = namespace_config["target-namespace-name"]
            overwrite_if_source_is_newer = namespace_config.get(
                "overwrite-if-source-is-newer", False
            )

            # For each file in the source pages, if it begins with:
            #   source_namespace + ".md"   OR
            #   source_namespace + "___"
            # we copy it over to the target, substituting the prefix
            # with target_namespace if they differ.
            for fname in os.listdir(source_graph_pages_dir):
                # Check if it starts with "source_namespace" in the relevant ways
                is_exact = fname == f"{source_namespace}.md"
                is_subpage = fname.startswith(f"{source_namespace}___")

                if not (is_exact or is_subpage):
                    continue

                source_file_path = os.path.join(source_graph_pages_dir, fname)
                # Replace only the first occurrence of source_namespace with target_namespace
                # in the filename (so e.g. Python___pathlib.md => Python___pathlib.md if same,
                # or if source_namespace=Python, target_namespace=MyPy => MyPy___pathlib.md)
                new_fname = fname.replace(source_namespace, target_namespace, 1)
                target_file_path = os.path.join(target_graph_pages_dir, new_fname)

                # Perform the copy if needed
                copy_file_if_needed(
                    source_file_path, target_file_path, overwrite_if_source_is_newer
                )


def main():
    """
    Main entry point. Iterate over all subdirectories in the current directory.
    If a subdir has a dependencies.json, run sync_graph_dependencies on it.
    """
    current_dir = os.getcwd()
    # We also might want to skip certain directories (.git, etc.) if desired
    for entry in os.listdir(current_dir):
        full_path = os.path.join(current_dir, entry)
        if os.path.isdir(full_path):
            # Check if there's a dependencies.json in this folder
            dependencies_file = os.path.join(full_path, "dependencies.json")
            if os.path.isfile(dependencies_file):
                print(f"\n=== Processing dependencies in: {full_path} ===")
                sync_graph_dependencies(full_path)
    print("\nDone.")


if __name__ == "__main__":
    main()
