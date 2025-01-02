# 02 - use individual symlinked pages 
- In this model of multi-graph, one would sync individual pages over using a symlink for each page.
- See the docstring of the `sync_dependencies.py` script for a basic theory of how this could work.
- Unfortunately, it seems as though 
  - using symlinks for individual files, the contents of the `python` pages don't show up in the `work` graph
  - open a Logseq graph to the `work` directory and select work -> Re-Index
    - expected behavior: logseq would follow the symlinks and index those pages
    - observed behavior (0.10.9): the symlinked files appear in the graph as pages, and one can click on them,
      however the contents of the pages are not visible
