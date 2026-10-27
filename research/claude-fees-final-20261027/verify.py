#!/usr/bin/env python3
"""Static verifier for the fees-final w580 composition (no compilation, VM execution or network).

Checks:
  * the gzipped candidate ELFs decompress to the recorded SHA-256 values (stripped and symbols);
  * the repository normalizer (research/fees-composed-frontier188/window_map.py) gives 580 normalized and
    198 raw-local original windows, with exactly [249264] gained and nothing lost against the parent packet's
    published symbols ELF (research/fees-social-claim-v2-recovery);
  * the 21,079-byte .rodata equals the original and all 105 global Source records match;
  * source.patch is exactly the diff between the parent's materialized sources and the two overrides.

usage: python3 -B research/claude-fees-final-20261027/verify.py [--materialize /abs/new/dir]
--materialize writes the parent's 46 workspace inputs (via the parent verifier) plus this packet's two
overrides, i.e. the exact w580 source tree (vendor + linker recipe as materialized by the parent).
"""
import argparse, contextlib, difflib, gzip, hashlib, importlib.util, io, json, struct, sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'research/fees-social-claim-v2-recovery'
STRIPPED = 'ca7f3c9711fa3694c6d57399efc9a3d36ae6183757c29e20034c3f298eb0ac81'
SYMBOLS = '08c8b0d3b6e491886c63b283823072391201e8843496730b0f1b879a66e93125'
OVERRIDES = ['programs/pump-fees/src/instructions/withdraw.rs', 'programs/pump-fees/src/withdrawal.rs']
sha = lambda b: hashlib.sha256(b).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def windows_summary(w, original, image):
    o, c = w.windows(original), w.windows(image)
    sigs, raws = {r['signature'] for r in c}, {r['raw_sha256'] for r in c}
    norm = {r['address'] for r in o if r['signature'] in sigs}
    raw = {r['address'] for r in o if r['raw_sha256'] in raws}
    return norm, raw, len(w.compare(o, c)['unique_pairs'])


def verify():
    w = module('ffinal_windows', ROOT / 'research/fees-composed-frontier188/window_map.py')
    loc = module('ffinal_locations', ROOT / 'research/fees-sharing-slice-recovery/verify.py')
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    stripped = gzip.decompress((HERE / 'builds/w580/candidate.so.gz').read_bytes())
    symbols = gzip.decompress((HERE / 'builds/w580/symbols.so.gz').read_bytes())
    assert sha(stripped) == STRIPPED and sha(symbols) == SYMBOLS
    result = json.loads((HERE / 'builds/w580/result.json').read_text())
    assert result['candidate_sha256'] == STRIPPED and result['symbols_sha256'] == SYMBOLS and result['exit_code'] == 0
    repeat = json.loads((HERE / 'builds/w580-repeat.json').read_text())
    assert repeat['candidate_sha256'] == STRIPPED and repeat['symbols_sha256'] == SYMBOLS
    parent_symbols = gzip.decompress((PARENT / 'builds/candidate/symbols.so.gz').read_bytes())
    pn, pr, _ = windows_summary(w, original, parent_symbols)
    cn, cr, pairs = windows_summary(w, original, symbols)
    _, _, _ = windows_summary(w, original, stripped)  # stripped image parses with the same windows
    assert len(pn) == 579 and len(pr) == 198
    assert len(cn) == 580 and len(cr) == 198 and pairs == 433
    assert sorted(cn - pn) == [249264] and not (pn - cn) and cr == pr
    for section in ('.rodata',):
        assert w.m.section_data(original, section) == w.m.section_data(symbols, section)
    assert len(w.m.section_data(symbols, '.rodata')) == 21079
    counters = []
    for image in (original, symbols):
        c = Counter()
        for address, kind in w.m.relocations(image):
            if kind & 0xffffffff != 8:
                continue
            try:
                c[loc.location(w, image, address)] += 1
            except (AssertionError, ValueError, StopIteration, struct.error, UnicodeDecodeError):
                pass
        counters.append(c)
    assert counters[0] == counters[1] and sum(counters[0].values()) == 105
    runtime = json.loads((HERE / 'runtime/w580-summary.json').read_text())
    assert runtime['candidate_sha256'] == STRIPPED and runtime['case_count'] == 17331 and not runtime['mismatches']
    return dict(normalized=len(cn), raw_local=len(cr), unique_pairs=pairs, gained=sorted(cn - pn), lost=sorted(pn - cn),
                rodata_equal=True, source_records=105, runtime_cases=runtime['case_count'],
                candidate_sha256=STRIPPED, symbols_sha256=SYMBOLS, whole_elf_equal=False)


def materialize(dest):
    parent = module('ffinal_parent', PARENT / 'verify.py')
    assert not dest.exists()
    with contextlib.redirect_stdout(io.StringIO()):
        import subprocess
        subprocess.run([sys.executable, '-B', str(PARENT / 'verify.py'), '--materialize', str(dest)], check=True,
                       stdout=subprocess.DEVNULL)
    patch = []
    for name in OVERRIDES:
        old = (dest / name).read_text()
        new = (HERE / 'overrides' / name).read_text()
        patch.append((name, old, new))
        (dest / name).write_text(new)
    return patch


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--materialize', type=Path)
    a = ap.parse_args()
    out = verify()
    if a.materialize:
        changed = materialize(a.materialize.resolve())
        text = ''.join(''.join(difflib.unified_diff(o.splitlines(True), n.splitlines(True), fromfile='parent/' + name,
                                                    tofile='w580/' + name)) for name, o, n in changed)
        (a.materialize / 'w580-overrides.patch').write_text(text)
        out['materialized'] = str(a.materialize)
    print(json.dumps(out, indent=2))
