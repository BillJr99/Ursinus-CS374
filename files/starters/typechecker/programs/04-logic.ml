# Well typed.  and, or, and not all take Bool and yield Bool.
let ready: Bool = true;
let done: Bool = false;
let go: Bool = ready and not done;
let either: Bool = ready or done;
print go;
print either;
