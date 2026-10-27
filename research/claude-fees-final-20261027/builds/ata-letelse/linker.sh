#!/bin/bash
set -e
printf '%s\n' "$@" > /work/c3/ata-letelse-link-args.txt
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
  if [[ "${args[i]}" == "-T" || "${args[i]}" == "--script" ]]; then
    cp "${args[i+1]}" /work/sdk-default-c3_ata-letelse.ld
    args[i+1]=/work/c3/ata-letelse/ordered.ld
  elif [[ "${args[i]}" == --script=* ]]; then
    cp "${args[i]#--script=}" /work/sdk-default-c3_ata-letelse.ld
    args[i]=--script=/work/c3/ata-letelse/ordered.ld
  fi
done
printf '%s\n' "${args[@]}" > /work/c3/ata-letelse-effective-args.txt
exec /work/sdk/rust/lib/rustlib/x86_64-unknown-linux-gnu/bin/rust-lld "${args[@]}"
