# Python Basics & Operators

> Source chapters: Chapter 1 (Quick Taste-1), Chapter 2 (Quick Taste-2), Chapter 3 (Python Basics)

**Curriculum graph node:** Variables → Operators

---

Chapter 1: Quick Taste -1
1.1 Getting Started
    Dear learner, pls go to your internet connected device (mobile phone, iPad, laptop or any other). Login to your gmail account. Then open a new tab in the browser and go to colab.research.google.com Skip any pop up. Click File and choose New Notebook. You will be in a page like the following. You are now ready to start writing Python programs.
Where the cursor blinks (call it a Cell), you can type your first program.
All the coloring is done automatically. You can type away without bothering. Take care not to miss the “:” in the end of first line. Dont change the automatic indent in second line.
Now, just click the run button on the top left of the cell and if you saw numbers 1 to 9 displayed, then Congratulations! You have successfully run your first Python program.
This program involves a “for loop”. Here is a plain English explanation of the program
```python
for i in range (1,10):  |  Taking the value of i from 1 to 9 (in steps of 1)
print (i)  |  Print i, each time
```

Exercise-1: Readout, guess the output and test by running the following for loops and make your observations on their results. The small changes in each program is shown in bold, where possible.
```python
PROGRAM SNIPPET  |  OUTPUT & YOUR REMARKS
for i in range (0,11):
  print(i)
for i in range (0,100):
  print(i)
for i in range (-10,10):
  print(i)
for i in range (20,10):
  print(i)
for i in range (0,10):
  print(‘Namaste’)
for i in range (0,10):
  print(i*i)
for i in  range (0,10):
  print(i, i*i)
for i in range (0,10):
  print(i), print(i*i*i)
for i in  range (1,10):
  print(1/i)  |  Using (0,10) will cause error of division by zero
for i    in range   (1,  10) :
         print      (    i)  |  Note various spacings
for i in  range (1,10):
print(i)  |  Note the absence of tab before print(i)
for i in range(1,10): print(i)
for i in  Range (1,10):
  print(i)  |  Note capitalisation
for numbers in  range (1,10):
  print(numbers)
for i in range(1,10): 
  print(i+5)
for i in range(1,10): 
  print(i-5)
for i in range(1,10): 
  print(100-i)
```

So far we focused on grammar (syntax) of Python. Now we will focus on use of logic in programs. Try out the following two sets of exercises.
Exercise-2a:  The output of program snippets is given.  For each of them, the desired output is given. Your task is to complete the print(……..) statement.
```python
for i in range (0,10):
      print(      )  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(      )  |  66  |  67  |  68  |  69  |  70  |  71  |  72  |  73  |  74  |  75
for i in range (0,10):
      print(      )  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(      )  |  66  |  65  |  64  |  63  |  62  |  61  |  60  |  59  |  58  |  57
for i in range (0,10):
      print(      )  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(      )  |  -1  |  -2  |  -3  |  -4  |  -5  |  -6  |  -7  |  -8  |  -9  |  -10


for i in range (0,10):
      print(      )  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(      )  |  0  |  -1  |  -2  |  -3  |  -4  |  -5  |  -6  |  -7  |  -8  |  -9
for i in range (0,10):
      print(       )  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(       )  |  -9  |  -8  |  -7  |  -6  |  -5  |  -4  |  -3  |  -2  |  -1  |  0
for i in range (0,10):
      print(        )  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(        )  |  9  |  8  |  7  |  6  |  5  |  4  |  3  |  2  |  1  |  0
```

Exercise-2b:  This is the reverse of Set-I. Predict the output of the program snippets below. For each of them, note down the effect of print. Finally test-out your predictions by running the programs.
```python
for i in range (0,10):
      print(i)  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(i)
for i in range (0,10):
      print(-i)  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(-i)
for i in range (0,10):
      print(i+5)  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(i+5)
for i in range (0,10):
      print(i-5)  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(i-5)
for i in range (0,10):
      print(i-10)  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(i-10)
for i in range (0,10):
      print(100-i)  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(100-i)
for i in range (0,10):
      print(i+100)  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(i+100)
for i in range (0,10):
      print(i*2)  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
for i in range (0,10):
      print(i*2)
for i in range (0,10):  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9
print(-1-i)
```

## 1.2 variations in for loops
    So far we have used the format for i in range (1,10). The first number in the range can be omitted,  it will be assumed as 0
```python
for i in range (10):
  print (i)  |  for i in range (0,10):
  print (i)
Output:  0 to 9, each printed on a new line.  |  Output: 0 to 9, each printed on a new line.
```

