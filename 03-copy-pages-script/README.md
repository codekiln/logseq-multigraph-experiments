- ### 03-copy-pages-script 
	- see the docstring to [sync_dependencies.py](./sync_dependencies.py) for a more full description of this prototype
	- #### **assumptions**
		- multiple Logseq Graphs are in the same directory as sibling directories
		- each Logseq Graph may optionally put in it's root directory a `dependencies.json` that expresses the files it wishes to be sync'd over from another graph. A `sync_dependencies.py` script will use that to implement the dependencies.
			- #Example
				- logseq-garden/
					-
					  ```
					  .
					  ├── README.md
					  ├── python
					  │   ├── journals
					  │   ├── logseq
					  │   │   ├── config.edn
					  │   │   └── custom.css
					  │   └── pages
					  │       ├── Python.md
					  │       ├── Python___pathlib.md
					  │       ├── Python___sort.md
					  │       ├── Python___sorted.md
					  │       └── contents.md
					  ├── sync_dependencies.py
					  └── work
					      ├── dependencies.json
					      ├── journals
					      ├── logseq
					      │   ├── config.edn
					      │   └── custom.css
					      └── pages
					          ├── contents.md
					          └── work.md
					  
					  ```
				- `work/dependencies.py`
					-
					  ```json
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
					  ```
	- #### After running `sync_dependencies.py`:
		-
		  ```
		  .
		  ├── README.md
		  ├── python
		  │   ├── journals
		  │   ├── logseq
		  │   │   ├── config.edn
		  │   │   └── custom.css
		  │   └── pages
		  │       ├── Python.md
		  │       ├── Python___pathlib.md
		  │       ├── Python___sort.md
		  │       ├── Python___sorted.md
		  │       └── contents.md
		  ├── sync_dependencies.py
		  └── work
		      ├── dependencies.json
		      ├── journals
		      ├── logseq
		      │   ├── config.edn
		      │   └── custom.css
		      └── pages
		          ├── contents.md
		          ├── Python.md
		          ├── Python___pathlib.md
		          ├── Python___sort.md
		          ├── Python___sorted.md
		          └── work.md
		  
		  ```
	-
