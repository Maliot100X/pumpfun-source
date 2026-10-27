#!/bin/bash
set -e
printf '%s\n' "$@" > /work/c2/w580-link-args.txt
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
  if [[ "${args[i]}" == "-T" || "${args[i]}" == "--script" ]]; then
    cp "${args[i+1]}" /work/sdk-default-c2_w580.ld
    args[i+1]=/work/c2/w580/ordered.ld
  elif [[ "${args[i]}" == --script=* ]]; then
    cp "${args[i]#--script=}" /work/sdk-default-c2_w580.ld
    args[i]=--script=/work/c2/w580/ordered.ld
  fi
done
printf '%s\n' "${args[@]}" > /work/c2/w580-effective-args.txt
exec /work/sdk/rust/lib/rustlib/x86_64-unknown-linux-gnu/bin/rust-lld "${args[@]}"
