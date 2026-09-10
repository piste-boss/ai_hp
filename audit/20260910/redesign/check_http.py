import json, sys, hashlib
from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parent
base=sys.argv[1].rstrip('/')
paths=['/','/css/redesign-20260910.css','/images/redesign-ascent-1200.webp','/images/redesign-ascent-640.webp','/images/redesign-workshop-1200.webp','/images/redesign-workshop-640.webp','/js/main.js','/js/analytics.js','/about','/blog/','/sitemap.xml']
def check(path):
 with urlopen(base+path,timeout=45) as res:
  data=res.read()
  assert res.status==200
  if path=='/':
   html=data.decode();assert 'redesign-home' in html and 'rd-hero' in html and 'contactForm' in html and 'redesign-20260910.css' in html
  if path.startswith(('/css/','/images/','/js/')):
   local=root.parent/'release/public'/path.lstrip('/')
   assert data==local.read_bytes(),path+' asset mismatch'
  return {'path':path,'status':res.status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
result={'base':base,'checks':list(ThreadPoolExecutor(max_workers=6).map(check,paths))}
(root/('http-check.json' if 'www.piste-ai.com' in base else 'preview-http-check.json')).write_text(json.dumps(result,indent=2))
print(json.dumps({'base':base,'passed':len(result['checks'])}))
