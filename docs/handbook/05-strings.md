# Strings

> Source: Chapter 6

**Curriculum graph node:** Strings

---

Chapter 6: Python Data Structures: Strings
## 6.1. Introduction
In last session we tried out lists which are similar to arrays in other programming languages but has many additional behaviours and features. Strings are basically like lists/arrays. They are lists/arrays of characters. While elements of lists can be changed anytime (mutable), strings are immutable, as we will soon see.
## 6.2. Initialising Strings
input( )  statement accepts input as string and it is therefore one way of intialising strings:
    message=input()
| S1='janaganamana'
S2='Jana Gana Mana' | alphabets='abcdefghijklmnopqrstuvwxyz' | alphabets='abcdefghijklmnopqrstuvwxyz' |
| --- | --- | --- |
| Digits='0123456789'
Digit='0' | Answer='y'
String='' | S='''multi line
String?''' |

Note:  single, double and triple quotes can be used to enclose strings. With triple quotes you can define strings that are spread into more than one line.
## 6.3. Processing Strings as lists
    As already mentioned, strings are basically a list of characters. You can access each character using index, as done in lists. Characters can be referred to in two ways, using usual indices and also negative indices. For the string  x=”janaganamana”, this is shown below
| j | a | n | a | g | a | n | a | m | a | n | a |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] |
| x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] | x[ ] |

Slicing can also be done, as in lists.
    x='janaganamana'
    y=x[0:3]               # y will be 'jan'
Strings are immutable. You cannot change, delete or insert characters in/into existing strings. However, you can delete the string altogether or redefine it altogether.
| String is immutable | But strings  can be deleted | … and can be redefined |
| --- | --- | --- |
| s='town'
s[0]= 'g' | s='gown'
del s | s='town'
s='gown' |
| error |  |  |

## 6.4. Operators applicable to strings:
Some of the arithmetic operators are applicable to strings: + and *. The operator + concatenates two strings, simply join them together (Unix/Linux has a command named cat, and a variation named dog !) The operator * can be used to multiply (repeat) strings.
```python
a1='ta'
a2='ka'
a3='di'
a4='mi'
a=a1+a2+a3+a4
print(a)
t=(a+' ')*8
print(t)
```

## 6. 5. Using in and not in to process Strings or its Slices:
    i in and i not in can be used with strings as exemplified below
    for i in 'Mary had a little lamb':
      print(i, end=' ')
    M a r y  h a d   a  l i t t l e  l a m b
Example below uses i in with for and if to label a string with v where vowels occur and _ elsewhere.
```python
for i in 'Mary had a little lamb':
  if i in 'aeiou': print('v', end='')
  else :print('-', end ='')  |  -v----v--v--v---v--v--
```

We can modify the above program to count vowels and non vowels
```python
v=0
n=0
for i in 'janaganamana':
  if i in 'aeiou': v=v+1
  else:n=n+1
print(v,n)  |  6, 6
```

Do you know that e is the most frequently used character in English (But  Gadsby,  a 1939 novel by Ernest Vincent Wright, does not have a single e !). You can try typing in a long sentence and check if there is an e:
```python
sentence=input()
if 'e' in sentence: print('Hmmm Not as clever as Gadsby')
else: print('Wow ! In the same class as Gadsby')
```

    i in also has an i not in option
```python
email=input()
if '@' not in email: print('Invalid email')
```

## 6.6. String Functions
There are diverse strings functions. They are exemplified below. For some of them, you have to import string package. Note that some functions are called in different style. Use print statement to see the results
6.6.1 Function related to case change.
| s1='i love you'
s1.capitalize() | 'india'.capitalize() | s1='i love you'
s1.upper() | s2=”I Love You”
s2.lower() |
| --- | --- | --- | --- |
| I love you | India | I LOVE YOU | i love you |

6.6.2 Functions related to length and count
```python
s1='harisri'
l=len(s1)  |  s2='i love you'
s2.count('o')  |  print('harisri'.count('i'))
7  |  2  |  2
```

