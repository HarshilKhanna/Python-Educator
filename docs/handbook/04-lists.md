# Lists, Tuples & Sets

> Source: Chapter 5

**Curriculum graph node:** Lists

> ⚠️ **Flagged gap:** Sections 5.5, 5.6, 5.7 appear absent from the source document (numbering jumps from 5.4 → 5.8). Content for those sections may be in images or was never authored. Verify against the original .docx.

---

   Chapter 5: Python Data Structures: Lists, Tuples & Sets
## 5.1 A QUICK TASTE OF LISTS
    A list is an ordered arrangement of data elements, separated by comma and capable of being referred to by indices (numbers representing their position in the list). Here is a list of numbers:
                                 x=[10, 20, 30, 40]
It is simply the numbers separated by comma, enclose with square brackets [ and  ]. You can handle it as a single entity and also elementwise. See the following two code snippets:
```python
x=[20, 50, 70, 10]
print(x)  |  x=[20, 50, 70, 10]
print(x[2])
[20, 50, 70, 10]  |  70
```

Let us also take a quick look at some ‘functions’ that can be used on lists. We will discuss them later.
```python
x=[20, 50, 70, 10]
x.sort()
print(x)  |  x=[20, 50, 70, 10]
x.reverse()
print(x)
Output: [10, 20, 50,70]  |  Output: [10, 70, 50, 20]
x=[20, 50, 70, 10]
print(len(x))  |  x=[20, 50, 70, 10]
print(sum(x))
Output: 4  |  Output: 150
```

## 5.2. THE CONCEPT OF DATA STRUCTURES
In programming language some data types are defined. In Python we have seen int, float, char, Bool etc. With basic data types as building blocks, structures of data can be conceived. Such data structures make programming convenient.
An analogy may be helpful here. Human beings use basic building materials like wood, metal, plastic etc. But they always make structures of different shapes suited for different situations. Wood can be used to build a box as well as a shelf. Which is better? Well, that depends on what you want to do with them. Imagine keeping books in a shelf and in a box. For library use, it is more convenient to keep the books in a shelf. If we were to keep all books in boxes it would cause long delays for users in searching & locating books they want to refer. In a warehouse of a printing company, multiple copies of the same books can well be stored in a box without any problem.  You can initially think of data structures as containers and vessels (Cups, plates, bowls, bottles) of different shape in which data is kept. In principle, you can use any data structure to store any data, but it can make program writing difficult and the programs inefficient (Imagine storing water in plates and rice in bottles!). In programs also similar situations arise. We can keep a sequence of numbers stored in a string, list, tuple or a file. The choice among these is dependent on the way you are required to use them (access them, modify the, archive them etc). Your program’s complexity and efficiency critically dependents on the selection of the appropriate data structures. One of the important skills of a programmer is to choose an appropriate data structure. One of the most influential computer science books written by Niklaus Wirth in 1976 is titled Algorithms + Data Structures = Programs. This title reflects the importance of data structures in programming and the fact that algorithms and data structures are intimately related.
In Python, a particular set of data structures are called Python Collections:
| Python Collections | Python Collections |
| --- | --- |
| Sequential
Lists
Strings
Tuples
Non-sequential
Dictionary | x=[25, 'indian', 'F', 37.8, True]
y=”Janaganamana”
coordinate=(1,2)
x={'ems' : 'cpm',  'vajpayee':'bjp', 'indiragandhi':'inc'} |
| Sets | x=set(1,2,3,4) |
| Files | f1=fopen('academic.txt', 'w') |

We will now discuss Python collections in detail. We will take up three of them in this chapter: lists, tuples and sets.
## 5.3. LISTS
#### A list is an ordered arrangement of data elements, separated by comma and capable of being referred to by indices (numbers representing their position in the list). It can be either single dimension or multi-dimension. Here are some key concepts about lists in Python:
Lists are arrangements/collection/group of data (which could be of different types) referred to by a single name such as A, sales, marks etc
Each element/value/member of the list is referred to by using an index, as in: A[0], A[1], sales[5], marks[j] etc. 0, 1, 5 and j inside the square brackets are examples of indices.
Indices start from 0 (First element of a list is actually 0th element). There are alternate indices for lists, from -1 for the last element and progressing to -2,-3,-4 etc backwards.
Lists can be handled easily and efficiently by using for/while loops.
In Python, unlike other languages, there is no need for list elements to be of same type. They can be a mix of types such as [7, 3.5, ‘F’, ‘India’, (2,3), [1,2,3]).
## 5.3.1 INITIALISING LISTS
Lists can be initialized by simple giving the values inside square brackets.
    x=	[11, 22, 33, 44, 55, 66]
    x=	[22.6, -17, 50.9, 6000]
    vow=	['a', 'e', 'i', 'o', 'u']
    pets=	['cat', 'dog', 'parrot']
    bio=	[‘Johnson’, 29, ‘M’, 87.95]
    When a list is to be filled with a regular sequence of numbers, range can be used to do it. You can specify start, stop and step, as we already saw while learning for loops. It may be noted that range does not work for float or character data types.
