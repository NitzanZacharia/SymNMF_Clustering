CC = gcc
CFLAGS = -ansi -Wall -Wextra -Werror -pedantic-errors -DBUILD_STANDALONE
LFLAGS = -lm
all: symnmf symnmfmodule
symnmf: symnmf.o
	$(CC) -o symnmf symnmf.o $(CFLAGS) $(LFLAGS)
symnmf.o: symnmf.c symnmf.h
	$(CC) -c symnmf.c $(CFLAGS)
symnmfmodule:
	python3	setup.py build_ext --inplace
py_sym: symnmfmodule
	python3 symnmf.py $(ARGS)
py_analysis: symnmfmodule
	python3 analysis.py $(ARGS)		
clean:
	rm -f symnmf.o symnmf
	rm -f symnmfmodule*.so		