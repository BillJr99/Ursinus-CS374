# Probes SEMANTICS.md section 1 (Truthiness).
#
# Nothing here is a trick; every line is legal syntax.  What each line PRINTS
# depends on decisions you made and wrote down: which values count as true in
# a condition, and what 'and'/'or' hand back when they short-circuit.
#
# Record the real output.  If your Type stage rejects this program before it
# runs, that rejection IS your answer for this section: your static checker is
# stricter than your evaluator, which is a defensible design, and SEMANTICS.md
# should say so explicitly rather than leave the disagreement unmentioned.

let n = 3;
while n {
    print n;
    n = n - 1;
}

print "" or "fallback";
print 0 or "zero decided";
print "value" and "second";