| n=range(1,100) | [1,2,3…99] |
| --- | --- |
| oddn=range(1,100,2) | [1,3,5…99] |
| even=range(2,100,2) | [2,4,6…98] |

It is possible to use * operator to achieve filling a list with large number of repeated values.
    d1=[0]*5     #[0, 0, 0, 0, 0]
    d2=[None]*5  #[None, None, None, None, None]
Redefining elements in a list
```python
x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x[3]=3333
print(x)  |  x[3]=3333
print(x)  |  x[3]=3333
print(x)  |  x[3]=3333
print(x)  |  x[3]=3333
print(x)  |  x[3]=3333
print(x)
0  |  1  |  2  |  3  |  4  |  5  |  0  |  1  |  2  |  3  |  4  |  5
00  |  11  |  22  |  33  |  44  |  55  |  00  |  11  |  22  |  3333  |  44  |  55
```

Deleteing elements in a list
```python
x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)
0  |  1  |  2  |  3  |  4  |  5  |  0  |  1  |  2  |  3  |  4
00  |  11  |  22  |  33  |  44  |  55  |  00  |  11  |  33  |  44  |  55
```

- List  Copying: Deep and Shallow
```python
Deep Copy  |  Shallow
L=[1,2,3]
G=L
L.append(5)
print(L); print(G)  |  L=[1,2,3]
G=list(L)
L.append(5)
print(L); print(G)
[1, 2, 3, 5]
[1, 2, 3, 5]  |  [1, 2, 3, 5]
[1, 2, 3]
```

Later in this chapter we will learn how to cut out a slice of a list. We can use that also for initializing lists. Given below is code for slicing out elements 3 to 6 from list x and using it to initialize y:
          0       1        2        3        4       5        6        7        8         9          indices
    x=[00, 11, 22, 33, 44, 55, 66, 77, 88, 99]
    y=x[3:7]
    print(y)     [22,33,44,55,66]
You can also use the + operator to add two lists and intialise another.
    x=[00, 11]; y=[22,33]
    z=x+y
Perhaps the most versatile way to intiliase lists is through a method called list comprehension which we introduce in detail in section 5.3.7. We note an example in advance, to initialize a list with square of odd numbers from 1 to 100:
    x=[ i*i  for i in range(1,101,2)]
EXERCISE: Do the list initialization of list x, as indicated below:
| With numbers from 1 to 10,000 |  |
| --- | --- |
| With odd numbers from 5 to 55 |  |
| With lowercase English alphabets |  |
| 1, 3, 5, 7,9…99 |  |
| [0.1, 0.1, 0.1 ….] 100 elements |  |
| [True, True, True…] 100 elements |  |

## 5.3.2 LIST INDICES
Elements of a list can be referred to by a number indicating their position in the list, called index. Python provides for two ways of indexing, positive and negative. Postive counts position from left to right, beginning with 0.  Negative counts position from right to left, beginning with -1.
| List | x=[11, 22, 33, 44, 55, 66] | x=[11, 22, 33, 44, 55, 66] | x=[11, 22, 33, 44, 55, 66] | x=[11, 22, 33, 44, 55, 66] | x=[11, 22, 33, 44, 55, 66] | x=[11, 22, 33, 44, 55, 66] |
| --- | --- | --- | --- | --- | --- | --- |
| List elements | 11 | 22 | 33 | 44 | 55 | 66 |
| Forward Indices | x[0] | x[1] | x[2] | x[3] | x[4] | x[5] |
| Backward Indices | 11 | 22 | 33 | 44 | 55 | 66 |
| Backward Indices | x[-6] | x[-5] | x[-4] | x[-3] | x[-2] | x[-1] |

A comparison of the indices
| +ve index | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- | --- |
| -  ve index | -6 | -5 | -4 | -3 | -2 | -1 |

EXERCISE: Consider the following lists and fill the table below
    a=[34, 56, 77, 2,  9]
    b=[ 1,  0,  1, 1,  1]
    c=[90, 20, 10, 45, 66, 77, 34, 56, 99]
