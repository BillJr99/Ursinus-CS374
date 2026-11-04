CC = gcc
CFLAGS = -Wall -g

mylang: parser.tab.c lex.yy.c ast.c eval.c main.c ast.h
	$(CC) $(CFLAGS) -Wno-unused-function -o mylang parser.tab.c lex.yy.c ast.c eval.c main.c -lm

parser.tab.c parser.tab.h: parser.y
	bison -d parser.y

lex.yy.c: scanner.l parser.tab.h
	flex scanner.l

test: mylang
	@failed=0; total=0; for f in programs/*.ml; do \
	  total=$$((total+1)); \
	  if ./mylang $$f | cmp -s - $${f%.ml}.expected; then echo "PASS $$(basename $$f)"; \
	  else failed=$$((failed+1)); echo "FAIL $$(basename $$f)"; fi; \
	done; echo "$$((total-failed)) passed, $$failed failed"

clean:
	rm -f mylang parser.tab.c parser.tab.h lex.yy.c
