/* semprobe - the POSIX semaphore calls CPython's parking lot (PyMutex) uses,
   on ABIv11: sem_timedwait() with an absolute CLOCK_REALTIME deadline,
   sem_post() from another thread, and a stress run of hand-offs. The thread
   pool test aborted with "PyMutex_Unlock: unlocking mutex that is not
   locked". */
#include <errno.h>
#include <pthread.h>
#include <semaphore.h>
#include <stdio.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

static double now(void)
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1e6;
}

static int timedwait_ms(sem_t *s, long ms)
{
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += ms / 1000;
    ts.tv_nsec += (ms % 1000) * 1000000L;
    if (ts.tv_nsec >= 1000000000L) { ts.tv_sec++; ts.tv_nsec -= 1000000000L; }
    return sem_timedwait(s, &ts);
}

static sem_t a, b;
static volatile long handed;

static void *poster(void *arg)
{
    struct timespec d = {0, 100000000L};
    (void)arg;
    nanosleep(&d, NULL);
    sem_post(&a);
    return NULL;
}

static void *pingpong(void *arg)
{
    long i, n = (long)arg;
    for (i = 0; i < n; i++) {
        if (timedwait_ms(&a, 5000) != 0) { printf("SEM pingpong worker timeout at %ld errno=%d\n", i, errno); return NULL; }
        handed++;
        sem_post(&b);
    }
    return NULL;
}

int main(void)
{
    double t0;
    int r, v = -1;
    pthread_t th;
    long i, n = 2000, bad = 0;

    printf("SEM init=%d\n", sem_init(&a, 0, 0));
    sem_init(&b, 0, 0);

    t0 = now(); errno = 0; r = timedwait_ms(&a, 0);
    printf("SEM past-deadline r=%d errno=%d (%s) %.3fs\n", r, errno, strerror(errno), now() - t0);
    t0 = now(); errno = 0; r = timedwait_ms(&a, 300);
    printf("SEM 300ms-timeout r=%d errno=%d (%s) %.3fs\n", r, errno, strerror(errno), now() - t0);
    sem_getvalue(&a, &v);
    printf("SEM value after timeouts=%d\n", v);

    sem_post(&a);
    t0 = now(); r = sem_wait(&a);
    printf("SEM post-then-wait r=%d %.3fs\n", r, now() - t0);

    pthread_create(&th, NULL, poster, NULL);
    t0 = now(); errno = 0; r = timedwait_ms(&a, 3000);
    printf("SEM cross-thread r=%d errno=%d %.3fs (expect 0 after ~0.1s)\n", r, errno, now() - t0);
    pthread_join(th, NULL);
    sem_getvalue(&a, &v);
    printf("SEM value after cross-thread=%d\n", v);

    pthread_create(&th, NULL, pingpong, (void *)n);
    t0 = now();
    for (i = 0; i < n; i++) {
        sem_post(&a);
        if (timedwait_ms(&b, 5000) != 0) { bad++; printf("SEM pingpong main timeout at %ld errno=%d\n", i, errno); break; }
    }
    pthread_join(th, NULL);
    sem_getvalue(&a, &v);
    printf("SEM pingpong %ld/%ld handed=%ld bad=%ld value(a)=%d %.2fs\n", i, n, handed, bad, v, now() - t0);
    printf("SEM-END\n");
    return 0;
}
