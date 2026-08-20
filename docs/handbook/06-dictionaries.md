# Dictionaries

> Source: Chapter 8

**Curriculum graph node:** Dictionaries

---

Chapter 8: Python Data Structures: Dictionaries
## 8.1. Introduction
Dictionaries are unordered and mutable list of pair values. Like lists, dictionaries are indexed lists, but indices are nor ordered numbers, only values. They are also known as hashes, maps or associative memory. Here is our first example:
| Dictionary creation | capitals={'India':'Delhi', 'Japan':'Tokyo'} | capitals={'India':'Delhi', 'Japan':'Tokyo'} |
| --- | --- | --- |
| Element pairs | 'India':'Delhi' | 'Japan':'Tokyo' |
| Key | 'India' | 'Japan' |
| Value | 'Delhi' | 'Tokyo' |

 Here are some facts on dictionaries
- They are (like sets) enclosed by { }
- Their elements are pairs of the form key : value
- Keys and values can be of any type or structure: numbers, characters, strings, lists, tuples…
- Duplicate key values will have only one effect (the one added last).
    Elements can be accessed by using key value as index as in capitals[‘india’]
## 8.2. Defining dictionaries
Here are some illustrative examples. Add print() statement also.
| d1={'India':'Delhi', 'Japan':'Tokyo', 'Cuba':'Havana', 'Quatar':'Doha'} |
| --- |
| d2={ } |
| d3={'Kohli':230, 'Dhoni':100} |
| d4={'Kohli':230, 'Dhoni':100, 'Kohli':37, 'Kohli':377} |
| d5={'septagon':'7','octagon':'8','duodecagon':'12'} |
| d6={'p1':(5,5),'p2':(15,5), 'p3':(10,15) } |
| d7={(5,5):'p1', (15,5): 'p2', (10,15): 'p3' } |
| d8={'L1':[22,33,44], 'L2':[55,66,77]} |
| d9={'Google': 'Do no evil', 'Apple':'Stay Foolish', 'Gandhiji':'Truth is God'} |
| d9={'Google': 'Do no evil', 
'Apple':'Stay Foolish', 
'Gandhiji':'Truth is God'} |

Dictionary elements can be assigned piece-wise too
```python
d10={}
d10['India']='Delhi'
d10['Cuba']='Havana'
print(d10)  |  Output:
{'India': 'Delhi', 'Cuba': 'Havana'}
d={22:33, 33:44}
l=list(d)
print(d,l)  |  {22: 33, 33: 44} 
[22, 33]
Converting key values to a list
```

Dictionaries are mutable data structures. Therefore, values can be redefined.
```python
d10={}
d10['India']='Delhi'
d10['Cuba']='Havana'
d10['India']='New Delhi'
print(d10)  |  Output:
{'India': 'New Delhi',          
 'Cuba' : 'Havana'}
```

## 8.3. Accessing elements of a Dictionary
    d1={'India':'Delhi', 'Japan':'Tokyo', 'Cuba':'Havana'}
```python
print(d1['India'])  |  print(d1['China'])
Delhi  |  KeyError
print(d1.get('India'))  |  print(d1.get('China'))
None
print(d1.get('Delhi'))  |  print(d1.get('China', ‘Not Found’))
```

## 8.4. Functions applicable to dictionaries.
General functions applicable to lists are applicable here also.
```python
d1={1:11, 2:22, 3:33}
len(d1)  |  3
d1={'india':'delhi','japan':'tokyo','cuba':'havana'}
del d1['japan']
print(d1)  |  {'india':'delhi',      
 'cuba':'havana'}
d1={'india':'delhi','japan':'tokyo','cuba':'havana'}
d1.clear()
print(d1)  |  { }
dee={1:11, 2:22, 3:33}
daa=dee
del daa[1]
print(dee,daa)  {2: 22, 3: 33} {2: 22, 3: 33}  |  Deep copying. 
Change in dee appears in daa, 
as they are the same.
dee={1:11, 2:22, 3:33}
daa=dee.copy()
del njan[1]
print(dee,daa) {1: 11, 2: 22, 3: 33} {2: 22, 3: 33}  |  Shallow Copy: 
Change in dee does not affect daa.
d1={1:11, 2:22, 3:33}
print(d1.items())  |  dict_items
([(1, 11), (2, 22), (3, 33)])
d1={1:11, 2:22, 3:33}
print(d1.keys())  |  dict_keys([1, 2, 3])
d1={1:11, 2:22, 3:33}
print(d1.values())  |  dict_values([11, 22, 33])
```

