# Loops

> Source: Chapter 4 §4.6 (for loops), §4.7 (while loops)

**Curriculum graph node:** Loops

---

## 4.6  for loops
A loop is a facility to repeat a set of statements as per specified conditions. Python gives you a choice of two loops: for and while. The for loop is used when an action is to be repeated for a fixed number of times. The while loop keeps repeating an action until an associated test becomes false (the later is useful when the programmer does not know in advance how many times the loop will be repeated).  We have already encountered the for-loop in our quick tasting of Python in chapters 1 and 2. We will relook at it formally now.
Let us first look at the terminology associated with a for loop:
```python
for i in range (1,11):
  print(i)  |  for  keyword
i     index of the loop
range(1,11)  iterable (there are other options)
print(i)  loop body/block/suite
Each ‘run’ of a loop iteration/execution
```

Why is a loop called by that name ? A loop in English refers to a circular shape and repetition (the circle itself embodies repetition, if you just move through a circle, you will be repeatedly travelling in the same path).
Let us note some points about range function. As already noticed, range(a,b) produces a range of numbers from a to b-1. Its general format is:
    range(start, stop+1, step)
step is assumed as 1 when not specified. Start is assumed as zero when not specified.  Start, stop and step should all be int. The possibilities of range are exemplified below:
| Sl no | Usage of range | Range of numbers produced |
| --- | --- | --- |
|  | range(1,10) |  |
|  | range(1,10,1) |  |
|  | range(10) |  |
|  | range(5,0,-1) |  |
|  | range(1,10,0.1) |  |

Let us now note some points about for loops:
1. Iterables: Loops have so far been demonstrated on range of numbers. In coming chapters we will learn about lists, strings etc. for loop can be used on them also (they are together called iterables).
```python
for i in [1,2,3,4]:           #List
    print(i)  |  for i in (1,2,3,4):         #Tuple
    print(i)
1,2,3,4  |  1,2,3,4
for i in 'abcdefg':         #String
    print(i)  |  for i in {1:33,2:44}:  #Dictionary
    print(i)
a b c d e f g  |  1,2
```

2. Loop without index: Let us also see a special usage without index. Consider the following two code snippets:
```python
for i in range (1,11):
  print(i)  |  for i in range (1,11):
  print(“Hello”)
```

In both loops, index is i. In the first one i is used in the body of the loop (print(i)). But in the second example, i is not used in the body. It just is used to keep counting the 10 iterations. In such cases, Python lets you avoid naming the index and use __ instead:
    for __ in range (1,11):
      print("Hello")
3. Loops with two indices: Loops can also be used with two indices on special occasions. Consider a data in pair format (we will be studying them when we study lists in next chapter). [ (1,'Ganga'), (2, 'Volga'), (3, 'Amazon)]
If we want to print both values in the pair, we can use two indices
```python
L=[ (1,'Ganga'), (2, 'Volga'), (3, 'Amazon)]
for i,j in  L:
   print (i,j)  |  Ganga
Volga
Amazon
```

Python can create the serial numbers of the data even if the data is not in pair format. For this enumerate function can be used (The word enumerate in English means to count one by one. This word is used in statistics and census. In our context, it means take items and list them with a serial number)
```python
L=[‘Ganga','Volga','Amazon’]
for i,j in enumerate(L):
   print (i,j)  |  0  Ganga
Volga
Amazon
```

4. Nested for loops : for statement can be executed within another for statement, which is called nesting. Let us see an example for printing multiplication table. In nested loops, inner loop runs to completion for each run of the outer loop.
```python
for i in range (1,11):
   for j in range (11):
        print(i,j, i*j)  |  for i in range (1,11):
   print('Multiplication Table for ', i)
   for j in range (1,11):
     print(i, ' * ', j,' =', i*j)
```

In the above program outer loop will run 10 times, and each time, the inner loop will run 10 times. Thus, the final print statement will run 100 times. We will use nested for-loops when we handle 2-D lists.
5. Handing the loop index: Do not use the index variable before or after the loop. Before the loop, it is undefined and after the loop it will hold the last value of the index at which it stopped. Do not redefine index variable inside loop (though it wont cause an error, it will have no effect.  The same loop variable can be used for more than one loop, provided they are not nested. See exercise below.
6. else clause in for loops: else clause is possible to be added to a for loop. The statement after else clause will be executed when the loop runs completely.
```python
for i in range (3):
   print(i)
else: print(“loop is over”)  |  0
1
2
loop is over
```

Exercise 6 Predict output or point out errors:
```python
print(i)
for i in range (10):
print(i)
for i in range (10):
print(i)
print('Outside the loop', i)
for i in range (1,6):
print(i)
for i in range (10,16):
print(i)
for i in range (1,11):
   for i in range (11):
        print(i,i, i*i)
for i in range (10):
  i=5
  print(i)
for i in range (10):
  i=i+1
  print(i)
```

## 4.7 while loops
A for loop is a compact way of iteration in which the start, stop and step of the loop are stated together in one go.
```python
for x in range(1,7,2):
   print (x*x)
```

This is an organized way to specify repeated tasks. At times, we may want to just do the repeated tasked in a lazy manner. We may just want to specify repetition without worrying about where to begin and end. While loop is the way to do this. See the following code for reading numbers and printing their squares.
```python
while(True):
   x=int(input())
   print(x*x)
```

This loop will keep asking for a number and print its square. When will it stop ? It wont. You will have to close your Python interpreter. There may also be an option called “Interrupt Execution/Restart Runtime”.
You can specify a condition to stop, by using an if statement along with break. Let us say we want to stop when the user inputs 0.
```python
while(True):
   x=int(input())
   if (x==0): break
   print(x*x)
```

A while loop is an alternative to for loop, where the start, stop, and step details are left to be taken care of by the programmer.
The stop condition is stated after while using any logical expression or the word ‘True’ as seen above.
```python
while (i<11):
   print (i)  |  Error !
```

This does not run (raises an error), because the variable i is not defined. Let us add it:
```python
i=1
while (i<11):
   print i
```

Now the loop runs, but without end, printing same value of 1, because we have not addressed the step. Let us add that too.
```python
i=1
while (i<11):
  print i 
  i=i+1
```

Now we have a while loop equivalent to for i in range(1,11,1). You may conclude that this is a cumbersome way of doing the same thing that a for loop can do. But note that the while loop gives you independent control of start and step and this the while loop can be handy in certain circumstances. For loop does not permit float value for index i. while loop has no such issues.
```python
i=0.5
while (i<11):
  print (i)
  i=i+0.5  |  0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5
```

Exercise 7: Predict Output of the following code snippets (if they are not erraneous)
```python
i=10
while(i<5):
  print(i)
  i=i+1
i = 5
while i > 0:
    print(i)
    i -= 1
i = 0
while i < 10:
    print(i)
    i += 2
i = 3
while i <= 15:
    print(i)
    i += 3
```

Exercise 8: Write While loops to achieve the following outputs
| 10, 9, 8, 7, 6, 5, 4, 3, 2, 1 |  |
| --- | --- |
| 1 4 9 16 25 |  |
| 3 6 9 12 15 |  |
| Print characters of "PYTHON" one by one |  |
| Print sum of numbers 1 to 5 |  |

Exercise 9  Write programs for the following using while loops
a) input characters and print it back (echo) until the character ‘x’ is typed in.
b) input integers and print it back (echo) until a negative integer is typed in.
c) input integers and print it back (echo) until the square of the integers read is > 1250.
d) input integers and print it back (echo) until the number read is <100 or  > 200.
