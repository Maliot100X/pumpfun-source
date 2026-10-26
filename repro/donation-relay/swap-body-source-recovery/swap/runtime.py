from pathlib import Path
import hashlib,json,importlib.util,sys,traceback
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest()
proposal=ROOT/'repro/donation-relay/local-validation-proposal';harness=proposal/'harness_proposal.py';expected='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
assert H(harness.read_bytes())==expected
build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged']
candidate=P/'candidate.so';assert H(candidate.read_bytes())==build['candidate_sha256']
spec=importlib.util.spec_from_file_location('frozen_relay_origin_harness',harness);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=dict(m.EXPECTED);m.EXPECTED=dict(old,candidate=build['candidate_sha256']);group=sys.argv[1];assert group in ('ordinary','business_rejection')
out=P/('runtime-'+group);out.mkdir(exist_ok=False)
record=dict(harness_sha256=expected,proposal_manifest_sha256=H((proposal/'manifest.json').read_bytes()),old_bindings=old,bindings=m.EXPECTED,group=group,adaptation='Only the module-local candidate digest binding changes. The frozen harness verifies its original package before execution. Fixtures, transaction/signature/blockhash checks, comparator, effects and stop-on-first-mismatch remain unchanged.')
(out/'launch.json').write_text(json.dumps(record,indent=2)+'\n');code=0
try:m.execute(ROOT,candidate,group,out/'comparison.json')
except BaseException as exc:
 code=exc.code if isinstance(exc,SystemExit) and isinstance(exc.code,int) else 1
 (out/'failure.txt').write_text(traceback.format_exc())
facts=dict(returncode=code,harness_unchanged=H(harness.read_bytes())==expected,candidate_unchanged=H(candidate.read_bytes())==build['candidate_sha256'],report_exists=(out/'comparison.json').exists())
(out/'process-result.json').write_text(json.dumps(facts,indent=2)+'\n')
if facts['report_exists']:
 r=json.loads((out/'comparison.json').read_text());print(json.dumps(dict(group=group,cases=[dict(name=x['case']['name'],mismatches=x['mismatches']) for x in r['cases']],passed=r['passed'],all_requested_completed=r['all_requested_completed'])))
print(json.dumps(facts));raise SystemExit(code)
