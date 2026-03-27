---
layout: assignment
permalink: /Assignments/Regex
title: "CS374: Principles of Programming Languages - Regular Expressions"


info:
  coursenum: CS374
  points: 100
  goals:
    - To match text patterns using Regular Expressions
  rubric:
    - weight: 60
      description: Algorithm Implementation
      preemerging: The algorithm fails on the test inputs due to major issues, or the program fails to compile and/or run
      beginning: The algorithm fails on the test inputs due to one or more minor issues
      progressing: The algorithm is implemented to solve the problem correctly according to given test inputs, but would fail if executed in a general case due to a minor issue or omission in the algorithm design or implementation
      proficient: A reasonable algorithm is implemented to solve the problem which correctly solves the problem according to the given test inputs, and would be reasonably expected to solve the problem in the general case
    - weight: 30
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice, and/or the code departs significantly from the style guide
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program, and/or there are minor departures from the style guide
      progressing: Code documentation is present that re-states the explicit code definitions, and/or code is written that mostly adheres to the style guide
      proficient: Code is documented at non-trivial points in a manner that enhances the readability of the program, and code is written according to the style guide
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways (for example, because it is lacking a readme writeup)
      progressing: The program is submitted according to the directions with a minor omission or correction needed, and with at least superficial responses to the bolded questions throughout
      proficient: The program is submitted according to the directions, including a readme writeup describing the solution, and thoughtful answers to the bolded questions throughout    
  readings:
    - rtitle: "Regex Activity"
      rlink: "../Activities/Regex"  
    - rtitle: "Regex Reference"
      rlink: "https://www.w3schools.com/python/python_regex.asp"
    - rtitle: "Python Regular Expressions Interface"
      rlink: "https://docs.python.org/3/library/re.html"
            
tags:
  - regex
  
---

The purpose of this assignment is to practice matching patterns in texts using regular expressions.  

## Part 1: Warmup

The Python language provides a regular expression processing library called `re` that you can use to match and replace text in a `String`.  Here's how it works:

```python
import re

file = open("somefile.txt")
data = file.read()

offset = 0
result = []

# This will return a Match object for the first semicolon in the string
match = re.search(r";", data)

# This will print a list of the starting index (from 0) and the ending index (non-inclusive) of the match
print(match.span())

result.append(match.span()) # keep track of all the matching positions, relative to the prior match position

nextIndex = match.span()
nextIndex = nextIndex[1]

offset = offset + nextIndex # keep track of the absolute position of the most recent match

# This will search the rest of the string for the next instance
# ... and return None if no match is found
match = re.search(r";", data[offset:])
```

Create a text file called `somefile.txt` (or something else, and you can modify your code to use this file instead!).  Modify the code example above to search for semicolons in your file, in a loop, printing out the span of all found matches until the `nextIndex` exceeds the length of the file data, or until no match is found.  

You will want to play around with the functions: print out their results, figure out how they work.  Check out the `re` library documentation.  Don't expect to understand everything at first glance - I'm asking you to explore the library as part of this exercise!  In particular, note that `re.search` returns a `match` whose `span` is a tuple containing two items: the index of the beginning of the match, and the index of the end of the match.  You can generate a substring using `data[match.span()[0], match.span()[1]` to view the matching text (although I suggest making variables to represent the span, the starting index, and the ending index, to improve the readability of your code!).  However, to ensure you don't find the same match again, you will likely substring your data prior to looping using `data[offset:]`, where `offset` is the index of the end of the match.  The next time you loop, though, you'll be given offsets that are relative to this new position!  You'll want to add `offset` to the beginning and end of your `span` tuple values in order to obtain absolute offsets.  Alternatively, you can leave these matches as relative offsets, and when you print the substrings themselves, add the ending index of the prior match span to the current ones to obtain a running total.

### Modularizing this Function into a Regular Expression Processor

Put this code into a function that returns an array of match spans for a given regular expression string and text data:

```python
import re

def regexmatch(pattern, file):
    # You can append your match spans to this list
    result = []
    
    # TODO: your code here
    
    return result
```

Don't forget to replace `r";"` with the variable parameter `pattern` when you merge into the function.  You will have effectively created `grep` by doing this!

## Part 2: Regular Expressions

Write a new program based on your warmup that computes the following regular expressions, and prints a list of all the spans matching each expression.  For each span that you find, print the substring (keep in mind that the ending index is non-inclusive, so your substring can omit the very last character index in each returned match).

1. Each substring **ending with** a semicolon: match the whole substring.  Hint: here is the regular expression: `r"\w*;"`.  The `r` character before the `String` indicates to Python that this is a "raw" `String`, so no escape characters are needed.  Alternatively, you could use this: `"\\w*;"`.
2. All characters inside a set of parentheses.  You can use `\(` and `\)` to represent an opening and closing parenthesis in your regular expression `String` (don't forget to mark the `String` as a raw `String` so you don't have to also escape the backslash character!  You may use `\w` again to represent a character to match inside the parenthesis.
3. Valid variable names.  A valid variable name can be formed in one of two ways: first, a lowercase letter (not a number), followed by zero or more upper case letters, lower case letters, or numbers; alternatively, a variable name may be an upper case letter (not a number) followed by zero or more upper case letters or numbers (no lower case letters).  So these are valid: `aVariableName1`, `piTimesD`, `FALSE`, but these are not: `2piR`, `AnotherVariable`.  
3. All phone numbers.  Phone numbers contain the following format: `1-215-555-1212`; however, the leading "1-" is optional, and the dashes may be either dashes or spaces.
4. All lines beginning with the word `DEPOSIT:`.

## Part 3: Limitations of Regular Expressions

In your README, discuss why it would be impossible to write a single regular expression to ensure that all opening parentheses are properly nested inside other parentheses, and balanced.  In other words, why is it difficult to write a regular expression that matches these `String`s: `(())`, `(()()(()))`, but not these: `((()()`, `())`?  Note: do not attempt to write this regular expression, beyond identifying that it cannot be done!

## Part 4: Replacements

The `re.sub(pattern, replacement, data)` will look for the regular expression defined by `pattern` in the text specified by `data`, and replace each instance with the string `replacement`.  Write a program or function to replace all instances of `CS374` or `CS 374` with `Principles of Programming Languages`.
