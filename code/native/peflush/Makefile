CC?=gcc
CFLAGS?=-O2 -fPIC -Wall -Wextra
LDFLAGS?=-shared
TARGET=libpeflush.so

all: $(TARGET)

$(TARGET): peflush.o
	$(CC) $(LDFLAGS) -o $@ $^

peflush.o: peflush.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o $(TARGET)
