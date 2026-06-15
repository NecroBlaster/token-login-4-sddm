#!/usr/bin/env bash
set -euo pipefail
cmake -B build -S . \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_INSTALL_PREFIX=/usr \
  -DCMAKE_INSTALL_LIBEXECDIR=lib/sddm \
  -DBUILD_WITH_QT6=ON \
  -DBUILD_MAN_PAGES=OFF
cmake --build build -j"$(nproc)"
