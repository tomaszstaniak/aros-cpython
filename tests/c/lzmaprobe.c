/* lzmaprobe - which liblzma call the ABIv11 xz library refuses. Python's
   lzma.compress() fails with "Invalid or unsupported options"
   (LZMA_OPTIONS_ERROR) for FORMAT_XZ and FORMAT_ALONE. The calls below are
   the ones CPython's _lzma module makes, one at a time. */
#include <lzma.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    lzma_stream s = LZMA_STREAM_INIT;
    lzma_options_lzma o;
    lzma_filter f[2];
    int c, r;

    printf("LZ version %s (header %s)\n", lzma_version_string(), LZMA_VERSION_STRING);
    printf("LZ sizeof stream=%d options_lzma=%d filter=%d\n", (int)sizeof(lzma_stream), (int)sizeof(lzma_options_lzma), (int)sizeof(lzma_filter));
    for (c = 0; c <= 10; c += (c == 0 ? 1 : (c == 1 ? 3 : 6)))
        printf("LZ check_is_supported(%d)=%d\n", c, lzma_check_is_supported(c));
    printf("LZ filter_encoder_is_supported(LZMA2)=%d LZMA1=%d\n",
           lzma_filter_encoder_is_supported(LZMA_FILTER_LZMA2), lzma_filter_encoder_is_supported(LZMA_FILTER_LZMA1));
    r = lzma_easy_encoder(&s, 6, LZMA_CHECK_CRC64); printf("LZ easy_encoder(6,CRC64)=%d\n", r); lzma_end(&s); s = (lzma_stream)LZMA_STREAM_INIT;
    r = lzma_easy_encoder(&s, 6, LZMA_CHECK_CRC32); printf("LZ easy_encoder(6,CRC32)=%d\n", r); lzma_end(&s); s = (lzma_stream)LZMA_STREAM_INIT;
    r = lzma_easy_encoder(&s, 0, LZMA_CHECK_NONE);  printf("LZ easy_encoder(0,NONE)=%d\n", r); lzma_end(&s); s = (lzma_stream)LZMA_STREAM_INIT;
    memset(&o, 0, sizeof o);
    r = lzma_lzma_preset(&o, 6); printf("LZ lzma_preset(6)=%d dict=%u lc=%u lp=%u pb=%u mode=%d nice=%u mf=%d depth=%u\n", r, o.dict_size, o.lc, o.lp, o.pb, (int)o.mode, o.nice_len, (int)o.mf, o.depth);
    r = lzma_alone_encoder(&s, &o); printf("LZ alone_encoder=%d\n", r); lzma_end(&s); s = (lzma_stream)LZMA_STREAM_INIT;
    f[0].id = LZMA_FILTER_LZMA2; f[0].options = &o; f[1].id = LZMA_VLI_UNKNOWN; f[1].options = NULL;
    r = lzma_stream_encoder(&s, f, LZMA_CHECK_CRC64); printf("LZ stream_encoder(LZMA2)=%d\n", r); lzma_end(&s); s = (lzma_stream)LZMA_STREAM_INIT;
    r = lzma_raw_encoder(&s, f); printf("LZ raw_encoder(LZMA2)=%d\n", r); lzma_end(&s); s = (lzma_stream)LZMA_STREAM_INIT;
    r = lzma_stream_decoder(&s, UINT64_MAX, 0); printf("LZ stream_decoder=%d\n", r); lzma_end(&s); s = (lzma_stream)LZMA_STREAM_INIT;
    r = lzma_auto_decoder(&s, UINT64_MAX, 0); printf("LZ auto_decoder=%d\n", r); lzma_end(&s);
    printf("LZ-END\n");
    return 0;
}
