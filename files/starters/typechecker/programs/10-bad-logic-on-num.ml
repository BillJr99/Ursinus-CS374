# Ill typed: 'and' requires Bool on both sides.  There is no truthiness in the
# static checker.
let flag: Bool = true;
print 1 and flag;
