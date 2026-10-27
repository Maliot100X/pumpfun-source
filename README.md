# pumpfun-source

Reconstructed Rust source for Pump.fun's Solana programs, with captured binaries,
reproducible builds and local differential tests.

**Progress as of 27 October 2026: all four core programs still differ from their
captured binaries. The selected Donation Relay reconstruction reproduces its complete meaningful
ELF and, through a separate loader deployment, its captured payload.**

## Current progress

[Current main-Pump parallel research snapshot](research/main-pump-parallel-checkpoint-20261027/README.md) preserves the verified intermediates and in-progress source beyond the maintained checkpoint.

**Main Pump: 70.8% of function windows matched; 50.0% of original text covered. Complete reconstruction remains unfinished.**

Reproduce the selected Pump ELF with its [archived Rust/linker recipe](repro/pump/main-contract-round34-20261027/reproduce.py).





Across the latest verified checkpoints, **2,879 / 3,338 inferred function windows
match (86.2%)**. Their matched windows cover **3,805,624 / 5,213,128 original text
bytes (73.0%)**. **One of five programs has complete meaningful-ELF identity**;
all four core contracts still differ from their captured binaries.

These percentages measure bounded binary-recovery progress, not a claim that
86.2% of the engineering work is finished. Complete reconstruction also requires
all remaining code, calls, data, relocations and build provenance.

| Latest verified checkpoint | Matched windows | Matched % | Raw-equal bodies | Normalized only | Unmatched | Whole ELF equal |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| [Pump Round34](repro/pump/main-contract-round34-20261027/README.md) | 733 / 1,035 | 70.8% | 137 | 596 | 302 | No |
| [PumpSwap / AMM](repro/pump_amm/quote-guard-recovery-20261027/README.md) | 643 / 785 | 81.9% | 148 | 495 | 142 | No |
| [Fees research](research/fees-ata-prefix-integration/README.md) | 581 / 585 | 99.3% | 200 | 381 | 4 | No |
| [Mayhem research](research/mayhem-initializer-current-recovery-20261027/README.md) | 430 / 441 | 97.5% | 100 | 330 | 11 | No |
| [Donation Relay](repro/donation-relay/canonical-exact-selection/README.md) | 492 / 492 | 100.0% | 492 | 0 | 0 | **Yes** |
| **Total** | **2,879 / 3,338** | **86.2%** | **1,077** | **1,802** | **459** | **1 / 5** |

“Windows” are inferred original machine-function ranges, including framework and
runtime helpers. Complete normalized matches mask specified call/address
operands; they do not prove the referenced callees or data match. Each original
window counts once. Raw equality means that local body is byte-equal, not that
the whole program is identical.

| Checkpoint | Text bytes in matched windows | Text covered | Unmatched text |
| --- | ---: | ---: | ---: |
| Pump Round34 | 895,416 / 1,792,208 | 50.0% | 896,792 |
| PumpSwap / AMM | 804,704 / 1,162,040 | 69.2% | 357,336 |
| Fees research | 756,600 / 799,648 | 94.6% | 43,048 |
| Mayhem research | 596,416 / 706,744 | 84.4% | 110,328 |
| Donation Relay | 752,488 / 752,488 | 100.0% | 0 |
| **Total** | **3,805,624 / 5,213,128** | **73.0%** | **1,407,504** |

Pump and AMM rows describe the verified maintained sources. Fees and Mayhem rows
are the latest qualified research frontiers, distinct from their maintained
selections in [repro/status.json](repro/status.json). The maintained Mayhem initializer now has its own [current-source build and
signed validation](repro/mayhem/initializer-current-20261027/README.md), separate
from the larger research frontier. Upstream Relay's canonical selection remains
the authority for its exact result.

Relay reproduces all **818,280 meaningful ELF bytes**. Its separate signed local
loader replay reproduces the **830,448-byte captured payload**, including 12,168
loader-allocated zero bytes. This does not establish the original historical
source or build recipe.

