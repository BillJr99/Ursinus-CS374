# Ill typed: ordering comparisons require Num operands.  Equality on two Str
# values would be fine; '<' is not.
let first: Str = "apple";
let second: Str = "banana";
print first < second;
