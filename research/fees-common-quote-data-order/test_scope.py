"""Mutation checks for the actual source and data-target validation boundaries."""
from pathlib import Path
from functools import lru_cache
import importlib.util
import struct
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('quote_data_tests', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Scope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = v.module('quote_data_test_windows', v.ROOT / 'research/fees-composed-frontier188/window_map.py')
        cls.w.m.elf_layout = lru_cache(maxsize=8)(cls.w.m.elf_layout)
        cls.w.m.relocations = lru_cache(maxsize=8)(cls.w.m.relocations)
        cls.original = (v.ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
        cls.candidate = v.read(HERE / 'artifacts/candidate-symbols.so')
        cls.before = v.read(v.SOURCE_PARENT / 'sources' / v.SOURCE_FILE)
        cls.after = v.read(HERE / 'overrides' / v.SOURCE_FILE)
        cls.link_map = v.read(HERE / 'builds/candidate.map').decode()
        cls.sections = {s['name']: s for s in cls.w.m.elf_layout(cls.candidate)['sections']}

    def file_offset(self, address):
        section = next(s for s in self.sections.values() if s['address'] <= address < s['address'] + s['size'])
        return section['offset'] + address - section['address']

    def reject_data(self, candidate):
        with self.assertRaises((AssertionError, StopIteration, KeyError, struct.error)):
            v.check_data(self.w, self.original, candidate, self.link_map)

    def test_correct_source(self):
        v.check_source(self.before, self.after)

    def test_private_helper_retained(self):
        with self.assertRaises(AssertionError):
            v.check_source(self.before, self.before)

    def test_unrelated_source_change(self):
        with self.assertRaises(AssertionError):
            v.check_source(self.before, self.after + b'\n')

    def test_changed_borrow_semantics(self):
        with self.assertRaises(AssertionError):
            v.check_source(self.before, self.after.replace(b'curve_quote_mint', b'different_quote_helper'))

    def test_correct_data(self):
        self.assertEqual(len(v.check_data(self.w, self.original, self.candidate, self.link_map)), 379)

    def test_nonpointer_payload(self):
        damaged = bytearray(self.candidate)
        section = self.sections['.data.rel.ro']
        fields = {p + i for p, kind in self.w.m.relocations(self.candidate)
                  if section['address'] <= p < section['address'] + section['size'] for i in range(8)}
        address = next(p for p in range(section['address'], section['address'] + section['size']) if p not in fields)
        damaged[self.file_offset(address)] ^= 1
        self.reject_data(bytes(damaged))

    def test_changed_function_target(self):
        damaged = bytearray(self.candidate)
        targets = {row['address']: row for row in self.w.windows(self.candidate)}
        row = next(r for r in v.load(HERE / 'data/targets.json')['references'] if r['evidence'] == 'complete-normalized-function')
        other = next(p for p, value in targets.items() if value['signature'] != targets[row['candidate_target']]['signature'])
        address = self.sections['.data.rel.ro']['address'] + row['offset']
        struct.pack_into('<II', damaged, self.file_offset(address), 0, other)
        self.reject_data(bytes(damaged))

    def test_changed_readonly_target_content(self):
        damaged = bytearray(self.candidate)
        row = next(r for r in v.load(HERE / 'data/targets.json')['references'] if r['evidence'] == 'complete-compiled-rodata-allocation')
        damaged[self.file_offset(row['candidate_target'])] ^= 1
        self.reject_data(bytes(damaged))

    def test_changed_internal_offset(self):
        damaged = bytearray(self.candidate)
        row = next(r for r in v.load(HERE / 'data/targets.json')['references'] if r['evidence'] == 'internal-data-reference')
        address = self.sections['.data.rel.ro']['address'] + row['offset']
        struct.pack_into('<II', damaged, self.file_offset(address), 0, row['candidate_target'] + 8)
        self.reject_data(bytes(damaged))


if __name__ == '__main__':
    unittest.main()
