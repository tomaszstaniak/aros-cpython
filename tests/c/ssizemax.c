/* ssizemax - SSIZE_MAX against the size of ssize_t. The ABIv11 2026.09
   SDK defines SSIZE_MAX as _POSIX_SSIZE_MAX (32767), the POSIX minimum,
   although its ssize_t is a 64-bit long; CPython took PY_SSIZE_T_MAX from it
   and refused every allocation over 32 KiB. The check is at compile time;
   the program only prints the values. */
#include <limits.h>
#include <stdio.h>
#include <sys/types.h>

int main(void)
{
    printf("sizeof(ssize_t)=%d SSIZE_MAX=%ld LONG_MAX=%ld\n",
           (int)sizeof(ssize_t), (long)SSIZE_MAX, (long)LONG_MAX);
    return SSIZE_MAX == LONG_MAX ? 0 : 1;
}