There is a facility to change the step by which i changes in the loop. Just add the step as the third number inside brackets. See the first example and predict the rest:
```python
for i in range (1, 11, 2):
  print(i)  |  Prints 1, 3, 5, 7, 9
for i in  range (1,100,5):
  print(i)
for i in  range (100,0, -5):
  print(i)
for i in  range (1,1000,100):
  print(i)
```

Finally, two more cases (i) strings of characters can be put in place of range of numbers. We will study this in later sessions. (ii) real numbers (numbers with decimal parts cannot be used in loops)
```python
for i in 'Jana Gana Mana':
  print(i)  |  J  a  n  a  G  a  n  a  M  a  n  a
for i in  range (1,10,0.1):
  print(i)  |  Error
for i in  range (1.0,10.0):
  print(i)  |  Error
```

1.3 Bringing in Some Graphics and Sound
    We have created sequences of numbers with "for i in range ( )" code. We can also diversify its use. We have also tried text (e.g., Namaste). Now, we can bring in some graphics.  Please ignore the first 5 program statements. Just focus on the for loops.  “t” refers to a turtle, a drawing facility in Python. You can ask turtle to go forward or backward, turn left or right etc.
Exercise-3:
```python
Code Snippet  |  Output
!pip3 install ColabTurtle
import ColabTurtle.Turtle 
t= ColabTurtle.Turtle
t.initializeTurtle()
t.speed(8)
for i in range(0,300,5):
     t.forward(i)
     t.right(90)
The following  code just changes (90) to (95)

for i in range(0,300,5):
     t.forward(i)
     t.right(95)
The following  code just changes (90) to (85)

for i in range(0,300,5):
     t.forward(i)
     t.right(85)
The following  code just changes (90) to (45)

for i in range(0,300,5):
     t.forward(i)
     t.right(45)
This code  changes  both forward and right

for i in range(0,300,5):
     t.forward(20)
     t.right(10)
NOW GO ON, BE ADVENTOUROUS, TRY OUT !!!
for i in range(0,300,5):
     t.forward(50)
     t.right(90)
     t.forward(50)
     t.left(60)
```

Chapter 2: Quick Taste -2
## 2.1 Some Selected Features of Python
    So far we were confined to playing with for i in range (start, end-1, step) code alone.  To diversify our examples, we introduce some selected Python features.
## 2.2 Arithmetic Operators in Python:
+, -, *, /, % and **.  All of these except the last two are common. ** stands for exponentiation. 5**2 gives 25.  % is deceiving, as an operator it has nothing to do with percentage.  Please note that the operator % is read as mod. It is to be understood in contrast with /.
Recall that in school maths, 9 divided by 4 gives quotient of 2 and remainder of 1
In calculators, 9 divided by 4 gives 2.25
In Python,    %   works like the remainder in school maths and /  works like in calculators.
           5/2= 2.5        5%2 = 1
Exercise-4:  Guess the result of division and mod given below, and test out with Python.
```python
Operation  |  Result (guess)  |  Code  |  Remarks
Divide 9 by 4  |  print(9/4)
Divide 8 by 4  |  print(8/4)
Remainder of division of 9 by 4  |  print(9%4)
Remainder of division of 8 by 4  |  print(8%4)
Remainder of division of 10 by 6  |  print(10%6)
Remainder of division of 10 by 11 (Tricky)  |  print(10%11)
Remainder of division of 2 by 4 (Tricky)  |  print(2%4)
Remainder of division of 0 by 4 (Tricky)  |  print(0%4)
```

## 2.3 Assignment and Comparison Operators in Python:
    These are >, >=, <, <=, != and ==.    The first four are obvious. != is for “not equal to”( ≠ ). All operators except != need two operands and all give results as True or False.
Exercise-5: Predict the output (True/False) of following comparisons:
| 2>3 | 3>3 | 5>3 | 3>=3 | 3!=3 | 3==3 | 7<7 | 7<=7 | -9 < -7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

The last operator needs an explanation.  == is for “equal to”.  Common symbol for “equal to” is =. But here we have ==. What is the difference? (It would be good to read the symbols as follows:    = as “assign” and == as “equals” ). In Python (and many programming languages), the meaning is as follows
       a=b   This is an action.  “Record value of b in the variable a”, consequently they become equal
       a==b This is a question. “Are the values of a and b equal ?” The answer is either True or False.
