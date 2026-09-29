# Ill typed: the classic.  '+' requires Num on both sides, and the error must
# be reported before anything runs.
let x: Num = 1 + true;
print x;
