# tiny.y and tiny.l

The same grammar as `../tiny.y`, with its hand-written `yylex` moved into a Flex scanner, `tiny.l`. The grammar in `tiny.y` is unchanged. The [Flex and Bison tutorial](https://www.billmongan.com/Ursinus-CS374-Fall2026/Tutorials/FlexAndBison) walks through both versions and the no-`%left` experiment.

Run Bison first, because `tiny.l` includes the `tiny.tab.h` header that `bison -d` writes:

```bash
bison -d -v tiny.y
flex tiny.l
gcc -o tiny tiny.tab.c lex.yy.c
printf '2 + 3 * 4\n2*3+4\n' | ./tiny
```

Expected output:

```text
14
10
```

To see a conflict, delete the two `%left` lines from `tiny.y` and rebuild with the same commands. Bison warns about 4 shift/reduce conflicts, and `2*3+4` prints 14 instead of 10. Open `tiny.output` and look at States 8 and 9 to see why.
