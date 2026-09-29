# Makefile for the mini-notation flex/bison example.
#
# Build:      make
# Try it:     echo "bd [sn sn] hh*2 ~" | ./mininote
#             make test        (runs every line of samples.txt)
# Clean:      make clean

CC     = cc
CFLAGS = -Wall -g
FLEX   = flex
BISON  = bison

OBJS = mininote.tab.o lex.yy.o ast.o eval.o main.o

mininote: $(OBJS)
	$(CC) $(CFLAGS) -o mininote $(OBJS)

mininote.tab.c mininote.tab.h: mininote.y
	$(BISON) -d mininote.y

lex.yy.c: mininote.l mininote.tab.h
	$(FLEX) mininote.l

mininote.tab.o: mininote.tab.c ast.h
	$(CC) $(CFLAGS) -c mininote.tab.c

lex.yy.o: lex.yy.c mininote.tab.h
	$(CC) $(CFLAGS) -c lex.yy.c

ast.o: ast.c ast.h
	$(CC) $(CFLAGS) -c ast.c

eval.o: eval.c ast.h
	$(CC) $(CFLAGS) -c eval.c

main.o: main.c ast.h
	$(CC) $(CFLAGS) -c main.c

test: mininote
	while IFS= read -r line; do \
	  echo "== $$line =="; \
	  echo "$$line" | ./mininote; \
	done < samples.txt

clean:
	rm -f mininote $(OBJS) mininote.tab.c mininote.tab.h lex.yy.c mininote.output

.PHONY: test clean
