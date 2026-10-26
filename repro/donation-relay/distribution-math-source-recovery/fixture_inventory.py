"""Count actual input stimuli independently of human-readable case labels."""
from pathlib import Path
import hashlib,json,collections
H=lambda b:hashlib.sha256(b).hexdigest()
def derive(stage):
 stage=Path(stage);groups=collections.defaultdict(list);files=sorted(list(stage.glob('*-cases.json'))+[stage/'idl-rejections.json']+list(stage.glob('runtime-*/comparison.json')));records=0
 for file in files:
  report=json.loads(file.read_text());assert 'cases' in report
  for index,row in enumerate(report['cases']):
   fixture=row['fixture'];stimulus={k:fixture[k] for k in ['accounts','instruction_hex','instruction_accounts']};digest=H(json.dumps(stimulus,sort_keys=True,separators=(',',':')).encode());label=row.get('kind',row.get('case',{}).get('name',str(index)));groups[digest].append(dict(file=str(file.relative_to(stage)),route=row.get('route'),case=label));records+=1
 duplicates=[dict(stimulus_sha256=h,records=rows) for h,rows in sorted(groups.items()) if len(rows)>1];assert records==536 and len(groups)==534
 assert len(duplicates)==1 and [x['case'] for x in duplicates[0]['records']]==['wrong_relayer','epoch_tracker_readonly','debouncer_readonly']
 return dict(case_records=records,unique_input_fixtures=len(groups),extra_duplicate_records=records-len(groups),duplicates=duplicates,definition='A stimulus consists of all supplied starting account states, instruction bytes and ordered account metas. Labels and other proof metadata do not make a distinct input. Loaded executable bytes are separately bound.')
if __name__=='__main__':
 import sys
 print(json.dumps(derive(sys.argv[1]),indent=2))
