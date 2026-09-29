# Well typed.  Arithmetic over Num, with precedence and a unary minus.
# Note that '/' yields a fractional value; the checker calls that Num too,
# so this program prints -4.0 rather than -4.  That is a dynamic detail the
# static checker deliberately does not distinguish.
let a: Num = 2 + 3 * 4;
let b: Num = (2 + 3) * 4;
let c: Num = -a + b / 2;
print c;
