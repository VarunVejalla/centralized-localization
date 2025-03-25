#include <stdio.h>

int foo(int x) {
    if (x > 0) 
        return x * 2;
    else
        return x;
}

int main(void) {
    printf("%d\n", foo(5));
    return 0;
}
