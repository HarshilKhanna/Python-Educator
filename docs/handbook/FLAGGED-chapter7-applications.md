# ⚠️ FLAGGED: Chapter 7 — Some Applications

Chapter 7 contains applied examples (sorting, random sentences, chatbot, cryptography, text processing, word index) that draw on **both strings and lists**.

It does not map cleanly to a single curriculum-graph node.

**Suggested resolution options:**
- Attach to `05-strings.md` (majority of examples are string-based)
- Create a separate `08-applications.md` as an optional enrichment file
- Split examples across the relevant topic files manually

Awaiting your decision before merging.

---

Chapter 7: Some Applications
## 7.1 SORTING LISTS: Selection-Sort Algorithm
Given a list ‘a’ of  ‘n’ numbers, how do we sort them? Assume that we have a requirement to rearrange the numbers in the same list a.  In Python, we just need to say: a.sort(). However, it is a good logical exercise to do it from scratch. Here is our strategy:
- Find biggest element of the whole list (0 to n-1), swap that with 0th element.  Now we have biggest element in 0th position
- Find biggest element of the rest of the list (1 to n-1), swap that with 1st  element. Now we have second biggest element in 1st  position
- Find biggest element of the rest of the list (2 to n-1), swap that with 2nd   element. Now we have second biggest element in 2nd   position
- ….
    Actually, we only need to do this up to the last-but-one element, because if we sort up to that, the last position will automatically have the right value. Before we code this, try it out visually in the following table for list a=[23,45,55,88,27]. Indicate the exchanges with arrow marks.
|  | i=0 | i=0 | i=0 | i=1 | i=1 | i=1 | i=2 | i=2 | i=2 | i=3 | i=3 | i=3 | Already done ! | Already done ! | Already done ! |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 23 |  | 88 | 88 |  |  | 88 |  |  | 88 |  | 88 | 88 |  |  |
| 1 | 45 |  |  | 45 |  | 55 | 55 |  |  | 55 |  | 55 | 55 |  |  |
| 2 | 55 |  |  | 55 |  | 45 | 45 |  | 45 | 45 |  | 45 | 45 |  |  |
| 3 | 88 |  | 23 | 23 |  |  | 23 |  |  | 23 |  | 27 | 27 |  |  |
| 4 | 27 |  |  | 27 |  |  | 27 |  |  | 27 |  | 23 | 23 |  |  |

It would be a good learning process to act this out in the classroom with a set of numbers written in cards (with numbers written in it with width proportional to the number to give visual effect. Mangoes and apples with weights marked would also be good!)
    Here is the code. Remember that if length of list is n, indices run from 0 to n-1.  Therefore, last but one index is n-2.  Also recall that in Python, range (0, n) runs up to n-1 only. Therefore, in effect the for i and for j loop ranges are (0, n-2) and (i, n-1)
```python
a=[23,45,33,88, 27]
n=len(a)  |  Define list, find length
for i in range(0,n-1):
      big=a[i]  |  For each position of the list from 0 to n-2, start with assumption that the value in the first position is biggest (big)
for j in range(i+1,n):
          if a[j]>=big: 
             big=a[j]
             bigindex=j
      temp=a[i]
      a[i]=a[bigindex]
      a[bigindex]=temp  |  Consider elements in the rest of the list (i+1 to n-1), reset big if you find any bigger values. Also note the index of any such values as bigindex.
for j in range(i+1,n):
          if a[j]>=big: 
             big=a[j]
             bigindex=j
      temp=a[i]
      a[i]=a[bigindex]
      a[bigindex]=temp  |  When the loop finishes, mutually exchange (swap) the elements in ith position and the located biggest position
print(a)  |  Print the sorted list
```

Let us work out the intermediate steps for a=[23, 45, 55, 88, 27]
    i=0
```python
j=1  |  j=2  |  j=3  |  j=4
big=a[i]  |  if a[j]>=a[i]: 
  big=a[j]
  bigindex=j  |  if a[j]>=big: 
  big=a[j]
  bigindex=j  |  if a[j]>=big: 
  big=a[j]
  bigindex=j  |  if a[j]>=big: 
  big=a[j]
  bigindex=j
temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp
```

    i=1
```python
j=1  |  j=2  |  j=3  |  j=4
big=a[i]  |  if a[j]>=big: 
  big=a[j]
  bigindex=j  |  if a[j]>=big: 
  big=a[j]
  bigindex=j  |  if a[j]>=big: 
  big=a[j]
  bigindex=j
temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp
```

    i=2
```python
j=2  |  j=3  |  j=4
big=a[i]  |  if a[j]>=big: 
  big=a[j]
  bigindex=j  |  if a[j]>=big: 
  big=a[j]
  bigindex=j
temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp
```

    i=3
```python
j=3  |  j=4
big=a[i]  |  if a[j]>=big: 
  big=a[j]
  bigindex=j
temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp  |  temp=a[i]
a[i]=a[bigindex]
a[bigindex]=temp
```

    i=4