| a[0] | b[1] | c[5] | a[9] | c[-1] | b[0] | a[b[2]] | c[9] |
| --- | --- | --- | --- | --- | --- | --- | --- |

    colors = ['red', 'green', 'blue', 'yellow', 'white', 'black']
| colors[ 2 ] | colors[ -1 ] | colors[-2  ] | colors[ -3 ] | colors[ 4 ] |
| --- | --- | --- | --- | --- |

## 5.3.3 PRINTING LISTS
You can print lists with simple print. We can also use loops to print out element by element. See next section.
    x=[22, -17, 50, 6000]
    print(x)
    22, -17, 50, 6000
## 5.3.4 PROCESSING LISTS WITH FOR-LOOPS
Let us first print a list using loops.
```python
Directly giving range  |  Using len() to give range  |  Directly using lists
m=[22, -17, 50, 6000]
for i in range(0,4):
    print(m[i])  |  m=[22, -17, 50, 6000]
for i in range(len(m)):
    print(m[i])  |  for i in [22,33,44]:
    print(i)
```

    While studying loops, we wrote code for printing, summing and counting numbers, all from a continuous sequence defined by a range. Now we can take a list of numbers and do the same processing. Here is an example where marks of 5 students are defined as a list and processed:
```python
Selective Printing  |  Selective Summing  |  Selective Counting
m=[34, 55, 97, 67, 50]

for i in range(0,5):
  if(m[i]>39): print(m[i])  |  m=[34, 55, 97, 67, 50]
sum=0
for i in range(0,5):
  if(m(i)>39):sum=sum+m[i]
print(sum/5)  |  m=[34, 55, 97, 67, 50]
count=0
for i in range(0,5):
  if(m(i)>39):count=count+1
print(count)
Output and Remarks  |  Output and Remarks  |  Output and Remarks
```

 Lists themselves can be taken as a range. Therefore, above programs can be modified in the following style
```python
m=[34, 55, 97, 67, 20]
for i in m:
  if(i>39): print(i)  |  fruits=[‘papaya’, ‘banana’, ‘apple’]
for f in fruits:
  print(f)
55, 97, 67  |  papaya banana apple
```

EXERCISES
1. Write a program to define a list L with 10 elements 32,56, 59, 78, 21, 90, 88, 69, 77, 41 and print out: (a) all numbers. (b)  numbers greater than 25. (c)  number not less than 50. (d) numbers greater than 25 and less than 50. (e)  numbers which are greater than 25 and less than 50 or greater than 75 and less than 100. (f)  numbers which are odd. (g)  Count of numbers which are even. (h)  Sum of numbers which are multiples of 7. (i)   Sum of numbers which are multiples of 3 and 6. (j) Count of numbers which are multiples of 3 or 5.
    2. Write a program to define a list c = ['a', 'A', 'Z', '@', 'j', 'e', 'I', 'o']and print: (a) all characters. (b)  all uppercase characters. (c)  all lowercase characters. (d)  all non-alphabetic characters. (e) all alphabetic characters. (f)  all lowercase vowels. (g) Count of character ‘e’ (Note: There are easy ways of achieving the above, once we study string functions. Here we may solve using for i in…)
## 5.3.5 ‘FUNCTIONS’ FOR BASIC MANIPULATION OF LISTS
    Functions are a concept which we will learn soon. For the moment, just take them as a waying of instructing Python.  Consider a list x= [0, 11, 22, 33, 44, 55]. Let us see different ways in which this list can be modified or made use of to create other lists. Note that the first 8 functions are used in the format x.function(), an indication of object-oriented approach (which we will learn soon)
a. Appending elements to a list
```python
x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x.append(66)
print(x)  |  x.append(66)
print(x)  |  x.append(66)
print(x)  |  x.append(66)
print(x)  |  x.append(66)
print(x)  |  x.append(66)
print(x)  |  x.append(66)
print(x)
0  |  1  |  2  |  3  |  4  |  5  |  0  |  1  |  2  |  3  |  4  |  5  |  6
00  |  11  |  22  |  33  |  44  |  55  |  00  |  11  |  22  |  33  |  44  |  55  |  66
```

b. Inserting elements (at specified index, pushing the rest to the right and retaining them)
```python
x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x.insert(4, 39)
print(x)  |  x.insert(4, 39)
print(x)  |  x.insert(4, 39)
print(x)  |  x.insert(4, 39)
print(x)  |  x.insert(4, 39)
print(x)  |  x.insert(4, 39)
print(x)  |  x.insert(4, 39)
print(x)
0  |  1  |  2  |  3  |  4  |  5  |  0  |  1  |  2  |  3  |  4  |  5  |  6
00  |  11  |  22  |  33  |  44  |  55  |  00  |  11  |  22  |  33  |  39  |  44  |  55
```

