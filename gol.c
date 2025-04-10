#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Usage: ./life <size> <steps> <seed>
int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <size> <steps> <seed>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int size = atoi(argv[1]);
    int steps = atoi(argv[2]);
    const char *seed = argv[3];

    int total_cells = size * size;

    if ((int)strlen(seed) != total_cells) {
        fprintf(stderr, "Error: Seed must be exactly %d characters long.\n", total_cells);
        return EXIT_FAILURE;
    }

    int *grid = malloc(sizeof(int) * total_cells);
    int *temp = malloc(sizeof(int) * total_cells);
    if (!grid || !temp) {
        fprintf(stderr, "Memory allocation failed.\n");
        return EXIT_FAILURE;
    }

    // Initialize grid from seed
    for (int i = 0; i < total_cells; i++) {
        if (seed[i] != '0' && seed[i] != '1') {
            fprintf(stderr, "Invalid seed character at position %d.\n", i);
            free(grid); free(temp);
            return EXIT_FAILURE;
        }
        grid[i] = seed[i] - '0';
    }

    // Game of Life simulation
    for (int step = 0; step < steps; step++) {
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                int idx = i * size + j;
                if (i == 0 || j == 0 || i == size - 1 || j == size - 1) {
                    temp[idx] = 0; // Border always dead
                    continue;
                }

                int n = 0;
                n += grid[(i - 1) * size + (j - 1)];
                n += grid[(i - 1) * size + j];
                n += grid[(i - 1) * size + (j + 1)];
                n += grid[i * size + (j - 1)];
                n += grid[i * size + (j + 1)];
                n += grid[(i + 1) * size + (j - 1)];
                n += grid[(i + 1) * size + j];
                n += grid[(i + 1) * size + (j + 1)];

                temp[idx] = (n == 3 || (n == 2 && grid[idx])) ? 1 : 0;
            }
        }
        memcpy(grid, temp, sizeof(int) * total_cells);
    }

    // Output final grid as binary string
    for (int i = 0; i < total_cells; i++) {
        putchar(grid[i] ? '1' : '0');
    }
    putchar('\n');

    free(grid);
    free(temp);
    return EXIT_SUCCESS;
}
