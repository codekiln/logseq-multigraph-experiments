title:: Python/sorted

- [Sorting HOW TO — Python 3.10.3 documentation](https://docs.python.org/3/howto/sorting.html)
	- default for `sorted` is ascending
- Ex01 - sort by last letter
	- ```python
	  words = ['cherry', 'cake', 'Michigan', 'transcript']
	  sorted(words, key = lambda x: x[::-1])
	  # ['cake', 'Michigan', 'transcript', 'cherry']
	  ```
		- via [How to use sorted() and sort() in Python](https://www.knowledgehut.com/blog/programming/python-sort-and-sorted)
- [Sorting HOW TO — Python 3.10.4 documentation](https://docs.python.org/3/howto/sorting.html)
	- Usually it’s less convenient than [`sorted()`](../library/functions.html#sorted "sorted") - but if you don’t need the original list, it’s slightly more efficient.
	- \>>>
	- the [`list.sort()`](../library/stdtypes.html#list.sort "list.sort") method is only defined for lists
	- the [`sorted()`](../library/functions.html#sorted "sorted") function accepts any iterable.
	- \>>>
	- Both [`list.sort()`](../library/stdtypes.html#list.sort "list.sort") and [`sorted()`](../library/functions.html#sorted "sorted") have a __key__ parameter to specify a function (or other callable) to be called on each list element prior to making comparisons.
	- ## Operator Module Functions[¶](#operator-module-functions "Permalink to this headline")
	- The key-function patterns shown above are very common, so Python provides convenience functions to make accessor functions easier and faster. The [`operator`](../library/operator.html#module-operator "operator: Functions corresponding to the standard operators.") module has [`itemgetter()`](../library/operator.html#operator.itemgetter "operator.itemgetter"), [`attrgetter()`](../library/operator.html#operator.attrgetter "operator.attrgetter"), and a [`methodcaller()`](../library/operator.html#operator.methodcaller "operator.methodcaller") function.
	- \>>>```\>>> from operator import itemgetter, attrgetter
	- \>>> sorted(student\_tuples, key\=itemgetter(2))
	- \[('dave', 'B', 10), ('jane', 'B', 12), ('john', 'A', 15)\]
	- \>>> sorted(student\_objects, key\=attrgetter('age'))
	- \[('dave', 'B', 10), ('jane', 'B', 12), ('john', 'A', 15)\]```
	- \>>>```\>>>```
	- sorted(student\_tuples, key\=itemgetter(1,2)) \[('john', 'A', 15), ('dave', 'B', 10), ('jane', 'B', 12)\] \>>> sorted(student\_objects, key\=attrgetter('grade', 'age'))
	- ## Ascending and Descending[¶](#ascending-and-descending "Permalink to this headline")
	- Both [`list.sort()`](../library/stdtypes.html#list.sort "list.sort") and [`sorted()`](../library/functions.html#sorted "sorted") accept a __reverse__ parameter with a boolean value. This is used to flag descending sorts. For example, to get the student data in reverse __age__ order:
	- \>>>```\>>> sorted(student\_tuples, key\=itemgetter(2), reverse\=True)
	- \[('john', 'A', 15), ('jane', 'B', 12), ('dave', 'B', 10)\]
	- \>>> sorted(student\_objects, key\=attrgetter('age'), reverse\=True)
	- \[('john', 'A', 15), ('jane', 'B', 12), ('dave', 'B', 10)\]```
	- Sorts are guaranteed to be [stable](https://en.wikipedia.org/wiki/Sorting_algorithm#Stability). That means that when multiple records have the same key, their original order is preserved.
	- \>>>