#!/bin/sh
# Download every input in inputs.sha256 into downloads/, check its SHA-256,
# and extract the ABIv0 SDK (the release ISO's Development directory) into
# sdk/. Needs curl, sha256sum, unzip and bsdtar (dnf install bsdtar).
set -e
cd "$(dirname "$0")"
mkdir -p downloads
while read -r file sum url; do
    [ -n "$file" ] || continue
    [ -f "downloads/$file" ] || curl -fL --retry 3 -o "downloads/$file" "$url"
    echo "$sum  downloads/$file" | sha256sum -c -
done < inputs.sha256
if [ ! -d sdk/Development ]; then
    rm -rf sdk-iso && mkdir -p sdk-iso sdk
    unzip -q downloads/AROS-20250313-1-pc-i386-boot-iso.zip -d sdk-iso
    bsdtar -xf sdk-iso/*/aros-pc-i386.iso -C sdk Development
    rm -rf sdk-iso
fi
echo "inputs ready"