See how the following are properly read (It is advised that in assignment statements, always look at the right-hand side first).
         A=5     Assign the value 5 to variable A
         A=B    Assign the value of variable B to variable A
         A==B  Are the values of A and B equal ?
Think of a variable as a cassette that can record one song. Each value is a song. See how we interpret the following using this analogy:
         A=5   Record 5 in Cassette A
         B=6     Record 6 in Cassette B
         A=B     Record music from cassette B in cassette A. (What is already in A gets overwritten)
Classic problem of swapping variables A & B can now be tried. Try the following solution. What is the result? What is a way out? Use the analogy above and you will be able to solve it.
```python
a=5
b=100
a=b
b=a
print(a,b)  |  a=5
b=100


print(a,b)
100,100  |  100, 5
```

    Another assignment statement worth explanation is a=a+b. We know that a=b means store the value of the right-hand side (b) in the variable at the left-hand side (a).  But here same variable appears in the left and right. If the same variable  appears on the left hand side and right hand side, you can read the right hand side as current value of x and the left hand side as new value of x. (Remember, in all assignment statements, always look at the right hand side first).
    a = a + b  New value of a = current value of a+ value of b
Exercise-6:  (a) Write the values of a, b, c, and d after execution of each of the assignment statements.  The first two cases are  shown with updated values in bold.
| Assignment statements | a | b | c | d |
| --- | --- | --- | --- | --- |
| Initial values | 1 | 2 | 3 | 4 |
| a = b | 2 | 2 | 3 | 4 |
| c = a | 2 | 2 | 2 | 4 |
| a = c + a |  |  |  |  |
| b = b+1 |  |  |  |  |
| d = d * 2 |  |  |  |  |
| a = (a + b) * ( c + d) |  |  |  |  |

 Exercise-6:  (b) Write the values of a, b, c, d, e, and f after execution of each of the assignment statements.  Show updated values in bold or circled. Test by writing code.
| Assignment statements | a | b | c | d | e | f |
| --- | --- | --- | --- | --- | --- | --- |
| Initial values | 5 | 6 | 3 | 10 | 2 | 3 |
| a=a+1 |  |  |  |  |  |  |
| a=0 |  |  |  |  |  |  |
| a = c * e |  |  |  |  |  |  |
| a = c * f |  |  |  |  |  |  |
| f = f * e |  |  |  |  |  |  |
| d = a+b * c+e/f |  |  |  |  |  |  |
| a = a + 5 |  |  |  |  |  |  |
| e = a /e/f + d/d |  |  |  |  |  |  |
| a = 0 |  |  |  |  |  |  |

Exercise-6:  (c) Write the values of a, b and c after execution of each of the assignment statements. Show updated values in bold or circled. Test by writing code.
| Assignment statements | a | b | c |
| --- | --- | --- | --- |
| Initial values | 5 | 3 | 2 |
| c = a + b |  |  |  |
| c = a - b |  |  |  |
| c = a * b |  |  |  |
| c = a / b |  |  |  |
| c = a % b |  |  |  |
| c = a+b+a+b+c+c |  |  |  |
| c = 15+a+30+b+c |  |  |  |
| a = a + 1 |  |  |  |
| b = b * 5 |  |  |  |
| a = 12 |  |  |  |
| b = 3 |  |  |  |

## 2.4 Conditional Statement in Python:
    We will only take one of the conditional statements: if. As you have seen, print(i) will print the value of i.  You can put an if before it to make it conditional.
        if (i>5) :print(i)      now i will get printed only for values greater than 5.
    You can add an else part too
        if (age>18) :print(‘Adult’)
        else: print(‘Minor’)
```python
Now, here is a standard trick
Do % division of i with 2, 
if you get 0, then i is even (multiple of 2)
if it is 1 (not zero), then i is odd. (not multiple of 2)  |  Generally
Do % division of i with N, 
if you get 0, then i is a multiple of N
if it is not zero, then i is not a multiple of N
if (i%2==0) :print(‘Even’)
else: print(‘Odd’)  |  if (i%5==0) :print(‘Multiple of 5’)
else: print(‘Not a Multiple of 5’)
```

    Logical Operators :   and    or    not:  These have their English meanings.
A and B  True only if both A & B are true (routes - one after the other)
A or B    True if at least A or B is true        (parallel routes)
not A           not (True)= False, not(false)= True.
Exercise-7:: Following is called truth table. Try filling it. 1 and 0 are equivalent to True and False.
| A | B | A and B | A or B |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 |
| 1 | 0 | 0 | 1 |
| 1 | 1 | 1 | 1 |

