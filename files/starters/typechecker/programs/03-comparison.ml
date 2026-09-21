# Well typed.  Comparisons take Num and yield Bool; equality takes two of
# the same type and yields Bool.
let n: Num = 7;
let smaller: Bool = n < 10;
let same: Bool = n == 7;
let words: Bool = "yes" == "yes";
print smaller;
print same;
print words;
