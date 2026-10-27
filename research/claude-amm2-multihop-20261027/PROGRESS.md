# multihop lane (amm2 workflow) — PROGRESS

Scope: `instructions/swap/multi_hop_swap.rs` windows. Base: main `repro/pump_amm/optional-context-recovery-20261027`
(candidate 97bd5553…, Linux 651 normalized / 148 raw / 134 unmatched). multi_hop_swap.rs is byte-identical in the 647
(event-decoder) and 651 checkpoints.

## Window map (original .text order = source DefIndex order; verified on the candidate)
| window | bytes | original function | Source/Location records | status on 651 |
|---|---|---|---|---|
| 0x3d8d0 | 752 | is_curve_hop | L 233:17, S 239 (6027) | line-only (candidate body r=1.0 at 250/256) |
| 0x3dbc0 | 9536 | #[program] multi_hop_swap with handler inlined | S 251(6084) 273(6002) 274(6001) 278(6044) 295(6086) 300(6084) 389; L 315:28 344:32 353:40 359:34 363:41 369:32 | code-level: candidate inlines the curve run (25,504 B) |
| 0x40100 | 520 | handler closure `ok_or_else(|| error!(NotEnoughRemainingAccounts))` | S 307 (6044) | code-level: candidate has no 6044 closure |
| 0x40308 | 1416 | program_for | S 414 (6027) | line-only (placement lane also claimed) |
| 0x40890 | 376 | accrue_hop_fees | – | matched |
| 0x40a08 | 15512 | amm_hop | S 469(6020 buy) 474(6021 sell) 642 643 712 | code-level (separate buy/sell disable checks, …) |
| 0x446a0 0x448a8 0x44cc8 0x44ed0 0x450d8 | 520 each | amm_hop Overflow closures | S 579 586 636 671 718 (6023) | line-only |
| 0x44ab0 | 536 | fee-gating closure defined INSIDE amm_hop between :586 and :636 (env = 8 refs) | – | code-level: original loads gates as i24 (ldxh+ldxb) and masks (and/neg) instead of branches |
| 0x452e0 | 1256 | vault_for_mint | L 772:20 773:10 775:10, S 777 (6084) | line-only (placement lane also claimed) |
| 0x457c8 | 376 | token_amount | – | matched |
| 0x45940 | 16912 | curve-run executor (non-inlined in original) | S 838(6027) 928(6023 direct) 929/936 (require_eq 6085); L 814:45 815:58 | code-level |
| 0xb92c8 | 520 | Overflow closure | S 941 (6023) | needs a closure at :941 (curve executor) |

## Phase A (in progress): item reorder + whitespace placement (gen/mk_a.py)
Layout: 1–99 unchanged (MultiHop derive stays at 68); helpers 100–231; is_curve_hop 232 (233:17, 239); execute 243–;
program_for err 414; amm_hop closures 579/586/636/671/718 (tail line-joined to end before 768); vault_for_mint 768 (772:20…777);
token_amount 782. Only token change: vault_for_mint local `account` -> `vault` (Location column 22 -> 20).
Expected gains: 0x3d8d0 0x40308 0x446a0 0x448a8 0x44cc8 0x44ed0 0x450d8 0x452e0.

## Negative controls / lessons
- (pending)