Exercise-8::
| Expression | Value | Expression | Value | Expression | Value |
| --- | --- | --- | --- | --- | --- |
| 5>3  and  3>2 |  | 5>3  or  3>2 |  | not 5>3 |  |
| 2>3  and  3>=3 |  | 2>3  or  3>=3 |  | not 3>5 |  |
| 3!=3 and  3==3 |  | 3!=3 or  3==3 |  | not 5>5 |  |
| 7<7  and  7<=7 |  | 7<7  or   7<=7 |  | not 5==5 |  |

Now we will use the newly learned features and go back to for loops and try them out.
Exercise-9: Guess the results of the following for loops and the test. The small changes in each program is shown in bold, where possible.
```python
Loop SET-I  |  Remarks
for i in range (1,11):
  print(i)
for i in range (1,11):
  if (i>4):
    print(i)
for i in range (1,11):
  if (i>4):print(i)
for i in range (1,11):
  if (i>=4):print(i)
for i in range (1,11):
  if (i>15):print(i)
for i in range (1,11):
  if (i<4):print(i)
for i in range (1,11):
  if (i!=4):print(i)
for i in range (1,11):
  if (i==4):print(i)
for i in range (1,11):
  if (i=4):print(i)  |  Careful!
Loop SET II
for i in range (1,11):
  if (i%2 == 0): print(i)
for i in range (1,11):
  if (i%2 == 1): print(i)
for i in range (1,11):
  if (i%5 == 0): print(i)
for i in range (1,11):
  if (i%2==0): print(‘even’)
  if (i%2==1): print(‘odd’)
for i in range (1,11):
  if (i%2==0): print(‘even’)
  else       : print(‘odd’)
for i in range (1,25):
  if (i%5 == 0) and (i%3==0): print(i)
for i in range (1,25):
  if (i%5 == 0) or  (i%3==0): print(i)
for i in range (1,25):
  if not (i%5 == 0): print(i)
```

Exercise-10:  Write programs for displaying the described numbers Write first, then run and test.
| Numbers from 1 to 50. | Multiple of 2, from 1 to 70. |
| --- | --- |
| Multiple of 5, from 10 to 70. | Multiple of 50, from 1 to 1000. |
| Odd numbers from 1 to 50. | Multiple of 3 and also 5, from 1 to 25. |
| Even numbers from 1 to 50. | Numbers from 1 to 10 along with square and cube |
| Multiple of 3, from 1 to 25. | Multiple of 3 or 5, from 1 to 25. |
| Square and cube of even numbers from 1 to 10. | Cube of numbers which are multiples of 5 or 3, from 0 to 25 |

Exercise-11:  You are given the sequence. Understand the pattern and write Python code to produce the sequence. (Do not try to achieve result by making changes in for statements.
| a)1,2,3,4,5,6,7,8,9 | f)1,3,5,7,9 |
| --- | --- |
| b) 1,2,3,4,5,6,7,8,9,10 | g) 0,4,8,12,16,20 |
| c) 0,1,2,3,4,5,6,7,8,9 | h)10,9,8,7,6,5,4,3,2,1,0 |
| d) -25, -15, -5, 5, 15, 25 | i)10,8,6,4,2,0 |
| e) 0,1, 0,1, 0,1, 0,1, 0,1,0,1 | j)0,0,0,1,0,0,0,1,0,0,0,1 |

## 2.5 : Summing Instead of Displaying Numbers using for loops
    We wrote so many code snippets to display a variety of numbers. What if we wanted to get the total of those numbers each time? If we kept adding each number you displayed to a variable (shall we call it sum?), then we will achieve our aim, wont we?
```python
Code to display numbers from 0 to 5

for i in range (0,6):
  print(i)  |  Code to display sum of  numbers from 0 to 5
sum=0
for i in range (0,6):
  print(i)
  sum=sum+i
print(sum)
```

|  |  |  |  |  |  | SUM |
| --- | --- | --- | --- | --- | --- | --- |
| i=0 | i=1 | i=2 | i=3 | i=4 | i=5 |  |

    The variable Sum is initialized to 0. Loop runs taking i from 0 to 9, each time the value of i is displayed.  If we keep adding i to Sum each time, the final value of the variable Sum will be the answer we want. It will be a good idea to visualise this process assuming sum to be a bucket and each i to be cups with i units of water. You may shade the water level in each cup and shade the units added to the bucket named ‘sum’, in the figure given aside.
    You are reminded of the explanation for the strange statement sum=sum+i. Recall that if a variable appears on the left-hand side and right-hand side, you can read the right-hand side as current value of sum and the left-hand side as new value of sum. (In all assignment statements, always look at the right-hand side first).