c. Removing elements
    There are three cases. The del() function can delete any element by citing its index (this has been introduced earlier). The remove()function can remove first occurrence of any element by value. The pop() function removes last, but can also remove specific element.
```python
x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)  |  del x[2]
print(x)
0  |  1  |  1  |  2  |  2  |  3  |  3  |  4  |  4  |  5  |  5  |  0  |  1  |  1  |  2  |  3  |  3  |  4  |  4  |  4
00  |  11  |  11  |  22  |  22  |  33  |  33  |  44  |  44  |  55  |  55  |  00  |  11  |  11  |  33  |  44  |  44  |  55  |  55  |  55
x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)  |  x.remove(11)
print(x)
0  |  1  |  1  |  2  |  2  |  3  |  3  |  4  |  4  |  5  |  5  |  0  |  1  |  1  |  2  |  3  |  3  |  4  |  4  |  4
00  |  11  |  11  |  22  |  22  |  33  |  33  |  44  |  44  |  55  |  55  |  00  |  22  |  22  |  33  |  44  |  44  |  55  |  55  |  55
x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x=[00, 11, 22, 33, 44, 55]
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)  |  x.pop( )
print(x)
0  |  0  |  1  |  1  |  2  |  2  |  3  |  3  |  4  |  4  |  5  |  0  |  0  |  1  |  1  |  1  |  2  |  2  |  3  |  4  |  4
00  |  00  |  11  |  11  |  22  |  22  |  33  |  33  |  44  |  44  |  55  |  00  |  00  |  11  |  11  |  11  |  22  |  22  |  33  |  44  |  44
```

    Note : x.pop(2) has same effect as del x[2] You can catch the popped value in a variable: y=x.pop()
- d. Sorting a list
```python
x=[55,11,22,33,0,44]
print(x)  |  x=[55,11,22,33,0,44]
print(x)  |  x=[55,11,22,33,0,44]
print(x)  |  x=[55,11,22,33,0,44]
print(x)  |  x=[55,11,22,33,0,44]
print(x)  |  x=[55,11,22,33,0,44]
print(x)  |  x.sort()
print(x)  |  x.sort()
print(x)  |  x.sort()
print(x)  |  x.sort()
print(x)  |  x.sort()
print(x)  |  x.sort()
print(x)  |  x.sort()
print(x)
0  |  1  |  2  |  3  |  4  |  5  |  0  |  1  |  2  |  3  |  4  |  5
55  |  11  |  22  |  33  |  0  |  44  |  0  |  11  |  22  |  33  |  44  |  55
```

    Note: sorted(x)  sorts, but x is not changed. You can catch the sorted result:  y=sorted(x)
- e. Reversing a list:
```python
x=[55, 11, 22, 33, 00, 44]
print(x)  |  x=[55, 11, 22, 33, 00, 44]
print(x)  |  x=[55, 11, 22, 33, 00, 44]
print(x)  |  x=[55, 11, 22, 33, 00, 44]
print(x)  |  x=[55, 11, 22, 33, 00, 44]
print(x)  |  x=[55, 11, 22, 33, 00, 44]
print(x)  |  x.reverse()
print(x)  |  x.reverse()
print(x)  |  x.reverse()
print(x)  |  x.reverse()
print(x)  |  x.reverse()
print(x)  |  x.reverse()
print(x)
0  |  1  |  2  |  3  |  4  |  5  |  0  |  1  |  2  |  3  |  4  |  5
55  |  11  |  22  |  33  |  00  |  44  |  44  |  00  |  33  |  22  |  11  |  55
```

- Note: It just reverses, not reverse sort. Try checking if the string input is a palindrome.
f. Index of first occurrence of an item
| x=[55, 11, 22, 33, 00, 44]
x.index(11) | x=[55, 11, 22, 33, 00, 44]
x.index(11) | x=[55, 11, 22, 33, 00, 44]
x.index(11) | x=[55, 11, 22, 33, 00, 44]
x.index(11) | x=[55, 11, 22, 33, 00, 44]
x.index(11) | x=[55, 11, 22, 33, 00, 44]
x.index(11) | 1 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 1 | 2 | 3 | 4 | 5 | 1 |
| 55 | 11 | 22 | 33 | 00 | 44 | 1 |

