/* tlsprobe - whether _Thread_local and pthread keys are per thread on
   ABIv11. CPython keeps the current thread state and the parking lot's
   per-thread wait data in _Thread_local variables; the thread pool test
   aborted with "PyMutex_Unlock: unlocking mutex that is not locked". */
#include <pthread.h>
#include <stdio.h>

static _Thread_local long tl = -1;
static pthread_key_t key;
#define N 6
static long seen[N], seenkey[N];
static void *addr[N];

static void *worker(void *arg)
{
    long i = (long)arg, k;
    tl = i * 100;
    pthread_setspecific(key, (void *)(i * 1000 + 1));
    addr[i] = (void *)&tl;
    for (k = 0; k < 200000; k++) {
        if (tl != i * 100) break;
        if (k % 1000 == 0) sched_yield();
    }
    seen[i] = tl;
    seenkey[i] = (long)pthread_getspecific(key);
    return NULL;
}

int main(void)
{
    pthread_t th[N];
    long i, bad = 0;
    pthread_key_create(&key, NULL);
    tl = 7;
    for (i = 0; i < N; i++) pthread_create(&th[i], NULL, worker, (void *)i);
    for (i = 0; i < N; i++) pthread_join(th[i], NULL);
    for (i = 0; i < N; i++) {
        int ok = seen[i] == i * 100 && seenkey[i] == i * 1000 + 1;
        bad += !ok;
        printf("TLS thread %ld tl=%ld key=%ld &tl=%p %s\n", i, seen[i], seenkey[i], addr[i], ok ? "ok" : "WRONG");
    }
    printf("TLS main tl=%ld (expect 7) &tl=%p\nTLS-END bad=%ld\n", tl, (void *)&tl, bad);
    return 0;
}