The latest [Metaplex research packet](research/claude-deps-metaplex-20261027/README.md)
matches all 707,448 bytes of the captured meaningful ELF and all 1,251 function
windows. A separate 86,543-byte zero extension matches the captured allocation;
it is not part of the stripped compiler artifact. This dependency result remains
unpromoted and does not change the core-program totals above. The [parallel-lane
review](research/claude-lanes-review-20261027/README.md) records the other packets
and their baseline/validation limits.
The [independent Utilize recovery](research/metaplex-utilize-exact-recovery/README.md)
adds the retained unstripped compiler output, empty-target build/dependency
receipts and two separately signed replays of that same 147-case corpus. Its
alternative source is an unpromoted compiler-context diagnostic.

## Behavior and remaining work

The [current-parent AMM event composition](research/amm-current-event-capture-20261027/README.md)
adds the complete 1,784-byte normalized sell-event body, retaining all prior
matches. Two builds agree; all 17,462 maintained cases and 26 focused event pairs
pass. Its 641-window research artifact remains separate from the selected
640-window source/ABI checkpoint; the parent's other supplemental matrices
were not rerun on this artifact.

Pump Round34 passes 10,468 full cases plus 7,536 focused executions, with 18,000
paired diagnostic-log cases. AMM passes 17,462 full cases plus the separate
account, fee, CPI, boundary and error-order matrices recorded in its checkpoint.
These corpora overlap and must not be summed as unique scenarios. Tests use
captured programs in local VMs; they do not establish current-chain acceptance.

The [current Mayhem initializer recovery](research/mayhem-initializer-current-recovery-20261027/README.md)
adds the complete 960-byte normalized initializer, including its five immediate
callees and four typed data references. Two current-framework builds agree;
6,636 fresh trade pairs and 69 initializer pairs pass, with ten successful
creations. Mayhem now has 430/441 normalized matches and eleven unmatched
windows. The [complete per-window inventory](research/mayhem-initializer-current-recovery-20261027/inventory.json)
separates raw-equal, normalized-only and unmatched bodies. A separate historical
macro composition reaches 430/141, kept outside the current row.

The [current-source Legacy Buy ownership composition](research/mayhem-current-ownership-composition-20261027/README.md)
preserves that 430/100 frontier and improves the partial handler to 13,784 bytes
against 13,848 original bytes. Its 50 immediate callee shapes and seven Source
records agree; two builds and 486 signed replay pairs pass. The full body remains
unmatched, so this adds no window to the table.

The earlier [Mayhem trade-origin and validator recovery](research/mayhem-trade-origins-validator/README.md)
adds the complete 1,296-byte normalized quote validator with its eight immediate
callees and fourteen typed data references checked. It reaches 429 normalized
and retains all 100 raw matches. Three partial trade handlers now reproduce 21
Source records and three CPI error origins. Two qualified builds agree, and 65
fresh case pairs pass. At that checkpoint twelve bodies, an allocator specialization and
whole-ELF identity remained unresolved; older runtime receipts keep their original
artifact bindings.

The [BuyV2 sizing follow-up](research/mayhem-sizing-panic-recovery/README.md)
preserves that frontier and restores the original typed sizing failure for all
three quote families. Its 6,636 fresh trade comparisons agree in functional
results and complete non-compute logs. The BuyV2 body remains unmatched.

A [same-IR compiler diagnostic](research/mayhem-host-llvm-comparison/README.md)
produces identical Mac and Linux LLVM objects for one earlier initializer
control. This narrows that investigation without adding a function match.

The [quote backend replay](research/mayhem-quote-backend-replay-20261027/README.md)
holds the saved Rust IR fixed: v1.54 reproduces the reference helper's masked
1,120-byte body, while v1.52 emits 1,288 bytes and v1.44 rejects the IR. The
original quote helper still differs in sixteen instruction slots; this
diagnostic adds no recovered function or runtime coverage.

An [allocator-context experiment](research/mayhem-allocator-context/README.md)
reproduces the missing reserve helper through a zeroed-allocation probe. It
identifies a compiler condition to recover through justified source; the probe
remains a diagnostic and the current reconstruction counts are unchanged.