- g. extending a list (joining two lists)
```python
x=[00, 11, 22]
y=[33, 44, 55]
x.extend(y)  |  print(x)
[0, 11, 22, 33, 44, 55]
```

- h. Counting number of elements
```python
x=[00, 11, 22, 55, 11, 45]
print(x.count(11))  |  2
```

- i. Finding length of a list
| x=[55, 11, 22, 33, 00, 44]
len(x) | x=[55, 11, 22, 33, 00, 44]
len(x) | x=[55, 11, 22, 33, 00, 44]
len(x) | x=[55, 11, 22, 33, 00, 44]
len(x) | x=[55, 11, 22, 33, 00, 44]
len(x) | x=[55, 11, 22, 33, 00, 44]
len(x) | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| 44 | 44 | 00 | 33 | 22 | 11 | 6 |

    Note  You can use for i in range(len(X)) to use a loop on a list.
- j. Simple Statistics of List elements
```python
x=[00, 11, 22, 33, 44, 55]
a=min(x)
b=max(x)
c=sum(x)
print(a,b,c)
```

Note: if the list contains non-numeric data types, the sum( ) function will cause error, but others work meaningfully, in the context of alphabetical order.
```python
x=[‘kichu’, ‘pachu’, ‘sachu’ ‘pikachu’]
a=min(x)
b=max(x)
print(a,b)
```

- k. Radomly picking list elements
    It is sometimes very useful to pick elements from a list at random. For this we need to import random package and use random.choice() function.  Run repeatedly to understand the effect.
```python
import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  import random
x=[55, 11, 22, 33, 11, 0, 44]
print(random.choice(x))  |  33
0  |  1  |  2  |  2  |  3  |  3  |  4  |  4  |  5  |  5  |  33
55  |  11  |  22  |  22  |  33  |  33  |  00  |  00  |  44  |  44  |  33
import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  import random
x=[‘red’,‘blue’,‘black’,‘white’,‘pink’]
print(random.choice(x))  |  ‘white’
0  |  1  |  1  |  2  |  2  |  3  |  3  |  4  |  4  |  ‘white’
‘red’  |  ‘blue’  |  ‘blue’  |  ‘black’  |  ‘black’  |  ‘white’  |  ‘white’  |  ‘pink’  |  ‘pink’  |  ‘white’
```

## 5.3.6 SPECIAL HANDLING OF LISTS: Slicing, Comprehension and Enumeration
- Slicing is a process of extracting a part of a list. The format is:
    X[start : stop : step]
- start refers to the index of the element to start slicing
     stop refers to the index of the element before which slicing should end
-  step n (optional) allows you to take each nth -element within a start:stop range.
| Default values of [start : stop : step] | Default values of [start : stop : step] | Default values of [start : stop : step] |
| --- | --- | --- |
| Start | Stop | Step |
| 0 (first element) | -1 (last element)
If you actually mention it as -1, then the value of -2 takes effect,  as  stop refers to the index of the element before which slicing should end | 1
When default is -1, start should be greater than stop |

| Various slicing expressions and their effect | Various slicing expressions and their effect | Various slicing expressions and their effect |
| --- | --- | --- |
| x=[00, 11, 22, 33, 44, 55] | y=x[1:2] | [11] |
| x=[00, 11, 22, 33, 44, 55] | y=x[0:3] | [00,11,22] |
| x=[00, 11, 22, 33, 44, 55] | y=x[ :3] | [00,11,22] |
| x=[00, 11, 22, 33, 44, 55] | y=x[3: ] | [33, 44, 55] |
| x=[00, 11, 22, 33, 44, 55] | y=x[0:-1] | [00, 11, 22, 33, 44] |
| x=[00, 11, 22, 33, 44, 55] | y=x[0:] | [00, 11, 22, 33, 44, 55] |
| x=[00, 11, 22, 33, 44, 55] | y=x[:] | [00, 11, 22, 33, 44, 55] |
| x=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] | y=x[0:15:2] | [1, 3, 5, 7, 9, 11, 13, 15] |
| x=[00, 11, 22, 33, 44, 55] | y=x[:] | [00, 11, 22, 33, 44, 55] |
| x=[00, 11, 22, 33, 44, 55] | y=x[::] | [00, 11, 22, 33, 44, 55] |
| x=[00, 11, 22, 33, 44, 55] | y=x[::2] | [00, 22, 44] |

Slice assignment can redefine a part of a list:
    x=[00, 11, 22, 33, 44, 55]
