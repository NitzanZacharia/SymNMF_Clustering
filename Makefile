CC = gcc
CFLAGS = -ansi -Wall -Wextra -Werror -pedantic-errors -DBUILD_STANDALONE
LFLAGS = -lm
# P_CFLAGS = $(shell python3-config --includes)
# P_LFLAGS = $(shell python3-config --ldflags)
my_app: symnmf.o symnmf.h
	$(CC) -o symnmf symnmf.o $(LFLAGS)

symnmf.o: symnmf.c symnmf.h
	$(CC) -c symnmf.c $(CFLAGS)

# symnmfmodule.o: symnmfmodule.c symnmf.h
# 	$(CC) -c symnmfmodule.c $(CFLAGS) $(P_CFLAGS)
		
clean:
	rm -f *.o symnmf *.so