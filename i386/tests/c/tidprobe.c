/* tidprobe.c - is pthread_self() constant for the whole life of a thread?
   Starts ROUNDS rounds of N threads; each compares pthread_self() at its
   first statement with pthread_self() after some work.
   Build: aros-v0-gcc -std=gnu11 tidprobe.c -o tidprobe -lpthread */
#include <pthread.h>
#include <stdio.h>

#define ROUNDS 50
#define N 8

struct rec { pthread_t a, b; };
static struct rec recs[N];

static void *work(void *p)
{
    struct rec *r = p;
    volatile unsigned long s = 0;
    r->a = pthread_self();
    for (unsigned long i = 0; i < 200000; i++)
        s += i;
    r->b = pthread_self();
    return NULL;
}

int main(void)
{
    int bad = 0, total = 0;
    for (int round = 0; round < ROUNDS; round++) {
        pthread_t t[N];
        for (int i = 0; i < N; i++)
            pthread_create(&t[i], NULL, work, &recs[i]);
        for (int i = 0; i < N; i++) {
            pthread_join(t[i], NULL);
            total++;
            if (recs[i].a != recs[i].b || recs[i].a != t[i]) {
                if (bad < 10)
                    printf("TID bad round=%d i=%d create=%lu start=%lu end=%lu\n", round, i,
                           (unsigned long)t[i], (unsigned long)recs[i].a,
                           (unsigned long)recs[i].b);
                bad++;
            }
        }
    }
    printf("TID threads %d mismatched %d\n", total, bad);
    return 0;
}
