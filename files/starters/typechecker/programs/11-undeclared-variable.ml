# The checker accepts this program: 'total' has no declaration, so its type is
# unknown and the checker leaves it to the Run stage, which reports the undefined name.
let subtotal: Num = 10;
print subtotal + total;