The [historical parser follow-up](research/mayhem-allocator-parser-provenance/README.md)
reproduces that allocator form with an earlier Anchor event-parser template and
current event types. It is a mixed-source compiler experiment; original Mayhem
source remains unproven. The [earlier current-source composition](research/mayhem-control-work-20261027/README.md)
now preserves all 429 normalized matches and reaches 139 raw-local bodies,
with one additional matching allocator call. Repeated native builds agree;
6,636 fresh trade and 69 initializer comparisons pass. Its 39 additional raw
bodies cover 33,968 original text bytes. This remains a diagnostic, so the
established checkpoint counts in the table above are unchanged.

The [current-source historical macro composition](research/mayhem-historical-macro-current-20261027/README.md)
reproduces that same artifact with the complete historical Anchor macro and
historical event definition, removing the manually rendered parser. Two native
root builds agree; the upstream-gated control reproduces the parent. The target
runtime is still current Anchor, and no new original matches or target executions
are claimed.

The latest [Fees associated-token recovery](research/fees-ata-prefix-integration/README.md)
reconstructs the 739-instruction validator through scoped error handling. Fees
now has 581 normalized / 200 raw-local matches, preserving all 21,079 readonly
bytes and the earlier Withdraw, Social and program-ID recoveries. Two fresh
normal Cargo builds agree; all 17,331 fresh comparisons pass. Four functions,
absolute layout and complete ELF identity remain unresolved.

The [Fees residual-work archive](research/fees-residual-parallel-checkpoint-20261027/README.md)
preserves another 13,511 new or updated research files beyond the earlier
checkpoints, including the four parallel reconstruction lanes and compiler
diagnostics. These experiments retain their individual status and add no
accepted matches.

The latest [PumpSwap native-quote and execution recovery](repro/pump_amm/quote-guard-recovery-20261027/README.md) matches 643 windows and 148 raw bodies, corrects all 11 reserved-recipient differences, fixes Token-2022 native creator transfers, and restores observed claim/InitBoost and legacy operation boundaries. All 17,462 corpus cases and retained supplemental suites pass; 142 AMM windows remain.

Remaining priorities are the 302 Pump, 142 AMM, 4 Fees and 11 Mayhem unmatched
windows; deeper call/data/relocation identity; original build provenance; and
uncovered behavior such as authentic fixed-admin AMM `create_config` success.
The historical [150-handler audit](repro/reconstruction-audit-2026-10-26/handlers.md)
remains a separate bounded classification; newer function matches do not
retroactively certify every handler.

See [remaining work](docs/REMAINING-WORK.md),
[current reconstruction review](docs/RECONSTRUCTION-STATUS.md) and the
[research history](docs/BYTE-IDENTITY-PROGRESS.md) for evidence and limitations.

## Dependencies

| Dependency | Current byte result |
| --- | --- |
| SPL Token | 108,600 / 108,600 captured bytes reproduced (100%) |
| Token-2022 | 611,056 / 611,056 meaningful ELF bytes reproduced (100%); full 1,382,016-byte allocation requires 770,960 separately added zero bytes |
| Associated Token Account | 105,032 / 105,032 bytes reproduced (100%) by two non-historical research recipes; authentic recipe and selected promotion unresolved |
| Metaplex Token Metadata | Latest reviewed inventory: 1,509 differing positions—1,477 text, 30 source-coordinate and 2 relocation bytes; allocation padding assessed separately |

[Dependency evidence and selection status](repro/dependency-status.json).
Allocation-image equality is separate from unchanged compiler-output equality.

## Quick start

Use Python 3.12. Clone without line-ending conversion to preserve evidence hashes:

```sh
git clone --config core.autocrlf=false https://github.com/lalalune/pumpfun-source.git
cd pumpfun-source
python3 scripts/verify_evidence.py
python3 scripts/test_tooling.py
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/local_validation.py
```

Build and compare instructions: [tooling guide](docs/TOOLING.md) and
[scripts index](scripts/README.md). Source is in `programs/`, captured comparison
inputs in `evidence/`, and reproducibility records in `repro/` and `research/`.
See also [scope](docs/SCOPE.md), [security policy](SECURITY.md) and
[audit scope](audit/AUDIT.md).

## License

This repository's own code and documentation are released under the
[MIT License](LICENSE). Third-party and vendored materials (for example the
Apache-2.0 Solana SDK files under `programs/pump-amm/vendor`, imported research
and retained crate archives) keep their original licenses, and upstream Pump IDLs
and binaries remain with their original authors.
