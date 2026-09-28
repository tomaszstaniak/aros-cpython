/* Declarations that the AROS i386 ABIv0 SDK (ABIv0_20250313-1) lacks and
   CPython and OpenSSL use. Included into every compilation with -include.

   1. Wide-character functions: its wchar.h marks them NOTIMPL and no link
      library defines them. Implemented in abiv0compat.c after their C99
      definitions.
   2. struct sockaddr_storage (RFC 2553): the AROSTCP <sys/socket.h> of this
      SDK predates it. The layout is the BSD one that the ABIv11 SDK has
      (sys/_sockaddr_storage.h), with ss_family as the u_char that this
      SDK's struct sockaddr uses for sa_family, so that both start alike. It
      is only a buffer large and aligned enough for any address. */
#ifndef ABIV0COMPAT_H
#define ABIV0COMPAT_H
/* Marks code in the CPython patches that applies to the ABIv0 line only
   (this header is included into every compilation of the i386 build and
   no other). */
#define _PY_AROS_ABIV0 1
#include <stddef.h>
#include <wchar.h>
wchar_t *wcschr(const wchar_t *s, wchar_t c);
wchar_t *wcsrchr(const wchar_t *s, wchar_t c);
wchar_t *wmemchr(const wchar_t *s, wchar_t c, size_t n);
wchar_t *wcstok(wchar_t *restrict s, const wchar_t *restrict delim,
                wchar_t **restrict ptr);

#ifndef _SS_MAXSIZE
#define _SS_MAXSIZE     128U
#define _SS_ALIGNSIZE   (sizeof(long long))
#define _SS_PAD1SIZE    (_SS_ALIGNSIZE - 2 * sizeof(unsigned char))
#define _SS_PAD2SIZE    (_SS_MAXSIZE - 2 * sizeof(unsigned char) - \
                         _SS_PAD1SIZE - _SS_ALIGNSIZE)
struct sockaddr_storage {
    unsigned char ss_len;
    unsigned char ss_family;
    char __ss_pad1[_SS_PAD1SIZE];
    long long __ss_align;
    char __ss_pad2[_SS_PAD2SIZE];
};
#endif
#endif
