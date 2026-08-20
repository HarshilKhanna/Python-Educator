# Conditionals

> Source: Chapter 4 §4.1–4.5 (if / elif / nested if-else), §4.8 (break, continue, pass), §4.9 (loop comparison), §4.10 (finding biggest)

**Curriculum graph node:** Conditionals

---

Chapter-4: Python Control Statements
Keywords: if, if-else, elif, for, iteration, iterables, loops, block/suite, index, while, break, continue, pass
## 4.1 Control Statements
Typically, statements in a program are executed one after the other, in the order in which they appear in the program.  Python permits this order to be changed, if desired.  Python features used for this are known as branching statements or conditionals or control statements/structures.  We are already familiar with for loop and if-else statement in this category. We will learn all control statements systematically in this session.
## 4.2 if Statement
Whenever you face a situation where you need to say: Do these only if such-and-such a condition is true, you will find an if statement appropriate. The form of an if statement is as follows:
    if (condition):
    		statement 1
    		statement 2
    		:
    		statement n
    The if statement starts with the keyword ‘if’ followed by a condition, followed by a colon and any number of Python statements (a suite / block), all indented.  The condition is a relational or logical expression like (a>5),((c>100)and(b==k)) etc.  If the condition is True, then the statements in the block are executed, and if False, the statements are ignored.
```python
if (m<=39):
  print(‘Failed’)
  print(‘Bad luck’)  |  if (m>39): print(“Passed”)  |  if (ans==’Y’): print (“OK”)

```

Here are some examples of how if statements could begin (the brackets are not mandatory):
```python
if ((a+b)== x):  |  if ((a>b) and (b>c)):  |  if ((a>b) or (c==d)):
if a+b == x:  |  if (!(a>b)):  |  if (x%2==0):
```

EXAMPLE: Write a program to accept the age and print out if the person is an adult (over 18). Note that you are not required to print out minor status, there will be no output in that case. We will address it in the next section.
    	age=input(‘give your age’)
    	if age>=18: print(‘You are an adult’)
Exercise 1 In all the tasks given below, you may note that only one condition is considered. No action is suggested if the condition is false. This will be addressed in the next section.
```python
Write a program to ask the year of birth of a person and calculate the age in the year 2075 and if the result (age) is more than 90 then give message that “It is likely that you may not be alive then”.
Write a program to accept two integers and when the numbers are equal, then print out  “EQUAL”.
Write a program to accept the grade of a student and print out if the student has a first class. (Only grade ‘A’ is first class).
Write a program that reads in two integers and display “Multiple” if the first is a multiple of the second.  (Hint :use the modulus operator). Test the program for different Use-cases.
Write a program to accept 3 integer numbers and print out whether they are all equal.
Write a program to accept the choice of the user (0 or 1) and show a happy face :-) for choice 0.
```

## 4.3 if-else statement
The form of an if-else statement is:
    	if (condition):
#### 		Do this if the condition  is True
    else:
    		Do this if the  condition  is False
    This simply says that if the expression given after if is true, then the first group of statement(s) is to be executed and if false, the second group of statements is to be executed.  Thus, one of the two set of statements will always be executed, whereas in the simple if statement, the statements inside the if-block were either executed or skipped.
EXAMPLE: |In the section above, we wrote a program to accept the age and print out if the person is an adult (over 18). We now modify it to also print out minor status, using if-else.
    	age=input(‘give your age’)
    	if age>=18: print(‘You are an adult’)
    	else: print(‘You are a minor’)
We can also achieve this with two if statements. Compare the two. Isn’t the first one more compact ?
         age=input(‘give your age’)
    	if age>=18: print(‘You are an adult’)
    	if age<18 : print(‘You are a minor’)
