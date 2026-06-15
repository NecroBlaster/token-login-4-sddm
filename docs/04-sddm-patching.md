# SDDM patching

The SDDM patch adds a new greeter action called `loginToken()`.

The new path asks `sddm-helper` to use the dedicated PAM service `sddm-token` instead of the normal `sddm` service.

## Files affected conceptually

The patch touches these areas of the SDDM source tree:

- common greeter/daemon message enum;
- greeter proxy;
- daemon socket server;
- display login handling;
- auth helper argument passing;
- helper application argument parsing;
- PAM backend service selection.

## Apply patch script

From inside the SDDM source tree:

```bash
python3 /path/to/sddm-ed25519-token-auth/sddm/scripts/apply-token-patch.py
```

The patch script is intentionally more tolerant than a static patch file because SDDM source formatting may vary between versions.

## Build example

```bash
cmake -B build -S . \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_INSTALL_PREFIX=/usr \
  -DCMAKE_INSTALL_LIBEXECDIR=lib/sddm \
  -DBUILD_WITH_QT6=ON \
  -DBUILD_MAN_PAGES=OFF

cmake --build build -j"$(nproc)"
```

## Exporting a static patch after testing

After applying the script and confirming that the build works:

```bash
git diff > ../sddm-login-token.patch
```

A static patch can then be reviewed and published for the exact SDDM version used.