Exercise-12:  Describe what the program does, predict and then test output
```python
Code Snippet  |  Description, Prediction & Remarks
sum=0
for i in range (1,6):
  print(i)
  sum=sum+i
print(sum)
for i in range (1,6):
  sum=0
  print(i)
  sum=sum+i
print(sum)
sum=0
for i in range (1,6):
  print(i)
  sum=sum+i
  print(sum)  |  Note the intend of last print
sum=0
for i in range (1,6):
  print(i)
  sum=sum+i
print(sum/5)
sum=0
for i in range (1,11):
  print(i)
  if (i%2==0):sum=sum+i
print(sum)
sum=0
for i in range (1,6):
  print(i)
  sum=sum+i*i
print(sum)
sum=0
for i in range (1,11):
  print(i)
  if (i%2==0):sum=sum+i*i
print(sum)
sum=0
for i in range (1,100):
  print(i)
  if (i%3==0) or (i%7==0):sum=sum+i*i
print(sum)
sum=0
for i in range (1,100):
  print(i)
  if(i%3==0)and (i%7==0):sum=sum+i*i
print(sum)
```

Exercise-13:  In exercise 11, you analysed, predicted the working of the given code snippets. Now do the reverse. Write programs based on the description given. Write first and test
| Sum of numbers from 1 to 50. | Sum of multiple of 5, from 10 to 70. |
| --- | --- |
| Sum of multiple of 3 or 5, from 1 to 25. | Sum of multiple of 50, from 1 to 1000. |
| Sum of numbers from -5 to 15. | Sum of multiple of 3 and 5, from 1 to 25. |
| Sum of squares of odd number from 1 to 10. | Sum of Cubes of numbers from 10 to 15. |
| Sum of square of even number from 1 to 10. | Sum of Square and cube of numbers from 1 to |
| Sum of cubes of odd numbers from 10 to 15. | Sum of numbers from 1 to 10, with square & cube. |
| 13. Sum of numbers from 1 to 50 which are neither multiples of 6 nor 5 | 14. Sum of numbers from 1 to 50 which are both multiples of 6 and 5 |
| 15. Sum of squares of numbers from 1 to 50 which are neither multiples of 6 nor 5 | 16. Product of numbers from 1 to 10 |

## 2.6 : Counting instead of Summing
You know that the following code will find sum of all numbers from 0 to 5:
    sum=0
    for i in range (0,6):
       sum=sum+i
    print(sum)
| i=0 | i=1 | i=2 | i=3 | i=4 | i=5 | COUNT |
| --- | --- | --- | --- | --- | --- | --- |

Instead of finding sum of all numbers from 1 to 5, what if I just wanted their count? It is obvious that the variable Sum may be changed to Count. What else? Guess!
    count=0
    for i in range (0,6):
      ……………………….
    print(count)
Let us visualise as in the case of Counting. The variable count is initialized to 0. Loop runs taking i from 0 to 5, each time if it is a multiple of 3, it is to be counted, and the variable count is to be updated.   The final value of the variable Count will be the answer we want. It will be a good idea to visualise this code assuming count to be a bucket and each i to be cups with various quantities of water.
    We can also find sum and count together. Then at the end of the program, we can calculate average.
    sum=0; count=0
    for i in range (0,6):
        count=......
        sum=sum+i
    print(sum,count,sum/count)
Exercise-14:  Write programs to find count of numbers described
| Count of numbers from 1 to 50. | Count of multiples of 5, from 10 to 70. |
| --- | --- |
| Count of multiple of 3 or 5, from 1 to 25. | Count of multiples of 50, from 1 to 1000. |
| Count of numbers from -5 to 15. | Count of multiples of 3 and 5, from 1 to 25. |
| Count of even numbers from 1 to 10. | Count of numbers from 7 to 34 which are multiples of both  4 and 6 |
| Count of odd numbers from 10 to 15. | Count of numbers from 1 to 50 which are multiples of 6 but not multiple of 5 |
| 11. Count of numbers from 1 to 50 which are both multiples of 6 and 5 | 12. Count of numbers from 1 to 50 which are neither multiples of 6 nor 5 |
| 13. Count of numbers from 7 to 34 which are not multiples of 4 | 14. Pi/4=1/1-1/3+1/5-1/7+1/9 …
15. Pi/2=2/1 * 2/3 * 4/3 * 4/5 * 6/5 * 6/7 * 8/7 … |