Exercise 2 In the tasks in exercise-1, only one condition is considered. No action was suggested if the condition considered was false. This exercise requires you to address cases when  condition is true and also when it is false. You can use if-else(or two separate if statements, which will be less compact).
```python
Write a program to ask the year of birth of a person and calculate the age in the year 2075 and if the result (age) is more than 90 then give message that “It is likely that you may not be alive then” and otherwise print out “Your age in 2075 will be ….”
Write a program to accept two integers and then print out either “the numbers are equal” or “the numbers are not equal”.
Write a program to accept the grade of a student and print out whether the student has a first class or not. (Only grade ‘A’ is first class).
Write a program that reads in two integers and display “Multiple”/”Not Multiple” if the first is a multiple of the second.  (Hint :use the modulus operator). Test the program for different Use-cases.
Write a program to accept the age and print out if the person is an adult (over 18) or a minor.
Write a program to accept 3 integer numbers and print out whether they are all equal or not
Write a program to accept the choice of the user (0 or 1) and show a happy face :-) for choice 0 and sad face :-( for choice 1. (you can research on printing a smiley itself)
```

## 4.4 Nested if-else
    if-else can be used in a nested manner as follows: Let us write a program to ask for two numbers and let the user choose an arithmetic operator and then print out the result of applying the operator
    a=input(‘first number’); b=input(‘second number’)
    c=input('1 for +, 2 for -, 3 for * and 4 for /')
    a=int(a); b=int(b); c=int(c)
    if (c==1):print(a+b)
    else:
      if (c==2):print(a-b)
      else:
        if (c==3):print(a*b)
        else:
          if (c==4):print(a/b)
- Test the program with following use-cases.
| a=7, b=3, c=1 | a=7, b=3, c=3 | a=7, b=3, c=4 | a=7, b=3, c=77 |
| --- | --- | --- | --- |

Exercise 3   (a) Write a program to accept the number of telephone calls made by a customer and then print out the rate as per the following tariff:
| No of Calls | Rs/call |  |
| --- | --- | --- |
| Up to 100 | 1.0 |  |
| 100-300 | 0.9 |  |
| 301 and above | 0.6 |  |

- (b) Predict output of the following code snippet
```python
N=input(‘a positive integer’)
if (n==0): print(“ganga”)
else if (n==1  ): print(“ volga”)
else if (n== 2 ): print(“ yamuna”)
else if (n==3  ): print(“kaveri ”)
else if (n==4  ): print(“ hubli”)
else if (n==5  ): print(“ nila”)
else :print(“None”)
```

- Finding biggest/smallest
Let us develop a method to find the biggest or smallest of given numbers. We will develop this fully in later stages, here we will understand basic logic.
Let us first try to read two numbers and print out the biggest. Here is an innocent first attempt:
    a=input();    b=input();        a=int(a);     b=int(b);
    if (a>b): print('Biggest=',a)
    if (b>a): print('Biggest=',b)
| Test Case (i) a=15, b=11 | Test Case (ii) a=25, b=60 | Test Case  (iii) a=30,b=30 |
| --- | --- | --- |

What does the testing tell you ?  Now try a slightly different one:
    a=input();    b=input()
    a=int(a);     b=int(b);
    if (a>=b): print('Biggest=',a)
    if (b>=a): print('Biggest=',b)
| Test Case (i) a=15, b=11 | Test Case (ii) a=25, b=60 | Test Case  (iii) a=30,b=30 |
| --- | --- | --- |

### Let us improve the program with if-else:
```python
Using if  |  Using if-else
a=input();    b=input()
a=int(a);     b=int(b);
if (a>=b): print('Biggest=',a)
if (b>=a): print('Biggest=',b)  |  a=input();    b=input()
a=int(a);     b=int(b);
if (a>=b): print('Biggest=',a)
else     : print('Biggest=',b)
```

| Test Case (i) a=15, b=11 | Test Case (ii) a=25, b=60 | Test Case  (iii) a=30,b=30 |
| --- | --- | --- |

    Let us now consider  a program to find biggest of 3. See the code using if and also if-else. The first approach is to check the complete condition that each one is the biggest. But this is not required. If we know that a is not the biggest, then we need only test b and c. If b is not biggest then it has to be c. This is done with if else.
```python
a=input( ); b=input( ); c=input( )
 a=int(a);     b=int(b); c=int(c);
if (a>=b)and(a>=c):print('Biggest=',a)
if (b>=a)and(b>=c):print('Biggest=',b)
 if (c>=b)and(c>=a):print('Biggest=',c)  |  a=input( ); b=input( ); c=input( )
a=int(a);     b=int(b); c=int(c);
if (a>=b)&(a>=c) :print("Biggest=",a)
else:
  if (b>=c)      :print("Biggest=",b)
  else           :print("Biggest=",c)
```

