#!/bin/bash
set -e
printf '%s\n' "$@" > /work/next614/common-quote-data-layout-link-args.txt
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
  if [[ "${args[i]}" == "-T" || "${args[i]}" == "--script" ]]; then
    cp "${args[i+1]}" /work/next614/sdk-default.ld
    args[i+1]=/work/next614/common-quote-data-layout/ordered.ld
  elif [[ "${args[i]}" == --script=* ]]; then
    cp "${args[i]#--script=}" /work/next614/sdk-default.ld
    args[i]=--script=/work/next614/common-quote-data-layout/ordered.ld
  fi
done
printf '%s\n' "${args[@]}" > /work/next614/common-quote-data-layout-effective-args.txt
exec /work/sdk/rust/lib/rustlib/x86_64-unknown-linux-gnu/bin/rust-lld "${args[@]}"
