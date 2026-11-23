# order_demo.py: the same term reduced in normal order and in applicative order.
# Terms are tuples, as in the deck's Model 3: ('var', n), ('lam', p, body), ('app', f, a).
def var(n):     return ('var', n)
def lam(p, b):  return ('lam', p, b)
def app(f, a):  return ('app', f, a)

def show(e):
    if e[0] == 'var':
        return e[1]
    if e[0] == 'lam':
        return "λ%s.%s" % (e[1], show(e[2]))
    f, a = show(e[1]), show(e[2])
    if e[1][0] == 'lam': f = "(%s)" % f        # a function that is a λ needs parentheses
    if e[2][0] != 'var': a = "(%s)" % a        # so does any argument that is not a name
    return "%s %s" % (f, a)

def free_vars(e):
    if e[0] == 'var': return {e[1]}
    if e[0] == 'lam': return free_vars(e[2]) - {e[1]}
    return free_vars(e[1]) | free_vars(e[2])

def subst(e, x, a):
    """e[x := a], renaming a binder when it would capture a free variable of a."""
    if e[0] == 'var':
        return a if e[1] == x else e
    if e[0] == 'app':
        return app(subst(e[1], x, a), subst(e[2], x, a))
    p, body = e[1], e[2]
    if p == x:
        return e                                   # x is rebound here: stop
    if p in free_vars(a):                          # capture risk: rename p first
        new = p + "'"
        while new in free_vars(a) | free_vars(body):
            new += "'"
        body, p = subst(body, p, var(new)), new
    return lam(p, subst(body, x, a))

def normal_step(e):
    """Leftmost-outermost redex first: the call is made before the argument is touched."""
    if e[0] == 'app' and e[1][0] == 'lam':
        return subst(e[1][2], e[1][1], e[2]), True
    if e[0] == 'app':
        f, done = normal_step(e[1])
        if done: return app(f, e[2]), True
        a, done = normal_step(e[2])
        if done: return app(e[1], a), True
    if e[0] == 'lam':
        b, done = normal_step(e[2])
        if done: return lam(e[1], b), True
    return e, False

def applicative_step(e):
    """Leftmost-innermost redex first: the argument is reduced before the call."""
    if e[0] == 'app':
        f, done = applicative_step(e[1])
        if done: return app(f, e[2]), True
        a, done = applicative_step(e[2])
        if done: return app(e[1], a), True
        if e[1][0] == 'lam':
            return subst(e[1][2], e[1][1], e[2]), True
    if e[0] == 'lam':
        b, done = applicative_step(e[2])
        if done: return lam(e[1], b), True
    return e, False

def run(name, step, e, limit=4):
    print("%s: %s" % (name, show(e)))
    for i in range(limit):
        e, done = step(e)
        if not done:
            print("  normal form after %d step(s): %s" % (i, show(e)))
            return
        print("  ->β %s" % show(e))
    print("  ... still going after %d steps" % limit)

omega_half = lam('x', app(var('x'), var('x')))      # λx.x x
OMEGA = app(omega_half, omega_half)                 # (λx.x x)(λx.x x)
K_y = lam('x', var('y'))                            # λx.y ignores its argument

run("Omega, normal order", normal_step, OMEGA, limit=2)
print()
run("(λx.y) Omega, normal order", normal_step, app(K_y, OMEGA))
print()
run("(λx.y) Omega, applicative order", applicative_step, app(K_y, OMEGA))
print()
# The worked example from the Class Notes: both orders agree here.
notes = app(app(lam('x', lam('y', app(var('x'), var('y')))), lam('z', var('z'))), var('w'))
run("Notes example, normal order", normal_step, notes)
run("Notes example, applicative order", applicative_step, notes)
print()
# The capture trap: (λx.λy.x) y must rename the inner y.
run("Capture trap, normal order", normal_step, app(lam('x', lam('y', var('x'))), var('y')))
