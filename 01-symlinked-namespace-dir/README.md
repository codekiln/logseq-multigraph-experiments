# 01 - try symlinking directories to namespaces doesn't quite work 
- In this model of multi-graph, one would symlink a directory to another graph's pages directory.
- This is the approach [Reddit user u/left_unsigned](https://www.reddit.com/user/left_unsigned/) suggested
  here: [Managing multiple graphs : r/logseq](https://www.reddit.com/r/logseq/comments/17w2gx9/comment/k9ipf3c/).
- in theory, if it worked like a normal directory, it would work, and the namespaced pages would be 
  sync'd over.  
- however, in practice, logseq doesn't seem to index subdirectories that are symlinks.
  - if you open up logseq graph in the `work` subdirectory, the pages from the `python` graph will not be 
    in the "all pages" view, even if you reindex.
- in addition, logseq automatically creates a `contents.md` file in both graphs, which 
  can't be symlinked over because it will link to a conflict because all files need to be 
  uniquely named in logseq; it will lead to an indexing error.
