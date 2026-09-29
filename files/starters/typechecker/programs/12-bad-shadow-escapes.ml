# Ill typed, and the counterpart to 06: the inner Str binding really is gone
# once the block closes, so assigning a Str to the outer Num x is an error.
let x: Num = 1;
{
    let x: Str = "inner";
    print x;
}
x = "outer now";
print x;
