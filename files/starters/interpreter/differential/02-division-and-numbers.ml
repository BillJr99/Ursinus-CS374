# Probes SEMANTICS.md sections 2 (Division by zero) and 6 (Type strictness).
#
# The first four lines ask whether your language keeps ints and floats apart.
# The last line is the error case, and it is last on purpose so everything
# above it still prints.  Record the exact error text and which pipeline stage
# reported it.

print 1 + 2.0;
print 4 / 2;
print 7 / 2;
print 1 == 1.0;

print 1 / 0;
