# Well typed, and the interesting one: an inner declaration may legitimately
# give a name a different type, but only for the inner scope.  The outer x is
# still a Num after the block closes.
let x: Num = 1;
{
    let x: Str = "inner";
    print x;
}
print x + 1;
