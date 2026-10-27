#!/usr/bin/env python3
"""Rebuild the archived main-Pump source with explicit external SBF target libraries."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
ROOT=next(p for p in P.parents if (p/'evidence/original/pump/deployed.so').is_file())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--registry-home',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--dependency-cache',type=Path)
 p.add_argument('--sdk',type=Path,help='Native macOS v1.44 SDK; its tool hashes must match the pinned profile.')
 p.add_argument('--target-library-directory',type=Path,required=True,help='External official Linux v1.44 SBF library directory (25 libraries and empty self-contained/).')
 a=p.parse_args();cp=json.loads((P/'CHECKPOINT.json').read_text())
 for name,digest in cp['primary_source_sha256'].items():assert sha(P/'primary'/name)==digest
 for name in ['scripts/pump_build_verified.py','scripts/pump_dependency_cache.py','scripts/pump_target_library_profile.py','scripts/pump_physical_source_wrapper.py']:
  assert sha(P/'inputs'/name)==cp['input_python_sha256'][name]
 assert sha(P/'inputs/scripts/pump_linux_v144_sbf_libraries.json')==cp['additional_input_sha256']['scripts/pump_linux_v144_sbf_libraries.json']
 assert sha(ROOT/'scripts/pump_physical_source_wrapper.py')==cp['input_python_sha256']['scripts/pump_physical_source_wrapper.py']
 sys.path.insert(0,str(P/'inputs/scripts'));path=P/'inputs/scripts/pump_build_verified.py'
 spec=importlib.util.spec_from_file_location('archived_pump_builder',path);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);b.ROOT=ROOT
 sys.argv=[str(path),'--source-directory',str(P/'primary'),'--workspace-layout','--registry-home',str(a.registry_home.resolve()),'--output',str(a.output.resolve()),'--target-library-profile',cp['target_library_profile'],'--target-library-directory',str(a.target_library_directory.resolve())]
 if a.sdk:sys.argv+=['--sdk',str(a.sdk.resolve())]
 if a.dependency_cache:sys.argv+=['--dependency-cache',str(a.dependency_cache.resolve())]
 if cp.get('text_section_order'):
  order=P/cp['text_section_order'];assert sha(order)==cp['text_section_order_sha256'];sys.argv+=['--text-section-order',str(order)]
 b.main();report=json.loads((a.output/'build-comparison.json').read_text())
 assert report['target_library_profile']['cache_context']==cp['target_library_profile_context']
 assert report['target_library_profile']['native_host_files_unchanged'] is True
 assert report['comparison']['candidate_sha256']==cp['candidate_sha256'] and report['unstripped_sha256']==cp['unstripped_sha256']
 print('Archived primary source reproduced both ELF hashes under the pinned hybrid target-library profile.')
if __name__=='__main__':main()
