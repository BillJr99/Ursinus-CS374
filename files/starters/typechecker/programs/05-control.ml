# Well typed.  if and while both require a Bool condition.
let count: Num = 0;
while count < 3 {
    count = count + 1;
}
if count == 3 {
    print "counted";
} else {
    print "miscounted";
}