| Slice assignment | Redefined X |
| --- | --- |
| x[0:3]=[00,10,20] | [00, 10, 20, 33, 44, 55] |
| x[0:3]=[00,05,10,15,20] | [00, 05, 10, 15, 20, 33, 44, 55] |
| x[0:3]=[00,25] | [00, 25, 33, 44, 55] |
| x[::2]=[1,1,1] | [1, 11, 1, 33, 1, 55] |
| del x[::2] | [11, 33, 55] |

Looping through Slice of list:  Earlier we saw how to process a list using loops.
```python
Looping through whole list  |  Looping through  list slice
x=[00, 11, 22, 33, 44, 55]
for i in x:
  print(i)  |  x=[00, 11, 22, 33, 44, 55]
for i in x[0:3]:
  print(i)
```

EXERCISES
```python
Write output of following slice statements, x=[0,1,2,3,4,5,6,7,8,9,10]  |  Write output of following slice statements, x=[0,1,2,3,4,5,6,7,8,9,10]
x[3,7]
x[0: ]
x[ : ]
x[ : -1]
x[::]
x[ : :2]
x[ : :3]
x[ 10:0:-1]
Write slice statementsto achieve the following outputs, if , x=[0,1,2,3,4,5,6,7,8,9,10]  |  Write slice statementsto achieve the following outputs, if , x=[0,1,2,3,4,5,6,7,8,9,10]
0,1,2,3,4,5
0,2,4,5,8,10
10,9,8,7,6,5
10,8,6,4,2,0
```

## 5.3.7 LIST COMPREHENSION
List comprehension is a way to create a new list based on the values of an existing list. It is a sort of short-hand notation.
    x=[1,2,3,4,5]
    y=[i*i for i in x]
    print(y)
How do we read the strange syntax above ?
```python
y=[i*i  |  for i in x ]
Add i*i to list y  |  for every member i of list x
```

EXERCISE: Predict output
```python
y=[ i for i in range(10)]
y=[i**2 for i in [1,2,3,4,5]]
y=[i * 0.1 for i in range(10)]
```

We can apply a condition in list comprehension. It can be mentioned at the end
    x=[1,2,3,4,5]
    y=[i*i for i in x if x>3]    [16,25]
```python
y=[i*i  |  for i in x  |  if i>3
Add i*i to list y  |  for every member i of list x  |  only if i>3
```

EXERCISES  Predict list y in each of the following cases
```python
y=[ i for i in range(15) if i%2==0]
Y=[i**2 for i in [1,2,3,4,5] if i%2==1]
x=[20,45,67,89,34]; y=[i>40 for i in x]

```

You can also add a condition in the beginning on what should be added to y
    y=[i if i%2==0 else i**2 for i in [1,2,3,4,5,6,7]]  [1,2,9,4,25,6,49]
EXERCISES Write list comprehension for the following cases, with x=[0,1,2,3,4,5,6,7,8,9,10]
| Y has same elements of x, when their values  are less than 5, otherwise double of it |  |
| --- | --- |
| Y has elements of x, plus 5, when their values  are less than 5, otherwise, element of x minus 5 |  |

Predict list y in each of the following cases
```python
y=[ i*0.1 if i%2==0 else i*0.2 for i in range(15) ]
y=[ i*0.1 if i%2==0 else i*0.2 for i in range(15) if i >5]
```

Finally, we can produce lists of True and False as a result of a condition we specify:
    y=[i>2 for i in [1,2,3,4,5]]  [False, False, True, True, True]
EXERCISES  Write list comprehension for the following cases, with x=[0,1,2,3,4,5,6,7,8,9,10]
```python
Y has True if element of x is odd, otherwise False
Y has True if element of x is greater than 7 or less than 3
```

So far, we have used numerical lists. But strings (which are lists of characters) can also be processed likewise.
    x = "janaganamana"
    y = [i for i in x if i==’a’ ]  [a a a a a a]
```python
x = "janaganamana"
y = ['a' if i=='a' else '-' for i in x]
print(y)  |  [- a – a – a – a – a - a
x = "janaganamana"
y = ['vowel' if i in 'aeiou' else '---' for i in x ]
print(y)
['---', 'vowel', '---', 'vowel', '---', 'vowel', '---', 'vowel', '---', 'vowel', '---', 'vowel']  |  x = "janaganamana"
y = ['vowel' if i in 'aeiou' else '---' for i in x ]
print(y)
['---', 'vowel', '---', 'vowel', '---', 'vowel', '---', 'vowel', '---', 'vowel', '---', 'vowel']
```

