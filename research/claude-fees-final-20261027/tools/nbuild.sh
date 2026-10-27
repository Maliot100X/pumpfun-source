#!/bin/bash
# Native macOS diagnostic build (sbf lock only). usage: nbuild.sh SRC_DIR [extra rustc args...]
set -u
L=/private/tmp/claude-501/-Users-shawwalters-Documents-Codex-2026-10-24-pumpfun-source/bf960843-6806-451b-a211-62c8b228d301/scratchpad/lanes/fees-final
SP=/private/tmp/claude-501/-Users-shawwalters-Documents-Codex-2026-10-24-pumpfun-source/bf960843-6806-451b-a211-62c8b228d301/scratchpad
T=~/.cache/solana/v1.44/platform-tools
SRC=$(cd "$1" && pwd); shift
cd "$SRC"
export CARGO_HOME=$HOME/.cargo RUSTC=$T/rust/bin/rustc RUSTDOC=$T/rust/bin/rustdoc CC=$T/llvm/bin/clang AR=$T/llvm/bin/llvm-ar
export CARGO_TARGET_DIR=$L/target-mac CARGO_NET_OFFLINE=true RUSTFLAGS=-Zremap-cwd-prefix= PATH=$T/rust/bin:$T/llvm/bin:/usr/bin:/bin
exec python3 $SP/sbf_lock.py --slots 6 --name sbf -- $T/rust/bin/cargo rustc --verbose --manifest-path $SRC/programs/pump-fees/Cargo.toml --release --target sbpf-solana-solana --locked --offline --jobs ${JOBS:-1} --lib -- \
  --remap-path-prefix=$SRC/programs/pump-fees/src/../../../pump-fees-math/=pump-fees-math/ --remap-path-prefix=$SRC/pump-fees-math/=pump-fees-math/ \
  --remap-path-prefix=programs/pump-fees/src/../../../pump-fees-math/=pump-fees-math/ "$@"
