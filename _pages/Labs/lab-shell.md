---
layout: assignment
permalink: /Labs/Shell
title: "CS374: Principles of Programming Languages - The Shell Terminal"


info:
  coursenum: CS374
  points: 100
  goals:
    - To execute commands in a shell terminal environment
    - To utilize the basic functionality exposed by a shell
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
  - shell
  
---

The purpose of this lab is to set up a terminal environment on your computer, to explore the `bash` shell, and preview the imperative programming language interface exposed by the shell.

If you are using a Linux operating system or MacOS, you already have a terminal program installed that, when you run it, will give you a `bash` shell environment.  Windows users have two options for installing a terminal environment that they can use, which we detail in the section below.  

## Windows Users: Installing a Terminal Environment

### Option 1: Installing Ubuntu Using the Windows Subsystem for Linux

Windows 10 includes the Windows Subsystem for Linux is an operating system layer that exposes the Linux POSIX interface to Windows, allowing us to run software that was compiled for Linux (including the shell).

[Follow these steps](https://docs.microsoft.com/en-us/windows/wsl/install-win10#manual-installation-steps) to install the Windows Subsystem for Linux, followed by Ubuntu.  This will install an Ubuntu shell that you can run from your Start Menu.

### Option 2: Installing Cygwin

Cygwin is an emulated Linux system layer that runs as a user application in your Windows operating system.  It will give you a program called Cygwin that you can run from your Start Menu.  [Download](https://www.cygwin.com/) and install Cygwin by following the steps in the installation menu.

## Exploring the Shell

Run Ubuntu, Cygwin, or your operating system's Terminal application.  You should see something like this:

![bash Shell]({{ site.baseurl }}/images/lab-shell/bash.png)

Your shell has a "working directory" associated with it.  This is the directory that you're exploring right now from the shell.  If you type:

`pwd`

this will "print the working directory" path to the screen for you.  You can change directories like this:

* `cd ..` (to go up one directory)
* `cd test` (to move into a directory called `test`, if you have one)
* `cd` (goes back to your user directory where you started, which is called your "home directory")
* `cd /home` (goes to a directory from the root of your tree called `home`, under which all the computer users' home directories are stored)

Try this:

```
cd /home
ls
```

and you should see your own user directory.  Type

`cd <type your user home directory name here>`

to return to your home directory.

### Editing Files
Personally, I use a program called `vim` to edit files.  There are tutorials available, like [this one](https://www.tutorialspoint.com/vim/vim_getting_familiar.htm) to learn all the features that vim provides.  There are other programs out there (for example, `emacs`).  You can install `vim` as follows on everthing **except** Cygwin:

`sudo apt install vim`

which tells your shell to install a program called `vim`, using the built-in package manager called `aptitude` or `apt`.  The `sudo` asks for the program to be run as `root`, or, in other words, in `administrator mode`.  If you try to run a command like `vim`, and the program is not installed, it will sometimes give you the `apt` command to run in order to install it first.

Cygwin does not have `sudo`, so you can check the boxes to instal `vim` and `nano` when you run the Cygwin installer instead.

If you'd like to learn `vim`, you can run the interactive tutorial `vimtutor` by typing `vimtutor` at your shell prompt and pressing return.  For now, we'll use an editor called `nano`.  Type:

`nano test`

which will edit a file called `test` in your working directory.  Type some text in the screen that appears, and then press `Control-O` on your keyboard to "output" or save the file.  It might ask you to confirm the filename, and you can hit Enter if this happens.  Press `Control-X` to quit back to the shell.

### Finding Your Way Around

This [tutorial](https://ubuntu.com/tutorials/command-line-for-beginners#1-overview) walks you through the Linux shell environment, including how to manipulate files and how to run programs.  The Linux subsystem provides a plethora of small **orthogonal** programs that do non-overlapping, very simple, specific, and specialized functions.  The goal of this course is not to learn them, but we will use them later as tools to write scripted programs in a programming language environment that the `bash` shell provides.

For now, create a file called `dobackup.sh` using `nano` or `vim`, and enter the following (then save the file, and quit your editor):

```
#!/bin/bash
TODAY=`date +%F`
SUCCESSMESSAGE="I have successfully backed up the directory!"
tar cvjpf ~/myhomedirectory-${TODAY}.tar.bz2 ${HOME}
echo ${SUCCESSMESSAGE}
```

Run this command to make the file "executable" (so that you can run it like a command): `chmod a+x dobackup.sh`

Finally, run the script: `./dobackup.sh`

This will create a file called `myhomedirectory-2021-01-17.tar.bz2` (or whatever today's date is for you!).  This is a compressed file, like a zip file, that contains all the contents of your home directory.  You can remove it like this:

`rm myhomedirectory-2021-01-17.tar.bz2` (substitute today's date for the date in the filename).

Notice that the script creates a variable called `TODAY`, set equal to today's date (by running a program and storing the output of the program in the variable!).  The tar command uses the `TODAY` variable, and another pre-defined variable called `HOME` that is set to your home directory's location.  You can reference a variable using this syntax: `${TODAY}`.

1. **What would have happened if you had written the `tar` command of your script as follows: `tar cvjpf ~/myhomedirectory-TODAY.tar.bz2 ${HOME}`?**
2. **What does the `echo` command do?**

In addition to answering the questions above, modify and submit a second script that creates a variable called `BACKUPLOCATION` containing the name of any directory you like, and modify the `tar` command of your script to backup that location instead of your home directory.

### Running Commands

Using `git`, we can clone a scheme interpreter if you do not already have one (i.e., by running `sudo apt install mit-scheme` on Ubuntu/Linux, or `brew install mit-scheme` on the mac).  Run the following command to install a `scheme` interpreter written in Python: `git clone https://github.com/vladimirfomene/scheme-interpreter.git`.  Later, when we write Scheme programs, we can save them in text files using `vim` or `nano` like you used in this lab, and then execute them by running `python scheme.py <your scheme file>`.
