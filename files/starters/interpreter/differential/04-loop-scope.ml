# Probes SEMANTICS.md section 4 (Loop-variable persistence).
#
# Does a 'let' in a loop body get a fresh binding each iteration, and does it
# survive the loop?  The first print tells you about the loop variable, the
# second about the body's binding.  If the second line is an error in your
# language, record the error: that is the decision, not a bug.

let i = 0;
while i < 3 {
    let inner = i * 10;
    i = i + 1;
}
print i;
print inner;
