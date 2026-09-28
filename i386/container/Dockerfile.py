# The ABIv0 build host plus zsh (the build scripts) and the host Python that
# a cross build of CPython 3.14.7 needs (--with-build-python): the same
# version, built from the same verified tarball.
FROM aros-abiv0-build:bookworm
RUN apt-get update && apt-get install -y --no-install-recommends zsh libssl-dev libffi-dev libbz2-dev liblzma-dev libsqlite3-dev libreadline-dev \
 && rm -rf /var/lib/apt/lists/*
COPY downloads/Python-3.14.7.tar.xz /tmp/
RUN echo "3b48dac8fb59f62eaa67ac83c1eb12bda1b7a08406dd286e252c11a66be27f81  /tmp/Python-3.14.7.tar.xz" | sha256sum -c - \
 && cd /tmp && tar -xJf Python-3.14.7.tar.xz && cd Python-3.14.7 \
 && ./configure --prefix=/opt/py314 --without-ensurepip -q && make -s -j2 && make -s install \
 && cd / && rm -rf /tmp/Python-3.14.7*
