/* tmprobe - what localtime(), localtime_r(), gmtime() and gmtime_r() leave in
   struct tm's tm_zone and tm_gmtoff on ABIv11. Python's time.localtime()
   crashed in strlen() on tm_zone. TypeOfMem() says whether the pointer is
   RAM at all before the string is read. */
#include <proto/exec.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static void show(const char *what, struct tm *p)
{
    const char *z = p ? p->tm_zone : NULL;
    ULONG type = z ? TypeOfMem((APTR)z) : 0;
    printf("TM %-12s ret=%p zone=%p typeofmem=%lu gmtoff=%ld isdst=%d",
           what, (void *)p, (void *)z, (unsigned long)type, p ? p->tm_gmtoff : 0L, p ? p->tm_isdst : -9);
    if (z && type)
        printf(" str=\"%.8s\"", z);
    printf("\n");
}

int main(void)
{
    time_t t = time(NULL);
    struct tm a, b;
    memset(&a, 0x55, sizeof a);
    memset(&b, 0x55, sizeof b);
    show("localtime_r", localtime_r(&t, &a));
    show("localtime", localtime(&t));
    show("gmtime_r", gmtime_r(&t, &b));
    show("gmtime", gmtime(&t));
    printf("TM sizeof(struct tm)=%d offsetof zone=%d\nTM-END\n", (int)sizeof(struct tm),
           (int)((char *)&a.tm_zone - (char *)&a));
    return 0;
}
