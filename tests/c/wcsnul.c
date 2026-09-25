/* wcsnul - does the ABIv11 wcstombs() write the terminating NUL when there
   is room for it (C11 7.22.8.2)? CPython's _Py_wfopen() relies on it for
   the fopen() mode. */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    char b[10];
    size_t r;
    FILE *f;
    memset(b, 'X', sizeof b);
    r = wcstombs(b, L"rb", sizeof b);
    printf("WN r=%ld bytes=%02x %02x %02x %02x\n", (long)r,
           (unsigned char)b[0], (unsigned char)b[1], (unsigned char)b[2], (unsigned char)b[3]);
    errno = 0; f = fopen("/RAM/no-such", b); printf("WN fopen(mode from wcstombs) errno=%d\n", errno); if (f) fclose(f);
    errno = 0; f = fopen("/RAM/no-such", "rb"); printf("WN fopen(\"rb\") errno=%d\nWN END\n", errno); if (f) fclose(f);
    return 0;
}