## ENUMERATING LISTS
    Enumerate means ‘to name things separately, one by one’. To enumerate ['a', 'b', 'c'] means to list out the elements with serial number: 1.a, 2.b, 3.c etc. For this enumerate() function can be used
    x=['a', 'b', 'c']. The result must be cast to a list.
    y=enumerate(x)
    print (list(y))  [(0, 'a'), (1, 'b'), (2, 'c')]
 A loop with two indices can be applied to print out the serial numbers and values:
```python
x=['a', 'b', 'c'] 
y=enumerate(x)
for i, j in y:
  print (i,j)  |  0 a
1 b
2 c
```

Special assignment with lists
Lists can also be used to assign values in a special way:
    [x,y]=[1,2]
    print (x,y)    1 2
## 5.4 TWO-Dimensional LISTS
    The lists we have already considered are one-dimensional. Two-dimensional (2-D) lists are used to store a group of data arranged in rows and columns and called by a single name. The list elements are referred to by two indices (plural of index), row index and column index. 3rd row 5th column in X is referred to as X[3][5].  We can define 2-D lists with nested [ ]. List can be defined by typing in different lines too.
```python
m= [[11, 12, 13], [21, 22, 23], [31, 32, 33]]
print (m)

[[11, 12, 13], [21, 22, 23], [31, 32, 33]]  |  m=[ 
[11,12,13],
[21,22,23],
[31,32,33]
]
```

Like 1-D lists, you can  print 2-D  lists with simple print( ) as shown above. Like one-dimensional lists, two-dimensional lists are also handled easily and efficiently by for loops. However, since both rows and columns are to be handled, we need nested for loops. See how we arrange 2-D list elements differently in each of the following code snippets.
```python
marks=[  [25,36,41],   [55,96,69],   [33,92,14]  ]  |  marks=[  [25,36,41],   [55,96,69],   [33,92,14]  ]  |  marks=[  [25,36,41],   [55,96,69],   [33,92,14]  ]
for i in range(0,3):
for j in range(0,3):
  print (marks[i][j])  |  for i in range(0,3):
  for j in range(0,3):
      print (marks[i][j])
  print("\n")  |  for i in range(0,3):
  for j in range(0,3):
     print (marks[i][j], end=' ')
  print("\n")
25
36
41
55
96
69
33
92
14  |  25
36
41

55
96
69

33
92
14  |  25 36 41 

55 96 69 

33 92 14
```

Example
Data of marks of 3 students in 3 courses are given below. Let us write a program to put the marks into a 2-D list. Predict effect of each of the code snippets below.
	Exam
			 0		 1		 2
		0	25		36		41
 	Student	1	55		96		69
		2	33		92		14
```python
m=[ [25,36,41], [55,96,69], [33,92,14] ]  |  m=[ [25,36,41], [55,96,69], [33,92,14] ]  |  m=[ [25,36,41], [55,96,69], [33,92,14] ]
for i in range(0,3):
 for j in range(0,3):
   print(m[i][j])  |  for i in range(0,3):
  for j in range(0,3):
    if(i==1):print(m[i][j])  |  for i in range(0,3):
  for j in range(0,3):
    if(i==j): print(m[i][j])
Rewrite the above with just one loop
```

EXERCISES
1. The sales data of 3 salesmen in 4 cities are given below:
      		  		         City
	             0		1		2		3
0   	6 		7		5		9
1   	3		2		8		11
2	22		6		0		7
Write a program to input this data and print out the following: (a) Whole sales data (b) average sales by salesman 1 (c) average sales in city 2 (d) Overall average sales (e)Maximum sale (f) Which city and which salesman registered maximum sales.
2. Initialize a list marks to store marks of 3 students in 4 exams and write code for given tasks.
   Student 				Exam
		0		1		2		3
	0   	40      		60		70		35
	1   	65		15		36		95
	2	77		93		13		22
(a) Find the average of marks in Exam 2 (b) Find the average of student No.2 (c) Find the number of students who have scored more than 75 marks
3. Write a program to initialize an array A of size 4 by 3 with the following values:
	21	32	57
	93	20	69
	37	66	17
	11	3	94
 Now, write for loops to print out: (a) all the element of the array, each row in separate line. (b) all elements>50 (c) all elements >50, with a zero in position of other elements. (d) all elements >50 and <60. (e) sum of all elements. (f) count and average of all elements >=40 (g) odd valued  elements (h) elements and their count. (i) elements which are multiples of 6. (j) elements in row 1 and column 2. (k) elements which are not in row 2 and column 1.
