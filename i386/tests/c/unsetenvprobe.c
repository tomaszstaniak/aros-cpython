/* unsetenvprobe.c - what unsetenv() returns on this C library, what errno
   it leaves, and whether the variable is actually gone afterwards.
   Build: aros-v0-gcc -std=gnu11 unsetenvprobe.c -o unsetenvprobe */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int r;
    printf("setenv   -> %d\n", setenv("UEP_X", "one", 1));
    printf("getenv   -> %s\n", getenv("UEP_X") ? getenv("UEP_X") : "(null)");
    errno = 0;
    r = unsetenv("UEP_X");
    printf("unsetenv -> %d errno %d\n", r, errno);
    printf("getenv   -> %s\n", getenv("UEP_X") ? getenv("UEP_X") : "(null)");
    errno = 0;
    r = unsetenv("UEP_NEVER_SET");
    printf("unsetenv(missing) -> %d errno %d\n", r, errno);
    return 0;
}
