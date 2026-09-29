# Probes SEMANTICS.md sections 3 (Scoping and shadowing) and 5 (Assignment
# vs. definition).
#
# The question this settles: does a bare assignment inside a block update the
# binding in the enclosing scope, or create a new one local to the block?  The
# two prints after the block are where the two answers diverge.  The final
# line assigns to a name that was never defined; it is last so everything
# above it still prints.  Record its exact error text and stage.

let x = 2;
let log = "outer=";
{
    let x = 51;
    print x;
    log = log + "shadowed";
}
print x;
print log;

never_defined = 1;
