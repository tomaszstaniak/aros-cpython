# 0.1.1 runtime and development package verification

Built with patches 0001-0023, GCC 10.5.0 and SDK-202609/Development.
Interpreter SHA-256: `570106329b02cc769d5374435fdcafbd728505634ca6e6ea1008ad5211c8bf5f`.
Runtime and dev use the same build/install tree; provenance validation passed.

Host: four package checks pass, including relocated CMake and pkg-config
consumers. The embedding executable has no undefined symbols (nm -u).
Embedding executable SHA-256: `216cc5fd8299090a1e6588c1e9c7355677eb0ecb480e492b877469ed2cfb32e1`.
Repeating packaging produced identical runtime TAR, ZIP, LHA and dev TAR/ZIP.
Runtime TAR/ZIP file contents match; archive hashes below identify the files.

Guest: exclusively reserved v11-2, AROS One 1.3 ABIv11, QEMU TCG, 2 GB,
1 MiB stack. os.uname reports 12.1, 41 Jan 30 2026; ENV:ABI is absent.
The interpreter reports abiv11 and its actual executable hash matches provenance.
The broad ABIv11 2026.09 acceptance remains historical 0.1.0 evidence.

- idprobe completed with the expected platform, SOABI and package tags.
- threads11: eight threads join, queue transfers 1000 items, pool and timer pass.
- thread_ident11: eight dumps with four live workers each (32 workers total).
  All assertions and joins complete; no faulthandler crash.
- Matching static embedding: host module, stdlib, codecs, SQLite, SSL version,
  initialization and finalization pass, return code 0.

Initial guest commands incorrectly used RAM: paths for Python script arguments
and PyConfig.home; these failed before executing tests. Successful logs here
use /RAM paths. A rapid multi-command interactive retry was also discarded.
The corrected embedding example and runtime were tested separately.
The final package adds acceptance text and the regression script after the
initial runtime archive was tested; interpreter and stdlib bytes are unchanged.

pthread_kill remains an SDK EINVAL stub, so delivery and identifier conversion
are not validated by that call. pthread_getcpuclockid is absent. GemRB, full
Lib/test, networking, Ctrl-C and physical hardware were not tested in this run.
The machine was stopped, logs collected and reservation released.

## Archives

- `aros-cpython-3.14.7-abiv11-0.1.1.lha`: `209afdc4106113ca70187fa426b0443f20f479917c54d868e731dfd43d04ee44`
- `aros-cpython-3.14.7-abiv11-0.1.1-dev.zip`: `2b62b59e5cdf07c3e6f585636417ef21ea7abf9a1ab0e3f8cbb58230b33949ff`
- `aros-cpython-3.14.7-abiv11-0.1.1.tar.gz`: `5036ed59e6b2d6e96319da56af8e1ac9baffd346b04f84b57765b9356a25e5ff`
- `aros-cpython-3.14.7-abiv11-0.1.1.zip`: `b43fd9e2da93ea1f2bda12b3274fbf0f1ec1dd353c82e6f3ed4e5426f676e7bd`
- `aros-cpython-3.14.7-abiv11-0.1.1-dev.tar.gz`: `4356d359b5352a10cb3612c98134a3e6460c45025e95f5f705b9e124ba27d543`
- `aros-cpython-3.14.7-abiv11-0.1.1.tar.gz.sha256`: `d62b279cc2cf8c54a00c6fa131ae65423d39eda60c045b8680dc15941e686306`
- `aros-cpython-3.14.7-abiv11-0.1.1.lha.sha256`: `3852bfae878ac1a2884aa4b70fb10ffc7ca8686f62544fb4d7f913775e25c17f`
- `aros-cpython-3.14.7-abiv11-0.1.1-dev.tar.gz.sha256`: `0d0107c61cf09c0320dc6f394b2a69242efaeebe4c66fcc20a113f4a335d1a4c`
- `aros-cpython-3.14.7-abiv11-0.1.1-dev.zip.sha256`: `0aca35d77d22a720ab93d37db0a8912cd2605b1e9bbcc3fe0ae46e70229d5370`
- `aros-cpython-3.14.7-abiv11-0.1.1.zip.sha256`: `9aeafa5d7f221db6f77ce9b920cf2217e5f7b16c77fa6934e7db59dbc3ae0a5b`
