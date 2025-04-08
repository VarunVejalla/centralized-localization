#include <stdio.h>

int f(int x) {
    return 5*x;
}

int foo(int x) {
    if (x > 0) 
        return f(x);
    else
        return x;
}

int main(void) {
    printf("%d\n", foo(5));
    return 0;
}
