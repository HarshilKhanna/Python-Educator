# Files, Pickles, Shelves & JSON

> Source: Chapter 9

**Curriculum graph node:** Files

---

Chapter 9: Python Files, Pickles, Shelves & JSON
## 9.1. Introduction
Lists, dictionaries, simple data type variables etc live only in the program. As soon as the program is closed, the data in lists, dictionaries and variables are lost. To ensure their persistence, you can save them in files or pickle or shelve them.
## 9.2. Opening & Reading Files
In Google Colab, files are saved in the file folders in Notebook facility itself. Let us create a file in any location in your device named “Row.txt”. Now, upload it in Colab File area (This will be available only during the session).  Now we write our first program to read the file Row.txt and print it.
    We open the file with the statement f=open('Row.txt', 'r'). f becomes the reference to the file in the program. f.readlines( ) reads the whole text in the file into a single list f1,  with each line of the file as a separate element. Note that each line ends with a “\n” character also.
```python
f=open('Row.txt', 'r') 
f1=f.readlines()
print(text)  |  ['Row row row your boat\n', 'Gently down the stream\n', 'Merrily merrily merrily merrily\n', 'Life is but a dream\n']
```

For more convenient handling, we can take each element of the list, strip off the \n character, split the words into separate elements and have each line as a separate list f2.
```python
f=open('Row.txt', 'r') 
f1=f.readlines();  f2=[]
for i in  f1:
  x=i.strip();x=x.split()
  f2.append(x)
print(f2)  |  [
 ['Row', 'row', 'row', 'your', 'boat'],    
 ['Gently', 'down', 'the', 'stream'],   
 ['Merrily', 'merrily', 'merrily', 'merrily'], 
 ['Life', 'is', 'but', 'a', 'dream']
]
```

    Note: f.readlines(5) reads 5 characters at a time, f.readlines() reads the whole file. Now you can start using the above code and do further things that you wish. Let us first make the code we developed in chapter on dictionaries and make the input file based.
Example-1: Creating a word index from text. We will consider only a simple case to begin with. Let us assume that all words are to be indexed
```python
Note: freq.get(j,0) means return 0 if not found. You can modify the above code further. The dictionary can be edited to delete common words such as I, of, the, in, at, me, you, we etc. The words can be sorted alphabetically.
Repetition from Chap 7.  Let us try a different version of the above program: instead of count of occurances, you can store line numbers where the word occurs (concordancing).
You may revisit this program as your learning progresses and convert the dictionary to a text file suitable for appending to a book

```

We can read any text file in the contents folder (If in root folder, pls mention path). The following example should be run after you upload Pledge.txt to Colab folder
    f=open('/Pledge.txt', 'r')
    print(f.read())
    f=open('/Pledge.txt', 'r')
    print(f.read())
