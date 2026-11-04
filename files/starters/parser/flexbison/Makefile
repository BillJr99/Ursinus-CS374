calc: calc.tab.c lex.yy.c
	gcc -o calc calc.tab.c lex.yy.c

calc.tab.c: calc.y
	bison -d calc.y

lex.yy.c: calc.l calc.tab.c
	flex calc.l

clean:
	rm -f calc calc.tab.c calc.tab.h lex.yy.c
