# Ill typed: '==' requires both sides to have the same type.  There is no
# cross-type comparison, so this is an error no matter how strict you chose
# to be about truthiness elsewhere.
let count: Num = 3;
let label: Str = "3";
print count == label;