6.6.3 Functions related to find and replacement
```python
s1='Superrrrrrrrrrrrr'
s1.find('r')  |  s1='Superrrrrrrrrrrrr'
s1.find('a')  |  s1='Superrrrrrrrrrrrr'
s1.find('a')
4  |  -1  |  -1
s1='Superrrrrrrrrrrrr'
s1.index('r')  |  s1='Superrrrrrrrrrrrr'
s1.index('a')  |  s1='Superrrrrrrrrrrrr'
s1.index('a')
4 (same effect as find)  |  Value Error  |  Value Error
s2='i love you'
s2.replace('love','hate')  |  s3='organize'
s4=s3.replace('z','s')
print(s3,s4)  |  s5='Hellooooooooo'
s6=s5.replace('o','_')
print(s6)
Error  |  organize organise  |  Hell________________
```

    You can also use find in reverse direction, using rfind()
| s1='Superrrrrrrrrrrrr'
s1.rfind('r') |
| --- |
| 16 |

Note: Sophisticated searching and matching using Regular Expressions is discussed in a separate chapter. Here is a sample:
    import re
    print(bool(re.match(X,Y)))
| Regular Expression   X | String Y | String Y |
| --- | --- | --- |
| Regular Expression   X | Matching  examples | Non-matching  examples |
| [Pp]ython | Python, python |  |
| trivandrum | trivandrum | trevandrum, trxvandrum |
| tr[ie]vandrum | Trivandrum, trevandrum | trxvandrum |
| (m|h|b|l|t)ics | politics, aerobics |  |
| [mhblt]ics | politics, aerobics, |  |

6.6.4 Function for Split & Join
Split is useful to convert sentences to words
| Cannot split words | Splits at – into words | Sentence to word list |
| --- | --- | --- |
| x='TaKaDiMi'
x.split() | x='Ta-Ka-Di-Mi'
x.split(sep="-") | x='I love you’
x.split() |
| ['TaKaDiMi'] | ['Ta', 'Ka', 'Di', 'Mi'] | ['I', 'love', 'you'] |

The splitlines( ) method splits a string into a list. The splitting is done at line breaks.
```python
s = 'Pat sat on a mat\nPat sat on a hat'
x = s.splitlines()
print(x)
['Pat sat on a mat', 'Pat sat on a hat']
```

Join is reverse of split. The method can be called on the string itself .
```python
x=['TaKaDiMi']
y = '-'.join(x)
print(y)  |  x=['Ta', 'Ka', 'Di', 'Mi']
y = '-'.join(x)
print(y)  |  x=['I', 'love', 'you']
y = ' '.join(x)
print(y)
TaKaDiMi  |  Ta-Ka-Di-Mi  |  I love you
```

6.6.5 Functions  for  justification, stripping
```python
s='I love you'
s1=str.ljust(s, 20)
s2=str.rjust(s, 20)
s3=str.center(s, 20)
print(s1)
print(s2)
print(s3)  |  I  |  l  |  o  |  v  |  e  |  y  |  o  |  u
s='I love you'
s1=str.ljust(s, 20)
s2=str.rjust(s, 20)
s3=str.center(s, 20)
print(s1)
print(s2)
print(s3)  |  I  |  l  |  o  |  v  |  e  |  y  |  o  |  u
s='I love you'
s1=str.ljust(s, 20)
s2=str.rjust(s, 20)
s3=str.center(s, 20)
print(s1)
print(s2)
print(s3)  |  I  |  l  |  o  |  v  |  e  |  y  |  o  |  u
s='I love you'
s1=str.ljust(s, 20)
s2=str.rjust(s, 20)
s3=str.center(s, 20)
print(s1)
print(s2)
print(s3)
s='I love you'
s1=str.ljust(s, 20,'*')
s2=str.rjust(s, 20, '*')
s3=str.center(s, 20, '*')
print(s1)
print(s2)
print(s3)  |  I  |  l  |  o  |  v  |  e  |  y  |  o  |  u  |  *  |  *  |  *  |  *  |  *  |  *  |  *  |  *  |  *  |  *
s='I love you'
s1=str.ljust(s, 20,'*')
s2=str.rjust(s, 20, '*')
s3=str.center(s, 20, '*')
print(s1)
print(s2)
print(s3)  |  *  |  *  |  *  |  *  |  *  |  *  |  *  |  *  |  *  |  *  |  I  |  l  |  o  |  v  |  e  |  y  |  o  |  u
s='I love you'
s1=str.ljust(s, 20,'*')
s2=str.rjust(s, 20, '*')
s3=str.center(s, 20, '*')
print(s1)
print(s2)
print(s3)  |  *  |  *  |  *  |  *  |  *  |  I  |  l  |  o  |  v  |  e  |  y  |  o  |  u  |  *  |  *  |  *  |  *  |  *
s='I love you'
s1=str.ljust(s, 20,'*')
s2=str.rjust(s, 20, '*')
s3=str.center(s, 20, '*')
print(s1)
print(s2)
print(s3)
```

