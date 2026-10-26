"""Read-only comparison of resolved registry source trees with pinned crate archives."""
from pathlib import Path
import hashlib,json,tarfile,tomllib,argparse
P=Path(__file__).resolve().parent;ROOT=P.parents[2];H=lambda b:hashlib.sha256(b).hexdigest()
def audit():
 metadata=json.loads((P/'current-source-proof/resolve.log').read_text());lock=tomllib.loads((P/'swap/source/Cargo.lock').read_text());checks={(p['name'],p['version']):p['checksum'] for p in lock['package'] if 'source' in p};rows=[]
 home=ROOT/'work/relay-anchor-idl-scaffold/cargo-home/registry';index='index.crates.io-6f17d22bba15001f'
 for package in sorted(metadata['packages'],key=lambda p:(p['name'],p['version'])):
  if package['source'] is None:continue
  key=(package['name'],package['version']);prefix='-'.join(key);archive=home/'cache'/index/(prefix+'.crate');assert H(archive.read_bytes())==checks[key],key;source=home/'src'/index/prefix
  with tarfile.open(archive) as tar:
   files={m.name[len(prefix)+1:]:H(tar.extractfile(m).read()) for m in tar.getmembers() if m.isfile()};sizes={m.name[len(prefix)+1:]:m.size for m in tar.getmembers() if m.isfile()}
  actual={str(f.relative_to(source)) for f in source.rglob('*') if f.is_file() and f.name not in ['.cargo-ok','.cargo-checksum.json']};assert actual==set(files),(key,actual^set(files))
  assert not any((source/n).is_symlink() for n in files);assert all(H((source/n).read_bytes())==h for n,h in files.items()),key
  rows.append(dict(name=key[0],version=key[1],archive_sha256=checks[key],files=files,bytes=sum(sizes.values())))
 return dict(registry_packages=len(rows),files=sum(len(r['files']) for r in rows),bytes=sum(r['bytes'] for r in rows),packages=rows)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result=audit();target=P/'registry-source-audit.json'
 if args.write:target.write_text(json.dumps(result,indent=2)+'\n')
 else:assert result==json.loads(target.read_text())
 print(json.dumps({k:v for k,v in result.items() if k!='packages'}))
