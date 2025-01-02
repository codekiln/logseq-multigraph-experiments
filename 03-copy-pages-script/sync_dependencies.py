#!/usr/bin/env python3
"""
sync_dependencies.py

This script scans all subdirectories of the current working directory. For each
subdirectory that contains a `dependencies.json`, it parses that file and carries
out a "namespace sync" from one or more source (local) Logseq graphs to the
target Logseq graph (the one containing the `dependencies.json`).

-------------------------------------------------------------------------------
DEPENDENCIES.JSON FORMAT:
-------------------------------------------------------------------------------
A typical `dependencies.json` file might look like:

{
    "dependent-graphs": [
        {
            "local-graph-path": "../python",
            "namespaces-to-sync": [
                {
                    "source-namespace-name": "Python",
                    "target-namespace-name": "Python",
                    "overwrite-if-source-is-newer": true
                }
            ]
        }
    ]
}

- "local-graph-path" points to the *relative* directory of the source graph.
- "namespaces-to-sync" is a list of namespace-sync configs, each of which:
  - "source-namespace-name": The namespace prefix in the source graph (e.g. "Python").
  - "target-namespace-name": The namespace prefix to use in the target (e.g. "Python").
  - "overwrite-if-source-is-newer": A boolean indicating whether an existing file in the
    target should be overwritten only if the source file's modification time is strictly
    newer.

-------------------------------------------------------------------------------
WHAT GETS COPIED:
-------------------------------------------------------------------------------
For each namespace-to-sync entry, the script looks inside the `pages` directory
of the source graph and copies all `.md` files matching either:
  1) `<source-namespace-name>.md`, or
  2) `<source-namespace-name>___*.md`

The prefix `<source-namespace-name>` in the filename is replaced with
`<target-namespace-name>` in the copy. Thus, for example, if the source file
is `Python___sort.md` and the namespace is changed from "Python" to "MyPython",
the resulting target file might be `MyPython___sort.md`.

-------------------------------------------------------------------------------
OVERWRITING LOGIC:
-------------------------------------------------------------------------------
By default, if the target file already exists:
  - If "overwrite-if-source-is-newer" = false, we skip copying entirely.
  - If "overwrite-if-source-is-newer" = true, we compare file modification times
    and only overwrite if the source is strictly newer. Otherwise, we skip.

-------------------------------------------------------------------------------
PAGE-LEVEL ATTRIBUTES:
-------------------------------------------------------------------------------
If a file is copied or overwritten, the script opens the newly created target `.md`
file and prepends two attributes at the top:

  logseq-remote-page:: true
  logseq-remote-page-link:: logseq://graph/<SOURCE_GRAPH_NAME>?page=<ENCODED_PAGE_NAME>

Where:
  - <SOURCE_GRAPH_NAME> is derived from the source graph's directory name (e.g., "python").
  - <ENCODED_PAGE_NAME> is derived from the filename (minus `.md`), with every
    triple underscore (`___`) replaced by `/`, then URL-encoded. 
    For example, "Python___sort" becomes "Python/sort" => "Python%2Fsort".

Hence, a page originally named `Python___sort.md` in the source graph "python"
becomes a page named `Python___sort.md` in the target, and its frontmatter will
contain:
  
  logseq-remote-page:: true
  logseq-remote-page-link:: logseq://graph/python?page=Python%2Fsort

-------------------------------------------------------------------------------
EXAMPLE WORKFLOW:
-------------------------------------------------------------------------------
Suppose you have two graphs: `python/` and `work/`. The `work/` directory has
a `dependencies.json` referencing "../python" as the source. After running:

  python3 sync_dependencies.py

any `.md` files under `python/pages/` that start with "Python" will be copied into
`work/pages/`, potentially overwritten if newer, and will include the logseq-remote
page-level attributes inserted at the top of each file.

-------------------------------------------------------------------------------
DIRECTORY STRUCTURE (ILLUSTRATION):
-------------------------------------------------------------------------------
.
├── python
│   ├── pages
│   │   ├── Python.md
│   │   ├── Python___pathlib.md
│   │   ├── Python___sort.md
│   │   └── ...
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

After running the script, for instance, the `work/pages/` directory may have
pulled in the "Python" namespace pages from the "python" graph, subject to the
logic and overwriting rules set forth in `work/dependencies.json`.

-------------------------------------------------------------------------------
"""

import json
import os
from urllib.parse import quote


def copy_file_if_needed(
    source_file_path: str, target_file_path: str, overwrite_if_newer: bool
) -> bool:
    """
    Copy source_file_path to target_file_path if necessary, respecting 'overwrite_if_newer'.
    Returns True if a copy actually occurred (either new file or overwriting).
    Returns False if skipping.
    """
    if not os.path.exists(source_file_path):
        print(f"Source file does not exist: {source_file_path}")
        return False

    # If the target does NOT exist, always copy
    if not os.path.exists(target_file_path):
        print(f"Copying new file:\n  {source_file_path}\n-> {target_file_path}")
        _do_copy(source_file_path, target_file_path)
        return True

    # If the target exists and we don't allow overwrites, do nothing
    if not overwrite_if_newer:
        print(f"Skipping file (overwrite_if_newer=False): {target_file_path}")
        return False

    # If the target exists and we do allow overwrites, compare mtimes
    source_mtime = os.path.getmtime(source_file_path)
    target_mtime = os.path.getmtime(target_file_path)
    if source_mtime > target_mtime:
        print(f"Overwriting older file:\n  {source_file_path}\n-> {target_file_path}")
        _do_copy(source_file_path, target_file_path)
        return True
    else:
        print(f"Target is up to date, skipping: {target_file_path}")
        return False


