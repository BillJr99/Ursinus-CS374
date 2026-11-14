# tiny.y

The smallest useful Bison grammar, from Part III of *Parsing, Part 2*: `+` and `*` over numbers, with `%left` settling precedence.

```bash
bison -d -v tiny.y
gcc tiny.tab.c -o tiny
printf '2 + 3 * 4\n' | ./tiny
```
