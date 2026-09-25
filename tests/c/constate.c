/* constate - which startup step leaves the Shell's console window no longer
   interpreting escape sequences once the program has exited (ABIv11).
   Seen after python ran as a Shell command, not after "Run python". Each
   step is chosen by one letter so each can run in a fresh Shell. */
#include <fcntl.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <unistd.h>

static void handler(int sig) { (void)sig; }
static void *worker(void *arg) { return arg; }

int main(int argc, char **argv)
{
    const char *steps = argc > 1 ? argv[1] : "";
    int fd;

    for (; *steps; steps++) {
        switch (*steps) {
        case 't':
            for (fd = 0; fd < 3; fd++) printf("isatty(%d)=%d\n", fd, isatty(fd));
            break;
        case 'f':
            for (fd = 0; fd < 3; fd++) { struct stat st; printf("fstat(%d)=%d\n", fd, fstat(fd, &st)); }
            break;
        case 'l':
            for (fd = 0; fd < 3; fd++) printf("lseek(%d)=%ld\n", fd, (long)lseek(fd, 0, SEEK_CUR));
            break;
        case 'c':
            for (fd = 0; fd < 3; fd++) printf("F_GETFL(%d)=%d F_GETFD=%d\n", fd, fcntl(fd, F_GETFL), fcntl(fd, F_GETFD));
            break;
        case 'i': {
#ifdef TIOCGWINSZ
            struct winsize ws;
            for (fd = 0; fd < 3; fd++) printf("TIOCGWINSZ(%d)=%d\n", fd, ioctl(fd, TIOCGWINSZ, &ws));
#else
            printf("no TIOCGWINSZ\n");
#endif
            break;
        }
        case 's':
            printf("signal=%p\n", (void *)signal(SIGINT, handler));
            signal(SIGINT, SIG_DFL);
            break;
        case 'S':
            printf("signal kept=%p\n", (void *)signal(SIGINT, handler));
            break;
        case 'a': {
            struct sigaction sa, old;
            memset(&sa, 0, sizeof sa);
            sa.sa_handler = handler;
            sigemptyset(&sa.sa_mask);
            printf("sigaction=%d\n", sigaction(SIGINT, &sa, &old));
            sigaction(SIGINT, &old, NULL);
            break;
        }
        case 'p':
            printf("SIGPIPE ign=%p\n", (void *)signal(SIGPIPE, SIG_IGN));
            break;
        case 'u': {
            pthread_t th;
            printf("pthread_create=%d\n", pthread_create(&th, NULL, worker, NULL));
            pthread_join(th, NULL);
            break;
        }
        case 'e':
            printf("write2=%ld\n", (long)write(2, "e2\n", 3));
            break;
        case 'z':
            printf("write2-0=%ld write1-0=%ld\n", (long)write(2, "", 0), (long)write(1, "", 0));
            break;
        case 'E':
            fprintf(stderr, "stderr line\n");
            break;
        case 'V':
            printf("setvbuf(stdout)=%d\n", setvbuf(stdout, NULL, _IONBF, 0));
            break;
        case 'v':
            printf("setvbuf=%d\n", setvbuf(stderr, NULL, _IONBF, 0));
            break;
        case 'd': {
            int d = dup(2);
            printf("dup2=%d\n", d);
            if (d >= 0) close(d);
            break;
        }
        case 'r': {
            char b[1];
            int fl = fcntl(0, F_GETFL);
            printf("O_NONBLOCK set=%d\n", fcntl(0, F_SETFL, fl | O_NONBLOCK));
            printf("read=%ld\n", (long)read(0, b, 0));
            fcntl(0, F_SETFL, fl);
            break;
        }
        }
    }
#ifdef WITH_LIBS
    {
        extern const char *zlibVersion(void);
        extern const char *BZ2_bzlibVersion(void);
        extern const char *lzma_version_string(void);
        extern const char *sqlite3_libversion(void);
        extern char *gettext(const char *);
        extern void *libiconv_open(const char *, const char *);
        if (argc > 2)
            printf("libs %s %s %s %s %s %p\n", zlibVersion(), BZ2_bzlibVersion(),
                   lzma_version_string(), sqlite3_libversion(),
                   gettext("x"), libiconv_open("UTF-8", "ISO-8859-1"));
    }
#endif
    printf("CS done\n");
    return 0;
}
