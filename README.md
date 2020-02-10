# objdict
Objdict - A collection of Dictionary like objects for any task.

* Objdict
 - The ultimate dictionary - all in one
 - recursivly updateable 
 - splitable
 - attribute accessible

Usage example:
```python
>>> from objdict import Objdict
# Create an Objdict and fill it with keys and values through attributes
>>> a = Objdict()
>>> a.x.y = 1
>>> a.x.list = [1,2,3]
>>> a
{'x': {'y': 1, 'list': [1, 2, 3]}}
# Create another Objdict with similar keys and different values
>>> b = Objdict()
>>> b.anotherKey = "anotherValue"
>>> b.x.list = [4, 5, "6"]
>>> b
{'x': {'list': [4, 5, '6']}, 'anotherKey': 'anotherValue'}
# Merge them (including the lists)
>>> a.update(b)
>>> a
{'x': {'y': 1, 'list': [1, 2, 3, 4, 5, '6']}, 'anotherKey': 'anotherValue'}
# Add an additional key
>>> a.yet_another_key = None
# Split the dict by keys - "x" in one group, and all the rest
>>> a.split([("x",)])
[{'x': {'y': 1, 'list': [1, 2, 3, 4, 5, '6']}}, {'yet_another_key': None, 'anotherKey': 'anotherValue'}]
```

* Rdict
  - Recursivly updateable dictionary
 
* AttrDict
 - Access, set, and delete items like attributes

* JsDict
 - Acts like a Javascript Object
 - Access, set, and delete items like attributes
 - Missing items return as None
 
* OrderedMap
 - An OrderedDict with an easy update chain syntax