Chapter-3:  Python Basics
## 3.1.  Python Features
### Interpreted, Interactive, Object-Oriented, Open-Source, Easy To Learn, Easy To Read, Easy To Type, Portable, Extendable, Rich In Packages. Here is an edited list of Python approaches described as “The Zen of Python”, by Tim Peters:
| Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Readability counts.
Special cases aren't special enough to break the rules,  Although practicality beats purity.
Errors should never pass silently,  Unless explicitly silenced. | There should be one-- and preferably only one --obvious way to do it.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those! |
| --- | --- |

## 3.2 Comments, multi-line statements, multi-statement lines
# is used to comment Python programs. One statement can be in more than one line by using \ at the end. Many statements can be in one line, if separated by ;
```python
Comment  |  Multi-line statement  |  Multi-statement line
#program for addition
a=5
b=6
print(a+b)  |  a=25678888999999 \
89997788556677886  |  a=5; b=6; c=7
```

### Input - Mutiple inputs in same statement?
We can receive input when program runs with input( ) statement.
    x=input()
    print(x)
Whatever is typed by user is accepted as a string. If it is meant to be a number, use int( ) or float() to convert them.
See two versions to print numbers from 0 to N-1, where N is given when the program runs.
```python
N=input( )
for i in range(int(N)):
   print(i)  |  N=input(‘Give Range’)
for i in range(int(N)):
   print(i)
```

Exercise 1: Write a Python program that inputs three different integers from the keyboard, and then print the sum, the average and the product of these numbers.  Display the information as below:
    Input three different integers:
    13
    27
    14
    Sum is 54
    Average is 18
    Product is 4914
