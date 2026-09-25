/* fdprobe - what CPython's make_non_inheritable() and os.times() meet on
   ABIv11: ioctl(FIOCLEX), fcntl(F_GETFD/F_SETFD) on a file descriptor, and
   sysconf(_SC_CLK_TCK). */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <time.h>

int main(void)
{
    FILE *f = fopen("/Python/python", "rb");
    int fd = f ? fileno(f) : -1, r;
    printf("FD fileno=%d\n", fd);
#ifdef FIOCLEX
    errno = 0; r = ioctl(fd, FIOCLEX, NULL); printf("FD ioctl(FIOCLEX)=%d errno=%d\n", r, errno);
#else
    printf("FD FIOCLEX not defined\n");
#endif
    errno = 0; r = fcntl(fd, F_GETFD, 0); printf("FD fcntl(F_GETFD)=%d errno=%d\n", r, errno);
    errno = 0; r = fcntl(fd, F_SETFD, FD_CLOEXEC); printf("FD fcntl(F_SETFD,CLOEXEC)=%d errno=%d\n", r, errno);
    errno = 0; r = fcntl(fd, F_GETFD, 0); printf("FD fcntl(F_GETFD) after=%d errno=%d\n", r, errno);
    errno = 0; long t = sysconf(_SC_CLK_TCK); printf("FD sysconf(_SC_CLK_TCK)=%ld errno=%d CLOCKS_PER_SEC=%ld\n", t, errno, (long)CLOCKS_PER_SEC);
    printf("FD EINVAL=%d ENOSYS=%d ENOTTY=%d\nFD END\n", EINVAL, ENOSYS, ENOTTY);
    if (f) fclose(f);
    return 0;
}
