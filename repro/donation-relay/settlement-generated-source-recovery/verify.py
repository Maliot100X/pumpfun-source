#!/usr/bin/env python3
"""Read-only source/output/full-body/data/call-map checks; no VM execution."""
from pathlib import Path
import argparse,hashlib,json,gzip,importlib.util,tomllib,tarfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2];H=lambda b:hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(current=False,registry_source=False):
 assert {str(f.relative_to(P)) for f in P.rglob("*") if f.is_file() and str(f.relative_to(P))!="manifest.json" and "__pycache__" not in f.parts}==set(read(P/"manifest.json"))
 for n,h in read(P/'manifest.json').items():assert H((P/n).read_bytes())==h,n
 for n,h in read(P/'external-inputs.json').items():assert H((ROOT/n).read_bytes())==h,n
 a=mod('payer_generated_elf',P/'analyze.py');selected=P/'settlement';source=read(selected/'source-manifest.json');assert len(source)==49 and all(H((selected/'source'/n).read_bytes())==h for n,h in source.items())
 assert set(source)=={str(f.relative_to(selected/'source')) for f in (selected/'source').rglob('*') if f.is_file() and (f.suffix=='.rs' or f.name in ['Cargo.toml','Cargo.lock'])}
 b=read(selected/'build-result.json');assert b['returncode']==0 and b['source_unchanged'] and H((selected/'build.log').read_bytes())==b['log_sha256'];assert H((selected/'candidate.so').read_bytes())==b['candidate_sha256'] and H((selected/'unstripped.so').read_bytes())==b['unstripped_sha256']
 class View:
  def __truediv__(self,n):return ROOT/'evidence/dependencies/donation_relay/deployed.so' if n=='original.so' else P/'original-windows.json' if n=='original-windows.json' else selected/n
 outputs=a.analyze(View())
 for n,v in outputs.items():assert v==read(selected/(n if n.endswith('.gz') else n+'.gz')),n
 summary=outputs['comparison-summary.json'];assert summary['original_normalized_match_windows']==462 and summary['original_raw_match_windows']==93 and not summary['whole_file_equal'];ledger=outputs['match-ledger.json'];prior=read(ROOT/'repro/donation-relay/swap-body-source-recovery/swap/match-ledger.json.gz');assert [x['ordinal'] for x,y in zip(ledger,prior) if not x['normalized_candidate_indices'] and y['normalized_candidate_indices']]==read(P/'losses.json')==[69,332];fs=outputs['candidate-function-ledger.json'];gains=[dict(ordinal=x['ordinal'],bytes=x['bytes'],candidate_names=[fs[i]['names'] for i in x['normalized_candidate_indices']]) for x,y in zip(ledger,prior) if x['normalized_candidate_indices'] and not y['normalized_candidate_indices']];assert gains==read(P/'gains.json') and [x['ordinal'] for x in gains]==[81, 119, 146, 147, 148, 149, 154, 155, 169, 184, 186, 187, 194, 200, 201, 203]
 old=tomllib.loads((ROOT/'repro/donation-relay/swap-body-source-recovery/swap/source/Cargo.lock').read_text())['package'];new=tomllib.loads((selected/'source/Cargo.lock').read_text())['package'];assert old==new
 # Native wrapper/context/predicate edges are decoded from actual ELF bodies.
 original=a.Elf((ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes());windows=read(P/'original-windows.json');of=outputs['original-function-ledger.json'];rows=read(P/'native-call-map.json');assert [(r['wrapper'],r['parser'],r['closures'],r['exit']) for r in rows]==[(180,126,[127,128,129,124],130),(181,131,[132,133,134,124],130)]
 for row in rows:
  log=('Instruction: '+''.join(x.capitalize() for x in row['instruction'].split('_'))).encode();wrapper=of[row['wrapper']];targets={x['target'] for x in wrapper['direct_calls']};assert windows[row['parser']]['start'] in targets and windows[row['exit']]['start'] in targets
  assert any(original.at(x['target'],len(log))==log for x in wrapper['data_references']);parser_targets={x['target'] for x in of[row['parser']]['direct_calls']}
  for closure in row['closures']+[102,103]:assert windows[closure]['start'] in parser_targets and ledger[closure]['normalized_candidate_indices']
  assert ledger[row['parser']]['normalized_candidate_indices'] and ledger[row['exit']]['normalized_candidate_indices']
 registry={x['name']+'-'+x['version']+'.crate':x['checksum'] for x in new if 'source' in x}
 for row in read(P/'primary-source.json'):
  archive=P/row['archive'];assert H(archive.read_bytes())==row['archive_sha256']==registry[archive.name]
  with tarfile.open(archive,'r:gz') as tar:data=tar.extractfile(row['member']).read()
  assert data==(P/row['path']).read_bytes() and H(data)==row['sha256']
 successes=0;failures=0
 for trial in sorted((P/'trials').iterdir()):
  source_map=read(trial/'source-manifest.json');assert all(H((trial/'source'/n).read_bytes())==h for n,h in source_map.items());result=read(trial/'build-result.json');assert result['source_unchanged'] and H((trial/'build.log').read_bytes())==result['log_sha256']
  if result['returncode']:
   failures+=1;assert trial.name in ['unknown-error-variant','argument-borrow-mismatch'] and result['returncode']==101;continue
  successes+=1;assert H((trial/'candidate.so').read_bytes())==result['candidate_sha256'] and H((trial/'unstripped.so').read_bytes())==result['unstripped_sha256']
  class TrialView:
   def __truediv__(self,n):return ROOT/'evidence/dependencies/donation_relay/deployed.so' if n=='original.so' else P/'original-windows.json' if n=='original-windows.json' else trial/n
  for name,value in a.analyze(TrialView()).items():assert value==read(trial/(name if name.endswith('.gz') else name+'.gz')),(trial.name,name)
 assert failures==0 and successes==6
 for row in read(P/'primary/new-index-records.json'):
  assert (row['name'],row['vers']) in {('spl-token-2022','7.0.0'),('spl-token-confidential-transfer-proof-generation','0.3.0')};assert registry[row['name']+'-'+row['vers']+'.crate']==row['cksum']
 for filename in (P/'primary').glob('*-archive-members.json'):
  row=read(filename);archive=P/row['archive'];assert H(archive.read_bytes())==row['sha256']==registry[archive.name]
  with tarfile.open(archive) as tar:assert {m.name:H(tar.extractfile(m).read()) for m in tar.getmembers() if m.isfile()}==row['files']
 if registry_source:assert mod('typed_mint_registry_audit',P/'audit_registry.py').audit()==read(P/'registry-source-audit.json')
 assert mod('typed_mint_policy_residual',P/'policy_residual.py').derive()==read(P/'policy-residual.json')
 assert mod('shared_donation_evidence',P/'shared_evidence.py').derive()==read(P/'shared-evidence.json')
 assert mod('close_epoch_evidence',P/'close_evidence.py').derive()==read(P/'close-evidence.json')
 assert mod('just_swap_evidence',P/'just_evidence.py').derive()==read(P/'just-evidence.json')
 assert mod('swap_balance_evidence',P/'balance_evidence.py').derive()==read(P/'balance-evidence.json')
 assert mod('settlement_generated_evidence',P/'settlement_evidence.py').derive()==read(P/'settlement-evidence.json')
 assert mod('actual_fixture_inventory',P/'fixture_inventory.py').derive(selected)==read(P/'fixture-inventory.json')
 assert [row['ordinal'] for row in read(P/'remaining-windows.json')]==[row['ordinal'] for row in ledger if not row['normalized_candidate_indices']] and len(read(P/'remaining-windows.json'))==30
 proof=P/'current-source-proof';b=read(proof/'build-result.json');assert b['returncode']==0 and b['source_unchanged'] and H((proof/'build.log').read_bytes())==b['log_sha256'];assert read(proof/'source-manifest.json')==source
 for n in ['candidate.so','unstripped.so']:assert (proof/n).read_bytes()==(selected/n).read_bytes()
 class LedgerText:
  def read_text(self):return gzip.decompress((selected/'candidate-function-ledger.json.gz').read_bytes()).decode()
 class SelectorView:
  def __truediv__(self,n):return ROOT/'evidence/dependencies/donation_relay/deployed.so' if n=='original.so' else P/'original-windows.json' if n=='original-windows.json' else LedgerText() if n=='candidate-function-ledger.json' else selected/n
 selectors=mod('payer_generated_selectors',selected/'check-selectors.py');selectors.P=SelectorView();assert {n:selectors.derive(n) for n in ['anchor']}==read(selected/'selector-proof-anchor77.json')
 program=mod('payer_generated_program_selectors',selected/'check-program-data.py');program.P=SelectorView();assert program.derive()==read(selected/'program-data-proof-all34.json')
 if current:assert all(H((ROOT/'programs/donation-relay'/n).read_bytes())==h for n,h in source.items())
 print(json.dumps(dict(verified=True,selected_source_builds=2,successful_background_source_builds=successes,failed_background_source_builds=failures,registry_source_checked=registry_source,normalized_windows=462,raw_windows=93,gained=[81, 119, 146, 147, 148, 149, 154, 155, 169, 184, 186, 187, 194, 200, 201, 203],lost=[69,332],native_call_map_checked=True,current_source_checked=current,selector_records=111,whole_original_byte_identity=False,vm_execution=False)))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--current',action='store_true');ap.add_argument('--check-registry-source',action='store_true');args=ap.parse_args();main(args.current,args.check_registry_source)
