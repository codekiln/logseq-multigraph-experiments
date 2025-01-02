title:: Python/sorted

- [Sorting HOW TO — Python 3.10.3 documentation](https://docs.python.org/3/howto/sorting.html)
	- Python Sorting HOWTO
		- Python lists have a built-in `.sort()` method and a `sorted()` function.
			- `.sort()` modifies the list in place.
			- `sorted()` returns a new sorted list.
		- **Key differences**:
			- `.sort()` is for sorting in place.
			- `sorted()` is for creating a new list.
		- Sorting Basics
			- Both `.sort()` and `sorted()` take two optional arguments:
				- `key`: A function that specifies a one-argument transformation.
				- `reverse`: A boolean to sort in descending order.
			- **Example**:
			  ~~~python
			  sorted([5, 2, 3, 1, 4])  # Output: [1, 2, 3, 4, 5]
			  ~~~
		- Key Functions
			- The `key` parameter specifies a function to transform each list element.
			- **Examples**:
				- Sort by absolute values:
				  ~~~python
				  sorted([-4, -2, 1, 3], key=abs)  # Output: [1, -2, 3, -4]
				  ~~~
				- Sort strings by their length:
				  ~~~python
				  sorted(["banana", "pie", "Washington", "book"], key=len)
				  ~~~
		- Operator Module Functions
			- The `operator` module provides key functions for common transformations.
			- Example: `operator.itemgetter` for tuples.
			  ~~~python
			  from operator import itemgetter
			  sorted([(1, 2), (3, 1), (5, 0)], key=itemgetter(1))
			  ~~~
		- Sorting with Multiple Criteria
			- Use a tuple in the `key` function for multiple sort criteria.
			- **Example**:
			  ~~~python
			  data = [('a', 2), ('c', 1), ('b', 1)]
			  sorted(data, key=lambda x: (x[1], x[0]))
			  ~~~
		- Stable Sorts
			- Python’s sort algorithm is stable:
				- Maintains relative order of items with equal keys.
			- Example:
			  ~~~python
			  data = [('a', 2), ('c', 2), ('b', 1)]
			  sorted(data, key=itemgetter(1))
			  ~~~
		- Advanced Sorting
			- Sort complex objects using `key` with attributes or methods.
			- **Example**:
			  ~~~python
			  class Student:
			      def __init__(self, name, grade):
			          self.name = name
			          self.grade = grade
			  students = [Student('john', 'A'), Student('jane', 'B')]
			  sorted(students, key=lambda s: s.grade)
			  ~~~
		- Custom Comparisons
			- Custom comparisons are less common due to the simplicity of `key`.
			- Use `functools.cmp_to_key` if necessary.
		- Performance
			- Python uses Timsort, optimized for real-world data.
			- Complexity:
				- Best case: O(n)
				- Average and worst case: O(n log n)
		- Summary
			- Use `.sort()` for in-place sorting.
			- Use `sorted()` for creating a new sorted list.
			- Prefer the `key` parameter for simplicity and performance.