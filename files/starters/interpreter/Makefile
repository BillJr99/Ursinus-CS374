scheme: parser.tab.c lex.yy.c scheme.c scheme.h
	gcc -o scheme parser.tab.c lex.yy.c scheme.c

parser.tab.c: parser.y
	bison -d parser.y

lex.yy.c: scanner.l parser.tab.c
	flex scanner.l

clean:
	rm -f scheme parser.tab.c parser.tab.h lex.yy.c