4. Write a program to initialize an array a of size 4 by 3 with the following values:
	‘h’    	‘a’	   ‘t’
	‘m’	‘a’	   ‘t’
	‘s’	‘a’	   ‘t’
	‘b’	‘a’	   ‘t’
Write for loops to print out: (a)  elements of the array, each row in separate line. (b) all elements which are vowels.(c)  elements which are vowels, with a space in position of others. (d) elements which are equal to ‘a’, ‘b’, ‘c’, or ‘d’. (e) count of all vowels. (f) count of all non-vowels.
## 5.8 TUPLES
Tuples are immutable lists. They are written within ( ) unlike lists which are written within [ ].
```python
Lists  [   ] - mutable  |  Tuples  (   )  - immutable
x=[1,2,3,4]
x[0]=0  |  x=(1,2,3,4)
x[0]=0  error
x=[1235, ‘john’, 97.32]  |  x=(1235, ‘john’, 97.32)
len(x) 3  |  len(x) 3
for i  in x
  print(i)   1 2 3 4  |  for i  in x
  print(i)   1 2 3 4
```

Recall functions like sort, remove, pop etc used on lists. Among them, those which do not alter the elements, work with tuples. Others do not, because tuples are immutable.
| Among functions which work with lists … | Among functions which work with lists … |
| --- | --- |
| Those which work with tuples | Those which do not work with tuples |
| len
min 
max 
sum (only when list has numbers alone)
index | sort
append
insert
remove
pop |

Where are tuples useful ? We list some cases below, some of which will be clearer in later sessions
- To handle ordered pairs that do not change, like coordinates (x,y), (x,y,z) etc.
- As a data types to return more than one value from a function.
- To do tuple assignement (x,y)=(3,5)
## 5.9 SETS
Sets are an implementation of the mathematical concept known by the same name. While lists and tuples are ordered collections, sets are not (ie, it cannot be accessed by indices and cannot be sorted or sliced). Lists use [ ], tuples use ( ), sets use { }
Intialising sets
    s1={1,2,3,4}
    set1 = {"apple", "banana", "mango"}
set2 = {1, 5, 7, 9, 3}
set3 = {True, False, False}
    set4 = {"abc", 34, True, 40, "male"}
    s={ }
Converting lists to sets and vice versa
    s2=set([1,2,3,4])
    s3=list({1,2,3,4})
Repetition has no meaning in sets (unlike lists and tuples)
    s4={1,1,2,2,1}
    print(s4)     {1,2}
SET Operations: Union , Intersection, Difference
    p={'gandhiji', 'adi sankara', 'narayana guru'}
    l={'nehru', 'gandhiji', 'subashchandrabose'}
```python
a=p.union(l)
b=l.intersection(p)
c=l.difference(p)
d=p.difference(l)
print(a)
print(b)
print(c)
print(d)  |  a {'narayana guru', 'nehru','subashchandrabose',  
   'adi sankara',   'gandhiji'}

b {'gandhiji'}

c {'nehru', 'subashchandrabose'}

d {'adi sankara', 'narayana guru'}}
Exercise: Tryout these too:
isdisjoint():   Returns whether two sets have a intersection or not
issubset():     Returns whether another set contains this set or not
issuperset():  Returns whether this set contains another set or not  |  Exercise: Tryout these too:
isdisjoint():   Returns whether two sets have a intersection or not
issubset():     Returns whether another set contains this set or not
issuperset():  Returns whether this set contains another set or not
```

Looping through SETS
```python
f = {'apple', 'banana', 'mango'}
print(f)
for x in f:
  print(x)  |  {'banana', 'apple', 'mango'}
banana
apple
mango
```

Function on Sets:
```python
s1={'apple', 'banana', 'mango'}
s1.add('jackfruit')
print(s1)  |  {'jackfruit', 'banana', 'apple', 'mango'}
s1={'apple', 'banana', 'mango'}
print(s1)
s2={'papaya', 'mango'}
s1.update(s2)
print(s1)  |  {'banana', 'apple', 'mango'}
{'apple', 'papaya', 'banana', 'mango'}
s1={'apple', 'banana', 'mango'}
s1.clear()
print(s1)  |  set()
s1={'apple', 'banana', 'mango'}
s1.remove('banana')
print(s1)  |  {'apple', 'mango'}
s1={'apple', 'banana', 'mango'}
s1.discard('banana')
print(s1)  |  {'apple', 'mango'}
s1={'apple', 'banana', 'mango'}
s1.pop( )
print(s1)  |  {'apple', 'mango'}removes a random element
```

