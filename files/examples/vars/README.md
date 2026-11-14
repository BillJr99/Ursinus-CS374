# vars.y

Variables as rules and actions, from Model 3 of *Calculator with Variables*: `let` stores a value, a letter reads one, and the symbol table is 26 slots.

```bash
bison -d vars.y
gcc vars.tab.c -o vars
printf 'let x = 3\nlet y = x * 2 + 1\nprint y\nlet x = x + 1\nprint x * y\n' | ./vars
```
