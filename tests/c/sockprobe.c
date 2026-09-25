/* sockprobe - what CPython's socket() setup meets on ABIv11 with AROSTCP:
   socket() with SOCK_CLOEXEC (the SDK defines it), then the close-on-exec
   calls _Py_set_inheritable() makes on a plain socket. Python's socket()
   failed with errno 86 (ENOTSUP). */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <proto/socket.h>
#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 0x10000000 /* as CPython sees it in sys/socket.h */
#endif

int main(void)
{
    int fd, r;
    errno = 0;
    fd = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    printf("SK socket(SOCK_CLOEXEC) fd=%d errno=%d\n", fd, errno);
    if (fd >= 0) CloseSocket(fd);
    errno = 0;
    fd = socket(AF_INET, SOCK_STREAM, 0);
    printf("SK socket() fd=%d errno=%d\n", fd, errno);
#ifdef FIOCLEX
    errno = 0; r = ioctl(fd, FIOCLEX, NULL);
    printf("SK ioctl(FIOCLEX)=%d errno=%d\n", r, errno);
#else
    printf("SK no FIOCLEX\n");
#endif
    errno = 0; r = fcntl(fd, F_GETFD);
    printf("SK fcntl(F_GETFD)=%d errno=%d\n", r, errno);
    { int on = 1; errno = 0; r = ioctl(fd, FIONBIO, &on); printf("SK ioctl(FIONBIO)=%d errno=%d\n", r, errno); }
    CloseSocket(fd);
    printf("SK-END\n");
    return 0;
}
