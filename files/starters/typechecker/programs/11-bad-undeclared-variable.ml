# Ill typed: 'total' is used before any declaration binds it.  The checker
# reports this at the variable's own line and column, before the program runs.
let subtotal: Num = 10;
print subtotal + total;