- Test the program with following use-cases.
| 7,3,1 | 2,4,6 | -1,3,-7 | 3,8,5 | 8,8,8 |
| --- | --- | --- | --- | --- |

    You may try finding biggest of 4 or 5 numbers in the above fashion. You will realise that the code becomes longer and longer. There is a better way. You can compare two at a time. The biggest you get in each comparison is kept in a special variable and all comparisons are done with that. Let us call this variable big. Let us assume its value as a, to begin with.
    a=input( ); b=input( ); c=input( )
    a=int(a);   b=int(b);   c=int(c)
    big=a
    if b>big, big=b
    if c>big, big=c
    print(big)
Now also the code will be longer if more numbers are to be compared, but the logic is simpler. Test the program with following use-cases.
| 7,3,1 | 2,4,6 | -1,3,-7 | 3,8,5 | 8,8,8 |
| --- | --- | --- | --- | --- |

We can use a loop to generalise the program for larger data set. We will see that later.
Exercise 4  Write a program to read 4 numbers and print out the smallest.
## 4.5. elif
Look again at the code for finding biggest of 3 numbers we discussed earlier. We find that else-if appearing repeatedly. Python lets you write in a single word - elif. There is no difference in effect, but the code can be made tidy and compact.
```python
a=input( ); b=input( ); c=input( )
a=int(a);     b=int(b); c=int(c);
if (a>=b)&(a>=c) :print("Biggest=",a)
else:
  if (b>=c)      :print("Biggest=",b)
  else           :print("Biggest=",c)  |  a=input( ); b=input( ); c=input( )
a=int(a);     b=int(b); c=int(c);
if (a>=b)&(a>=c) :print("Biggest=",a)
elif (b>=c)      :print("Biggest=",b)
else             :print("Biggest=",c)
```

Let us also use elif in the simple caluculator program which accepts a command for basic arithmetic: 1 for +, 2 for - , 3 for * and 4 for /
```python
a=input(‘first number’);  a=int(a)
b=input(‘second number’); b=int(b)
c=input('Type 1for+,2for,3for*,4for/')
c=int(c)
if (c==1):print(a+b)
else: 
   if (c==2):print(a-b)
   else:
     if (c==3):print(a*b)
     else:
       if (c==4):print(a/b)
       else: print(‘wrong operator’)  |  a=input(‘first number’);  a=int(a)
b=input(‘second number’); b=int(b)
c=input('Type 1for+,2for-,3for*, 4for/')
c=int(c)
if (c==1) :print(a+b)
elif(c==2):print(a-b)
elif(c==3):print(a*b)
elif(c==4):print(a/b)
else: print(‘wrong operator’)
```

Here is another example to convert digits to roman letters. You may complete it.
```python
N=input(‘Give a digit to convert to Roman Numeral’)
if (N==0):  print(‘Romans had no Zero!’)
elif(N==1): print(‘I’)
elif(N==2): print(‘II’)






else: print(‘This program accepts only digits 0-9’)
```

Exercise 5
1. Electricity consumers are divided into category 1, 2 and 3.  Read the category and number of units of electricity used and then print out the total charge according to the following rates: (Category: 1: Rs 10, Category: 2: Rs 15, Category: 3: Rs 20)
2. Write a program to input a character and print out if it is a vowel. (a) Using if-else statement (b) Using elif statement.  Note: Trace the flow of execution for the following cases (i) ‘a’ (ii) ‘o’ (iii) ‘k’
Special usage of if
Python provides for special short form usages for commonly occurring requirements. We may very often have to set the value of a variable to one of two values, depending on a condition, such as : If category is 1, then rate is 10%, otherwise it is 15% This  can be written in straightforward manner or short hand, as follows:
```python
if (cat==1): rate=10
      else: rate=15  |  rate=10 if (cat==1) else 20
```

A short hand form is also permissible in writing conditions:
```python
if(x>50 and x<60):  |  if x>50 and <60:
```

