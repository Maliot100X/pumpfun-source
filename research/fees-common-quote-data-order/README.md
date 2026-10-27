# Reuse the common quote helper and recover the readonly-data order

The CreateDonation handler now calls the existing `common::curve_quote_mint` helper. Its private duplicate performed the same borrow and slice operations at different source locations. Reusing the common helper preserves those operations and recovers their original `common/mod.rs:33:48` and `33:56` locations. Removing the duplicate eliminates two extra 24-byte Source records. All **105 original Source records** now have matching counterparts, with none extra.

The unchanged function-order recipe and an additional qualified input-section order place all **265 relocatable readonly-data objects** at their original relative offsets. The section is 6,744 bytes in both artifacts. Its 3,712 nonpointer bytes and all 379 pointer-field positions agree. Each pointer target is checked: 268 refer to equal complete compiled readonly allocations, 108 refer to complete normalized function counterparts, and three preserve internal data offsets.

**Literal section and whole-ELF equality remain false.** The section starts at a different address, pointer values differ, and the pure readonly-data section still has different ordering and padding. Normalized function targets do not establish complete transitive or indirect behavior. Eight original function bodies remain unmatched.

The result preserves all **577/585 normalized functions, 198 raw-local matches, 430 unique structural pairs, 181 matched-caller Source observations and 3,870/3,877 equal direct-callee observations** from the [parent](../fees-qualified-linker-layout/README.md). It adds no complete function match. The global count of 105 Source records and the 181 observations at matched instruction sites are different measurements.

Two native builds produce identical complete stripped and symbol artifacts. Fresh independent execution passes **17,331 cases across 18 suites**, with matching application logs in all 6,413 cases that contain them. The original fixture ordering and multiplicities are preserved.

| Artifact | SHA-256 |
| --- | --- |
| Stripped candidate | `c594b69a08242c879ca4145a625dfd68ff8ccad72293fa5a7e01b68d8e914de3` |
| Symbol artifact | `7c2a073b1866a6358f40a044256c1ee28c4aea9bd28b8f593481e31ab66ffaef` |

The source delta is one call-site replacement and removal of the unused duplicate helper, with source-line count preserved. All 46 Rust/build inputs are bound to the parent plus the one override. The linker script contains object/archive and section names. No original instruction fragments, assembly, patched output bytes or appended padding are used.

The saved native controllers, commands, compiler logs and maps are retained. They use the parent Linux platform-tools v1.44 SDK, locked warm dependencies and ordinary stripping. The root Rust crate is recompiled separately in both winning builds; this is not a fresh dependency rebuild or a new SDK authentication claim.

```sh
python3 -B research/fees-common-quote-data-order/verify.py
python3 -B research/fees-common-quote-data-order/test_scope.py
python3 -B research/fees-common-quote-data-order/verify.py --materialize /absolute/new/directory
```

The verifier checks saved evidence without invoking a compiler, VM or network. Materialization recovers the exact source and linker inputs. Native reproduction uses the saved controller and launch arguments with the parent's SDK/cache setup; the recorded local mount paths must be preserved or adapted consistently. Neither the reconstructed helper name nor the explicit linker recipe is claimed to be the historical source or build recipe.
