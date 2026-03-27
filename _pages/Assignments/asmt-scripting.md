---
layout: assignment
permalink: /Assignments/Scripting
title: "CS374: Principles of Programming Languages - Scripting Languages"


info:
  coursenum: CS374
  points: 100
  goals:
    - To explore shell scripting languages using bash
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
  
tags:
  - scripting
  
---

The purpose of this assignment is to write a shell script to help automate a task, and to explore the language by which your shell exposes its functionality to you.  Shell scripting allows you to write code, including variables, conditionals, and interation, that executes shell commands.  Although your shell primarily manages the running processes on your computer, it exposes that functionality with a Turing complete language!

## Part 1: Creating an MD5 Dictionary
Open your shell and execute the following command:

`find . -type 'f' -exec md5sum {} \; 2>/dev/null`

This command searches for all files (per the `-type 'f'` clause) under your current working directory and recursively into all subdirectories.  It also executes a command on each file: specifically, it computes an MD5 hash on the contents of each file.  The `2>/dev/null` causes all error messages (like file permissions failures) to be suppressed, so you'll only get meaningful output for the files that you can read.  The computed MD5 hash changes if the contents of the file changes.  The format of each line is:

```
<md5 hash><space><space><file path>\n
```

Use the `cut` or `awk` command to read the hash and the file path into two separate `bash` variables.  Write those to a file in the following format:

```
<file path><space><md5 hash>\n
```

You can append two commands together using the pipe character: for example, the command below lists all files in your directory, and pipes the output to the sort command, which sorts the output alphabetically:

```
ls | sort
```

You can also append `> output` to the end of a command to write its output to a file called `output` (or any file name you choose).  Let's output to a file called `md5dict.txt`.  To append to an existing file, you can use `>> output` instead.

To use the `cut` command, you can do the following:

`echo test,tube | cut -f2 -d','`

which obtains the second field (`tube`) from the line of text, using the delimiter `,`.  

### Summary

In short, you can generate your database of file hashes within your directory by executing this command first in your script:

```
find . -type 'f' -exec md5sum {} \; >db.txt 2>/dev/null
```

**On Mac, the tool is called md5, and the output format is slightly different (the file name is the second token, and the path is the fourth token).**

Then, you can convert your data file to be comma delimited to make parsing easier by looping over each line in this file:

```
# you may wish to remove md5dict.txt before running this script
cat db.txt | while IFS= read -r line
do
  # set a variable to the first cut field (the hash)
  # set a variable to the second cut field (the filename)
  # echo the filename, a comma, and the hash, and append that to a new md5dict.txt file
done
```

Arrange your command(s) to compute the MD5 hash into a shell script and test it.  Write the following line as the first line of your script file, so that your computer knows it is a `bash` script:

```
#!/bin/bash
```

and, before you execute it, run this to make the file executable (I'll use the filename `myscript.sh` as an example, but you can call your file whatever you'd like!):

```
chmod a+x myscript.sh
./myscript.sh
```

## Part 2: Checking for Changes

In your shell script (or in a new shell script), before you create the MD5 dictionary file from Part 1, check if the `md5dict.txt` file already exists.  If it does, read each entry in the file and the MD5 hash into two `bash` variables.  Use the file path variable, and if the file exists, compute `md5sum` on the file, storing the current MD5 hash into another variable.  If the MD5 does not match the one you read in your original dictionary, print out that the file has changed to the screen.  If the file no longer exists, print out a message indicating that as well.  If the file exists and the MD5 hashes match, print nothing (this way, you have a concise log of all the files that have changed in your directory!).  

Finally, we need to see if any new files were created.  Use a `find` command to find all files in your current working directory.  For each one, `grep` for it in your `md5dict.txt` file.  If no match is found, print out hat you have identified a new file in your working directory.

To find all files in your directory and loop over each one, you can use this snippet:

```
find . -print0 -type 'f' | while IFS= read -r -d '' line; do 
    # Your code here, which can use the ${line} variable
done
```

Once you are done, you can proceed with your code from Part 1, so that you re-generate a new `md5dict.txt` file.  Alternatively, you can organize Part 1 and Part 2 into two separate shell scripts, if you prefer.
