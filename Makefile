SRCS := $(wildcard *.c)
BIN := bin

all: $(SRCS)
	mkdir -p $(BIN)
	for src in $(SRCS); do \
		gcc -O0 -fdump-tree-all-graph -c $$src -o /dev/null; \
		mv $$src.* $(BIN)/ 2>/dev/null || true; \
	done

clean:
	rm -rf $(BIN)
