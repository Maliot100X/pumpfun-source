#!/bin/bash
set -e
printf '%s\n' "$@" > /work/next612/common-quote-layout-link-args.txt
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
  if [[ "${args[i]}" == "-T" || "${args[i]}" == "--script" ]]; then
    cp "${args[i+1]}" /work/next612/sdk-default.ld
    args[i+1]=/work/next612/common-quote-layout/ordered.ld
  elif [[ "${args[i]}" == --script=* ]]; then
    cp "${args[i]#--script=}" /work/next612/sdk-default.ld
    args[i]=--script=/work/next612/common-quote-layout/ordered.ld
  fi
done
printf '%s\n' "${args[@]}" > /work/next612/common-quote-layout-effective-args.txt
exec /work/sdk/rust/lib/rustlib/x86_64-unknown-linux-gnu/bin/rust-lld "${args[@]}"