6.6.6 Functions related to typechecking & miscellaneous functions
            s1='India' s2='4G' s3='786' s4='a+b' s5='a,b' s6='bee+'
    Two ways to call type-checking functions (i) s1.isalnum()  (ii) str.isalnum(s1)
| str.isalnum(s1) | T | str.isalpha(s1) | T | T | str.isdecimal(s1) | str.isdecimal(s1) |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| str.isalnum(s2) | T | str.isalpha(s2) | F | F | str.isdecimal(s2) | str.isdecimal(s2) |  |
| str.isalnum(s3) | T | str.isalpha(s3) | F | F | str.isdecimal(s3) | str.isdecimal(s3) |  |
| str.isalnum(s4) | F | str.isalpha(s4) | F | F | str.isdecimal(s4) | str.isdecimal(s4) |  |
| str.isalnum(s5) | F | str.isalpha(s5) | F | F | str.isdecimal(s5) | str.isdecimal(s5) |  |
| str.isalnum(s6) | F | str.isalpha(s6) | F | F | str.isdecimal(s6) | str.isdecimal(s6) |  |
| str.isnumeric(s1) |  | str.isdigit(s1) | str.isdigit(s1) | F | F |  |  |
| str.isnumeric(s2) |  | str.isdigit(s2) | str.isdigit(s2) | F | F |  |  |
| str.isnumeric(s3) |  | str.isdigit(s3) | str.isdigit(s3) | T | T |  |  |
| str.isnumeric(s4) |  | str.isdigit(s4) | str.isdigit(s4) | F | F |  |  |
| str.isnumeric(s5) |  | str.isdigit(s5) | str.isdigit(s5) | F | F |  |  |
| str.isnumeric(s6) |  | str.isdigit(s6) | str.isdigit(s6) | F | F |  |  |

    Note: startswith and endswith can also test strings: s1.startswith('Ind'): True
|  | India | INDIA | india | iNdIa | iNDIA |
| --- | --- | --- | --- | --- | --- |
| s1.istitle() |  |  |  |  |  |
| s1.isupper() |  |  |  |  |  |
| s1.islower() |  |  |  |  |  |
| s1.swapcase() |  |  |  |  |  |
| s1.title() |  |  |  |  |  |
|  | India | 346 |  |  |  |
| s1.endswith('a') |  |  |  |  |  |
| s1.endswith('6') |  |  |  |  |  |
| s1.endswith('b') |  |  |  |  |  |
| s1.startswith('I') |  |  |  |  |  |

Stripping leading or trailing spaces in a string
|  | s1.lstrip() | s1.rstrip() |
| --- | --- | --- |
| s1='   India    ' | 'India    ' | '  India' |

Miscallaneous
```python
s1='india'
s1.zfill(15)  |  ‘0000000000india’
s1='India'
for i,j  in enumerate(s1):
    print(i,j)  |  0 I
1 n
2 d
3 i
4 a
```