def _do_copy(src_path: str, dst_path: str) -> None:
    """Helper function that actually does the file copy, creating directories as needed."""
    dst_dir = os.path.dirname(dst_path)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)

    with open(src_path, "rb") as src_f, open(dst_path, "wb") as dst_f:
        dst_f.write(src_f.read())


def _prepend_page_level_attributes(
    target_file_path: str, source_graph_name: str
) -> None:
    """
    Open the newly copied file at `target_file_path`, determine the "page name"
    from the filename, and prepend two lines:

      logseq-remote-page:: true
      logseq-remote-page-link:: logseq://graph/<SOURCE_GRAPH_NAME>?page=<URL_ENCODED_PAGE_NAME>
    """
    # Figure out the base name without .md
    base_name = os.path.splitext(os.path.basename(target_file_path))[0]
    page_name = _derive_page_name(base_name)

    # URL-encode all special characters (including slash)
    encoded_page_name = quote(page_name, safe="")
    logseq_url = f"logseq://graph/{source_graph_name}?page={encoded_page_name}"

    # Read the existing contents
    with open(target_file_path, "r", encoding="utf-8") as f:
        old_content = f.read()

    # Prepend the page-level attributes
    new_content = (
        f"logseq-remote-page:: true\n"
        f"logseq-remote-page-link:: {logseq_url}\n\n"
        f"{old_content}"
    )

    # Write back
    with open(target_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def _derive_page_name(base_name: str) -> str:
    """
    We interpret triple underscores as subpage slashes.

    Examples:
      "Python___sort"       => "Python/sort"        => URL-encoded to "Python%2Fsort"
      "Python___sorted"     => "Python/sorted"      => "Python%2Fsorted"
      "Python___foo___bar"  => "Python/foo/bar"

    If your environment only wants the first triple underscore replaced,
    or some other convention, adjust accordingly.
    """
    return base_name.replace("___", "/")


def sync_graph_dependencies(target_graph_dir: str) -> None:
    """
    Given a path to a target graph directory (which presumably has a dependencies.json),
    read that file and carry out the specified file sync logic. Then, for each newly
    copied/overwritten file, prepend the page-level attributes.
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

        source_graph_dir = os.path.abspath(
            os.path.join(target_graph_dir, local_graph_path)
        )
        # This is used in the final logseq:// URL
        source_graph_name = os.path.basename(os.path.normpath(source_graph_dir))

        target_graph_pages_dir = os.path.join(target_graph_dir, "pages")
        source_graph_pages_dir = os.path.join(source_graph_dir, "pages")

        if not os.path.isdir(source_graph_pages_dir):
            print(f"No pages directory in source graph: {source_graph_pages_dir}")
            continue

        for namespace_config in namespaces_to_sync:
            source_namespace = namespace_config["source-namespace-name"]
            target_namespace = namespace_config["target-namespace-name"]
            overwrite_if_source_is_newer = namespace_config.get(
                "overwrite-if-source-is-newer", False
            )

            # Copy each relevant .md file
            for fname in os.listdir(source_graph_pages_dir):
                is_exact = fname == f"{source_namespace}.md"
                is_subpage = fname.startswith(f"{source_namespace}___")
                if not (is_exact or is_subpage):
                    continue

                source_file_path = os.path.join(source_graph_pages_dir, fname)
                # Replace the FIRST occurrence of source_namespace with target_namespace in the filename
                new_fname = fname.replace(source_namespace, target_namespace, 1)
                target_file_path = os.path.join(target_graph_pages_dir, new_fname)

                # Perform the copy if needed
                did_copy = copy_file_if_needed(
                    source_file_path, target_file_path, overwrite_if_source_is_newer
                )

                # If we actually copied/overwrote the file, then prepend the page-level attributes
                if did_copy:
                    _prepend_page_level_attributes(target_file_path, source_graph_name)


def main():
    """
    Main entry point. Iterate over all subdirectories in the current directory.
    If a subdir has a dependencies.json, run sync_graph_dependencies on it.
    """
    current_dir = os.getcwd()
    for entry in os.listdir(current_dir):
        full_path = os.path.join(current_dir, entry)
        if os.path.isdir(full_path):
            dependencies_file = os.path.join(full_path, "dependencies.json")
            if os.path.isfile(dependencies_file):
                print(f"\n=== Processing dependencies in: {full_path} ===")
                sync_graph_dependencies(full_path)
    print("\nDone.")


if __name__ == "__main__":
    main()
