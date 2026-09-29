# Probes SEMANTICS.md sections 6 (Type strictness) and 7 (String
# concatenation).
#
# The first two lines ask whether '+' is overloaded for strings.  The last
# line asks what happens when the two sides disagree; it is last so the legal
# lines print first.  Record the error's exact text and which stage caught it:
# a language with a strong static checker may reject this before it runs,
# while a purely dynamic one reports it at evaluation.

let greeting = "hello";
print greeting + " world";

print greeting + 1;