## 3.3 Variable names (identifiers)
Like in algebra where we use variables, Python also permits use of variables. Similar to our saying in algebra “Let a=5”, we can have a Python statement too: a=5. Here a is called a variable name or identifier. There are certain rules to be followed when naming variables. The rules are:
It should use only alphabets (upper and lower-case English alphabets and also characters of other world languages), digits and underscore ‘_’.   (We cannot use special symbols like !, @, #, $, % etc).
It should not begin with a digit and must have at least one alphabet.
It can be of any length (Do not overuse this provision!)
It should not be a reserved word (a word which has a special meaning in Python).
Here are the reserved words in Python. There is no need to remember all of these. Once you are familiar with Python, the common reserved words can be easily recognized. Note: only 3 have uppercase alphabets.
    False		await		else		import	pass
    None		break		except	in		raise
    True		class		finally	is		return
    and		continue	for		lambda	try
    as		def		from		nonlocal	while
    assert		del		global	not		with
    async		elif		if		or		yield
At a later stage you may also find it useful to know certain conventions in naming of variables: (a) class names start with uppercase and others are all lowercase. (b)  If a variable name starts with _ it is meant to be private variable and __ indicates strongly private. (c)  If a variable has leading and trailing __, it is a language defined special name.
Exercise 2: Classify the following as valid or invalid identifiers giving reasons for each invalid case.
```python
Identifier  |  Remarks  |  Identifier  |  Remarks  |  Identifier  |  Remarks
toTaAl  |  a1,1  |  for
a566  |  A/C_Number  |  For1
IIndTot  |  संख्या  |  FOR
a10000  |  A_1  |  1st
a1,0000  |  A-1  |  _a
2ndtotal  |  1999total  |  firstsum
ABD  |  IstRank  |  False1
```

    Python will tell you if an identifier you plan to use is valid. A function isidentifier() does this. For example, 'A/C_number'.isidentifier()returns False
## 3.4. Data Types: Numbers
Organization of data in any language has two levels: (i) basic types and (ii) super structures made of the basic data types. Let us look at three basic data types of Python
| Integer (No decimal part) | Float  (Decimal part present) |
| --- | --- |
| a          = 5
b          = -250
student_id = 25697 | interest_rate = 3.5
height        = 1.6
x       = -1027.683 |

Integers normally do not behave differently from floats. We can force behavior of integers as in examples below (Recall that Integer division ideally should give integer results).   LONG ?
```python
A=5, B=2
C=A/B
print(C)  |  2.5  |  A=5, B=2
C=int(A/B)
print(C)  |  2
A=5.0, B=2.0
C=A/B
print(C)  |  2.5  |  A=5.0, B=2.0
C=int(A/B)
print(C)  |  2
```

One more thing about integers, they have no size limit. Try this
          x=5**100000;  print(x)
    100099890379869416681626471319330624849934750830578004920283338007975850731624625203823576404317149791344357367267357191117087223553968539157458451546476042061840988683634681233609630835423737990420104226266686804483529043342258010198210289444899155707086901660605819760615719404885741285305873426398855977339413799099515925626119014563216304967288118167414655750126726815646494456029700763 …. <CUT> >>>>>>>It will run into pages.
## 3.5 Data Types: Characters (Strings)
Now we will look at characters (Actually characters are merely strings with just one element, we will learn about strings in a later chapter). They are handled almost in the same way (chr and ord do not work with strings, we will see later). Some arithmetic operators work on characters
```python
x = ‘@’
print(x)  |  x = ‘@’
print(x*5)  |  x ='a', 
y ='b'
print(x+y)  |  x =’a’ 
y =x+1
print(y)
@  |  @@@@@  |  ab  |  b
```

Characters have number codes (Unicode) behind them. You can see them using ord()
```python
x='a'
print(ord(x))  |  x='A'
print(ord(x))  |  x='₹'
print(ord(x))
97  |  65  |  8377
```

Unicode is a table of alphabets and symbols from all world languages. It is along table which has  65,535 entries. Here is a table of codes for alphabets for some selected languages
| English | Lower case: 97-123, Upper case: 65-91 |
| --- | --- |
| Malayalam | 3333-3385 |
| Hindi/Devanagari | 2309-2359 |
| Tamil | 2949-2999 |
| Arabic | 1877-1927 |

We can print all alphabets of a language using chr() which converts number codes to characters.
    for i in range(2309,2359):
         print(chr(i), end=' ')
    अ आ इ ई उ ऊ ऋ ऌ ऍ ऎ ए ऐ ऑ ऒ ओ औ क ख ग घ ङ च छ ज झ ञ ट ठ ड ढ ण त थ द ध न ऩ प फ ब भ म य र ऱ ल ळ ऴ व श
## 3.6 Complex Numbers (may be skipped by learners with non-Maths background)
Complex numbers are a pair of numbers called real and imaginary in the form z=x+iy, where i is square root of -1. See the following examples.
```python
Define & Print  |  Operations  |  Conversions: Require import  |  Conversions: Require import
z=complex(5,6)
print(z)
print(z.real)
print(z.imag)  |  Z1=5+6j
Z2=3+4j
Z3=Z1+Z2
Z4=Z1*Z2
Z5=1/Z2
print(Z3,Z4,Z5)  |  Rect to Polar
import cmath
z1=5+6j
cmath.polar(z1)  |  Polar to Rect
cmath.rect(7.81,0.87)
(5+6j)
5.0
6.0  |  (8+10j) 
(-9+38j) 
(0.12-0.16j)  |  (7.81,0.87)
Magnitude & phase  |  (5.000+5.999j)
```

    There are more data types: Bool (True/False), bytes, bytearray, memoryview etc. You can force (cast) a data into a particular type by using int(), float(), str() functions. You can check type with type() function. You can check if a variable is of a particular type by using isinstance. Eg: isinstance(1+2j, complex)
## 3.7. Output formatting
    Operations on Floats (real) can produce long sequence of digits after decimal point. You can use formatting to print in the format you want. The string '%1.2f' below indicates width of the digits before and after decimal point as 1 and 2 respectively. If we give '%1.2f>', the output gets right adjusted
```python
A=1
B=3
print(A/B)  |  A=1
B=3
print('%1.2f' % ( A/B))
0.3333333333333333  |  0.33
```

You can use formatting with integers also (Note leading blank spaces)
```python
for i in range (1501):
  if i%90==0: print(i)  |  for i in range (1501):
  if i%90==0: print('%4d'% i)
0
90
180
…
1350
1440  |  0
  90
 180
…
1350
1440
```

Escape Sequences are characters that don’t print anything but have an effect.  Most popular is \n (back-slash-n) is used to print new line on the screen. Try also \b  back space
```python
\t for Tab  |  \a for alert  |  \n for newline
for i in range(0,10):
  print(i, end='\t')  |  for i in range(0,10):
  print(i, end='\a')  |  for i in range(0,10):
  print(i, end='\n')
default
```

    Python print uses \n at the end of print, automatically, as the last example above may reveal. Suppose you want to avoid it ? Use print(i, end=' ')
```python
Ordinary print  |  print with \n supressed
for i in range(0,10):
  print(i)  |  for i in range(0,10):
  print(i, end=' ')
0
1
2
3
…  |  0 1 2 3 4 5 6 7 8 9
```

    Note:  There are many ways to format output (text and background) color and style. This is left as an exercise to the learner.
## 3.8. Python Operators and Expressions
```python
Arithmetic operators  |  Relational Operators  |  Logical Operators

Binary Logic Operators 
(may be skipped by first-time programming learners)
(operates bit by bit on binary equivalent)
&, |, ^, ~, <<, >>
a=5; b=6;   print(a&b)  4    (in binary 5=101, 6=110)  |  Binary Logic Operators 
(may be skipped by first-time programming learners)
(operates bit by bit on binary equivalent)
&, |, ^, ~, <<, >>
a=5; b=6;   print(a&b)  4    (in binary 5=101, 6=110)  |  Assignment Operators (Short-forms)
=     +=,  -=,   *=,  /=,  %=
           
                        a=a+1               a+=1
```

Mutiple assigments:
    x, y = 5, 6
Swapping can be done by
    x,y = y,x
Expressions, use of brackets and precedence
A Python expression is made up of variables, values and operators (and also functions calls which return values, as will soon see). You can use any number of operators and operands in an expression. Following are examples:
| 5
a
a+b * c-d | a*b/c
a**b/b**c
a+b**2 | p+q*2
x*sin(theta)
5+3%3 | a+b*c-d/d*e%f
5**1000
sin(theta)**2 |
| --- | --- | --- | --- |

However, there are some rules to be followed on such occasions. Suppose we want to calculate
a+b
  c
We may naturally write a+b/c. However this may be confused (by you, not Python !) with an expression such as
    a + b which has a different meaning. For a = 6, b=4, c=2
      c
| a+b      = 6+4       = 10   = 5	
   c	     2	        2 | a+ b    =  6+ 4      =    6+2     = 8
       c             2 |
| --- | --- |

So, in Python, if we write a+b/c as in the above case, what could be the result ? 5 or 8? Before we answer that, we will learn how to avoid the confusion. Always put parenthesis to make clear to Python what you mean.
| i) (a+b) can be written as (a+b)/c
       c | ii) a+ b can be written as a+(b/c)                                                                  
         c |
