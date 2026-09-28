/* See abiv0compat.h. Behaviour as specified by C99 7.24.4.5 (wcschr,
   wcsrchr, wcstok) and 7.24.4.5.8 (wmemchr); the terminating null wide
   character counts as part of the string for wcschr and wcsrchr. */
#include "abiv0compat.h"

wchar_t *wcschr(const wchar_t *s, wchar_t c)
{
    for (;; s++) {
        if (*s == c)
            return (wchar_t *)s;
        if (*s == L'\0')
            return NULL;
    }
}

wchar_t *wcsrchr(const wchar_t *s, wchar_t c)
{
    const wchar_t *last = NULL;
    for (;; s++) {
        if (*s == c)
            last = s;
        if (*s == L'\0')
            return (wchar_t *)last;
    }
}

wchar_t *wmemchr(const wchar_t *s, wchar_t c, size_t n)
{
    for (; n > 0; n--, s++)
        if (*s == c)
            return (wchar_t *)s;
    return NULL;
}

static int in_set(wchar_t c, const wchar_t *set)
{
    for (; *set != L'\0'; set++)
        if (*set == c)
            return 1;
    return 0;
}

wchar_t *wcstok(wchar_t *restrict s, const wchar_t *restrict delim,
                wchar_t **restrict ptr)
{
    wchar_t *start;
    if (s == NULL)
        s = *ptr;
    while (*s != L'\0' && in_set(*s, delim))
        s++;
    if (*s == L'\0') {
        *ptr = s;
        return NULL;
    }
    start = s;
    while (*s != L'\0' && !in_set(*s, delim))
        s++;
    if (*s != L'\0')
        *s++ = L'\0';
    *ptr = s;
    return start;
}