4.8 break, continue, and pass in loops
With the break statement we can stop the loop (both for and while) even if the while condition is True:
```python
i = 1
while i < 10:
  print(i)

  i =i + 1  |  i = 1
while i < 10:
  if i == 5: break
  print(i)
  i =i + 1
1 2 3 4 5 6 7 8 9  |  1 2 3 4
```

The continue statement stops the current iteration, and continues with the next:
```python
i = 1
while i < 10:
  
  print(i)
  i =i+ 1  |  i = 1
while i < 10:
  if i == 5:  i=i+1; continue
  print(i)
  i=i+1
1 2 3 4 5 6 7 8 9  |  1 2 3 4   6 7 8 9
```

The pass statement does nothing. But it is surprisingly very useful. We will see that later.
```python
i = 1
while i < 10:
  
  print(i)
  i =i+ 1  |  i = 1
while i < 10:
  if i == 5:  pass
  else: print(i)
  i=i+1
1 2 3 4 5 6 7 8 9  |  1 2 3 4   6 7 8 9
```

EXAMPLE: (These are easier with for loops)
```python
Summation of numbers from 0 to N
N=input( )
sum = 0; i = 1
while i <= N:
    sum = sum + i
    i = i+1    
print(sum)
```

A useful form of while loop is the while(True) format. This loop has an always true condition, thus will never stop as far as the condition checking is concerned. But the trick is to check the condition inside the loop and break the loop. The advantage is that you can begin writing the loop without bothering about the terminating condition and write the statements and at an appropriate point, break out.
    while(True):
      Statement
      Statement
      if (…): break
      Statement
See the previous examples rewritten
```python
Summation of numbers from 0 to N
N=input ( )
sum = 0; i = 1
while (True):
    sum = sum + i
    i = i+1 
    if i>N: break   
print(sum)
```

Exercise 10
Write ‘for’ loops for the following, making use of ‘continue’ or ‘break’ as required.
    Print numbers from 1 to 100 except 75.
    Print characters from ‘a’ to ‘z’ except ‘p’.
    Print numbers from 50 to 100 except 56 and 79.
    Print characters from ‘a’ to ‘z’ except ‘p’, ‘q’ and ‘r’.
    Input integers until a negative number is typed in. However, the printing (and inputting) should stop if the number is a multiple of 7.
    Input lowercase alphabet characters and echo them, stop printing if the character is ‘m’ or ‘n’.
Predict
## 4.9. Comparison between loops
The ‘while’ is convenient to use when we don't have any idea as to how many times the loop will be executed, and the ‘for loop’ is usually used in those cases when we are doing a fixed number of iterations. The ‘for loop’ is also convenient because it has all the control information of the loop in one place. It is possible that the ‘while’ loops may never execute the statement within the loop at all. This is because the test is done at the beginning of the loop, and the test may fail during the check itself.
    Exercise 11  How many times does each of the following loops execute the print statements?
```python
i = 5
while i < 10:
  print(i)
  i =i + 1  |  i = 5
while i <= 10:
  print(i)
  i =i + 1  |  for i in range (2,10):
   for j in range (3,7):
        print(i*j)
i = 5
while i > 10:
  print(i)
  i =i + 1  |  i = 5
while i >0:
  print(i)
  i =i + 1  |  for i in range (10):
   for j in range (5):
        print(i*j)
```

## 4.10 Finding biggest of any set of numbers
We had earlier written a simple program to find biggest of 3 given numbers.
    a=input( ); b=input( ); c=input( )
    a=int(a);   b=int(b);   c=int(c)
    big=a
    if b>big, big=b
    if c>big, big=c
    print(big)
Now let us generalize it with while loop so that it can handle any count of numbers. We will accept numbers through input until a zero is typed. Note that we input the first number outside the loop and initialize big with the first value.
```python
Usual while loop  |  Using while(True)
x=int(input())
big=x
while x!=0:
    if x>big: big=x
    x=int(input())

print(big)  |  x=int(input())
big=x
while True:
    if x>big: big=x
    x=int(input())
    if (x==0): break
print(big)
```