| --- | --- |

Exercise 3 (a) Write the Python expression for each of the following mathematical expressions. (Use parenthesis to ensure correctness, if required)
| 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- |
| r2 | a .b
a+b | p + q 	 	 r2 | a – b 
a . b | (a+b)2 | a + b+ c
a . b . c |

The answers may be written in coding sheet  (one character per box)
| 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

Exercise 3 (b) Predict the output  of each of the following expressions:
| ((1+2) * (3 – 4)) | ( (3+2)%5) | (-13/2)%(-3*2) | (3%5)+(5%3) |
| --- | --- | --- | --- |

Let us now go back to the question what Python will do with the expression a+b/c. If given without brackets will Python take it as a+b or a+ b ?
                                                 c             c
Python  will take it as the second one. This is because Python has a standard order in which operators are applied. This standard order of arranging operators is known as  precedence of operators.
| ( ) | Whatever is inside ( ) will be calculated first |
| --- | --- |
| ** | Exponentiation |
| Unary +, - | +x, -y |
| *   /     % | Among these, whichever comes first from left |
| +    – | Among these, whichever comes first from left |
| ==, !=, >, >=, <, <=, is, is not, in, not in | Comparisons, Identity, Membership operators |

Example: Consider the following expression and see how the evaluation is taking place.
	       5+6 * 2 – 4
                  5 + 12 – 4
                      17 – 4
                          13
Exercise 4  Predict  the value of each of the following Python arithmetic expressions using the precedence of operators.
| (a) 1 + 2 * 3 – 4 | (b) 1 + 2 % 3 – 4 | (c) 13/2 % 3 – 4 |
| --- | --- | --- |
| (d) 100/10/2 % 3 | (e)(10+2)*3 |  |

Exercise 5  Predict  the value of the following Python comparison/logical expressions given below
| p=5, q=10, r=15, s=0 | x= 'A', y= 'B', z= 'C' |
| --- | --- |
| (p+q)>(r+s)
(p/q)<(s/r)
(p*q)==(r*s)
(p+q+r)!=(r+q+p)
(p+q)>=(s/r)
((p+q)>2) or ((p+r)>q) | x>y
(x<y) and (y<z)
(x<y) or (y>z)
(x==y) or (y== 'B')
((x+1)==y) |

There is no need to be an expert in precedence of operators. Just use brackets to make things clear
