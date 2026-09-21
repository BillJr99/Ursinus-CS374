# Probes SEMANTICS.md section 1 (Truthiness).
#
# Nothing here is a trick; every line is legal syntax.  What each line PRINTS
# depends on decisions you made and wrote down: which values count as true in
# a condition, and what 'and'/'or' hand back when they short-circuit.
#
# Record the real output.  If your Type stage rejects this program before it
# runs, that rejection IS your answer for this section: you chose the stricter
# static rule, and SEMANTICS.md section 1 asks you to show the staged Type
# error and name what that strictness costs you.  If your checker allows any
# type in a condition, the loop runs and you document that instead.  Part 4
# spells out the choice; neither answer is the wrong one.

let n = 3;
while n {
    print n;
    n = n - 1;
}

print "" or "fallback";
print 0 or "zero decided";
print "value" and "second";
