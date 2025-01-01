# 02 - use individual symlinked pages 
- In this model of multi-graph, one would sync individual pages over.
- See the docstring of `sync_dependencies.py` for a basic proof of concept for how this could work.
- Unfortunately, it seems as though updating the source graph page does not end up 
  triggering an update of the dependended on page, even in the case of individual page links