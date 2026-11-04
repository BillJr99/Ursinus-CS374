<Your name> and <your partner's name>   (or: <Your name>, worked alone)

# Part 1: AND and OR

AND = λp.λq. p q p

| p | q | Term after substitution | Which argument the first boolean picks | Result |
|---|---|---|---|---|
| TRUE | TRUE | TRUE TRUE TRUE | | |
| TRUE | FALSE | TRUE FALSE TRUE | first | FALSE |
| FALSE | TRUE | | | |
| FALSE | FALSE | | | |

OR = λp.λq. p p q

| p | q | Term after substitution | Which argument the first boolean picks | Result |
|---|---|---|---|---|
| TRUE | TRUE | | | |
| TRUE | FALSE | TRUE TRUE FALSE | first | TRUE |
| FALSE | TRUE | | | |
| FALSE | FALSE | | | |

# Part 2: XOR

XOR = λp.λq. p ___ ___

| p | q | Term after substitution | Result | Matches the truth table? |
|---|---|---|---|---|
| TRUE | TRUE | | | |
| TRUE | FALSE | | | |
| FALSE | TRUE | | | |
| FALSE | FALSE | | | |

# Part 3: SUCC and ADD

SUCC

1. In the SUCC ONE walkthrough, TWO has two copies of f.  Which one came from SUCC, and which came from ONE?  Point to the line that shows it.

2. What does `n f x` mean in words, and why does SUCC need it instead of just writing one more f?

3. Work out SUCC ZERO, one line at a time.  Which numeral do you get?

ADD

4. In the ADD ONE ONE walkthrough, what does the `x` of the outer ONE become at line 3, and why does that make the two counts add?

5. Work out ADD TWO ONE, one line at a time.  How many copies of f does the result have?

6. Would ADD ONE TWO give the same numeral?  Explain why, from what each numeral does to f.

# Part 4: Multiplication

Step 1.  Write the function that applies f a total of n times:  ______

Step 2.  Apply that function m times, starting from x, by filling in the blank:  m (______) x

Step 3.  Make it a numeral by wrapping it in the f and x binders:  λf.λx. ______

Step 4.  Make it a function of two numbers:  MULT = λm.λn. ______

Step 5.  Check MULT TWO TWO.  Using your formula, how many times does the outer TWO apply its function, and how many copies of f does each one contribute?  How many copies of f are in the result, and which number is that?
