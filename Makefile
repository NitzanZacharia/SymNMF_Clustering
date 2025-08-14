CC = gcc
CFLAGS = -ansi -Wall -Wextra -Werror -pedantic-errors -DBUILD_STANDALONE
LFLAGS = -lm
my_app: symnmf.o symnmfmodule.o symnmf.h
	$(CC) -o my_app symnmf.o symnmfmodule.o $(CFLAGS) $(LFLAGS)

symnmf.o: symnmf.c
	$(CC) -c symnmf.c $(CFLAGS)

symnmfmodule.o: symnmfmodule.c
	$(CC) -c symnmf.c $(CFLAGS)
		
clean:
	rm -f *o
	rm my_app		