|  |  |  |  | j=4 |
| --- | --- | --- | --- | --- |
|  |  |  |  | big=a[i] |

## 7.2 Random Sentences
    Study the following program. It uses a random.choice() function to pick words randomly from three lists and keep creating grammatically correct statements. The program continues when you press enter in the input field. Type any character to quit. You can try to improve its performance in many ways, both programmatically and by adding more vocabulary. Do revisit the problem after you learn about functions and files.
    import random
    objects = ['grandmother', 'elephant', 'cat', 'chief minister', 'king', 'minister']
    subjects = ['fruit', 'candy', 'parotta', 'peanut', 'sugar']
    verbs = ['ate', 'saw', 'requested', 'will eat?', 'avoided']
    while True:
        print(random.choice(objects) + " " + random.choice(subjects) + " " + random.choice(verbs))
        x = input()
        if x != "":
            break
## 7.3 Chatbot
Study the following chat program (It is modelled after ELIZA program that surprised many, a few decades ago. Today programs like GPT3 make ELIZA trivial).  Try improving it in many ways (Picking more than one keyword, randomizing responses, avoiding repetitions and adding more likely keywords and their responses). Revisit the problem after learning functions and files.
    print('Hello, I am Eliza Kumari ! Chat with me, Type quit to stop')
    while True:
      x=input();  x=x.lower()
      if x=='quit': print('goodbye');break
      y=x.split()
      if len(y)==0:       print('please say something')
      elif y[-1]=='?':    print('Why do you ask that')
      elif 'hello' in y:  print('Hello, Good day')
      elif 'good morning' in y:  print('Hello, Good day')
      elif 'mother' in y: print('Tell me more about your mother')
      elif 'father' in y: print('Tell me more about your father')
      elif 'love' in y:   print('Love is an emotion not known to me')
      elif 'music' in y:  print('I love all genres of music')
      elif 'repeat' in y: print('repetition is not creative')
      elif 'friend' in y: print('Friend in need is a friend indeed')
      elif 'sun' in y:    print('sun is the source of all energy')
      elif 'age'  in y:   print('I am ageless !')
      elif 'colors' in y: print('what a colorful question !')
      elif 'joke' in y:   print('Nothing like a good laugh, I agree !')
      elif y[0]=='i' and y[1]=='feel':print('Why do you feel so?')
      else: print("Go on")
## 7.4 Simple Cryptography
    Here is a simple cryptography program to hide your message. (i) Read and explain the approach taken. (ii) Try changing chr((ord(c)+1)) to chr((ord(c)+2)). (iii) Write code to decrypt.
    message=input()
    secret=''
    for c in message:
      secret=secret+chr((ord(c)+1))
    print(secret)
| bioinformatics | cjpjogpsnbujdt |
| --- | --- |
| <Your name> |  |

## 7.5 Text processing
Which of the following is easier to read?. What makes your reading very involved? Can you develop a code to read a sentence and produce a text with _ at random positions? Try replacing 10% of letters.
| India is my country and all Indians are my brothers and sisters. I love my country and I am proud of its rich and varied heritage. I shall always strive to be worthy of it. I shall give respect to my parents, teachers and elders and treat everyone with courtesy. To my country and my people, I pledge my devotion. In their well being and prosperity alone, lies my happiness. | In_ia _s my coun_ry and all Indians are my br__hers and sist_rs. I love _y country an_ I am proud _f its _ich a_d varied h_ritage. I sh_l_ always st_ive to be worthy of it. I shall give resp_ct to my parents, t_achers and el_ers and tre_t everyone with courtesy. To my _ountry and my pe_ple, I p_edge my d_votion. In __eir well being and prosperity a_one, lies my hap_in_ss. |
| --- | --- |

Please note that strings are unmutable and therefore you must store result in another variable.
    import random
    text=input(); l=len(text)
    text1=''
    for i in range(l):
      x=random.choice([0,1,2,3,4,5,6,7,8,9])
      if x==1: text1=text1+'_'
      else:text1=text1+text[i]
    print(text1)
## 7.6 Word Index
Creating a word index from text. We will consider only a simple case to begin with. Let us assume that all words are to be indexed
| India is my country;
All Indians are my brothers and sisters.
I love my country, and I am proud of its rich and varied heritage. 
I shall always strive to be worthy of it.
I shall respect my parents, teachers and all elders and treat everyone with courtesy.
To my country and my people, 
I pledge my devotion.
In their well being and prosperity lies my happiness. |
| --- |
| Count of Words: All:2; India:1; I:5; Country:3 |

```python
Let us first code for indexing a sentance
You can modify the above code further. The dictionary can be edited to delete common words such as I, of, the, in, at, me, you, we etc. The words can be sorted alphabetically.
7.7 Concordancing: Let us try a different version of the above program: instead of count of occurances, you can store line numbers where the word occurs (concordancing).
You may revisit this program as your learning progresses and convert the dictionary to a text file suitable for appending to a book. 
7.8 Telephone Directory: Simple Telephone directory with add and search facility. We use a new feature: shelve. It is nothing but a dictionary, but stored after the program is run
```

