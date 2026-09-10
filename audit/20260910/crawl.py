import requests,json,re,concurrent.futures,collections,xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
BASE='https://www.piste-ai.com/'
OUT=Path('audit/20260910')
class Parser(HTMLParser):
 def __init__(self): super().__init__();self.tags=[];self.active=None;self.fields=collections.defaultdict(list)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append((tag,a))
  if tag in ['title','h1','h2'] or (tag=='script' and a.get('type')=='application/ld+json'):self.active=tag;self.buf=''
 def handle_data(self,data):
  if self.active:self.buf+=data
 def handle_endtag(self,tag):
  if tag==self.active:self.fields[tag].append(self.buf.strip());self.active=None

def parse(html):
 p=Parser();p.feed(html);d=dict(p.fields)
 for key,tag,attr,val,out in [('name','meta','content','description','description'),('rel','link','href','canonical','canonical'),('property','meta','content','og:image','ogimage'),('name','meta','content','robots','robots')]:d[out]=[a.get(attr) for t,a in p.tags if t==tag and a.get(key)==val]
 d['links']=[a['href'] for t,a in p.tags if t=='a' and a.get('href')]; imgs=[a for t,a in p.tags if t=='img'];d['images']=len(imgs);d['missing_alt']=sum('alt' not in a for a in imgs);d['missing_dimensions']=sum(not a.get('width') or not a.get('height') for a in imgs);d['ga4']=sorted(set(re.findall(r'G-[A-Z0-9]{6,}',html)));d['clarity']='w54yutjekb' in html;d['noindex']='noindex' in ' '.join(d['robots']);return d

def fetch(url):
 try:
  r=requests.get(url,timeout=25);d={'url':url,'final':r.url,'status':r.status_code,'bytes':len(r.content),'xrobots':r.headers.get('x-robots-tag'),'type':r.headers.get('Content-Type')};
  if 'text/html' in d['type']:d.update(parse(r.text))
  if url==BASE:(OUT/'home.html').write_text(r.text)
  return d
 except Exception as e:return {'url':url,'error':str(e)}
sm=requests.get(BASE+'sitemap.xml',timeout=25);(OUT/'sitemap.xml').write_text(sm.text);smurls=[e.text for e in ET.fromstring(sm.content).iter() if e.tag.endswith('}loc')]
local=[]
for f in Path('site').rglob('*.html'):
 if '.netlify' in str(f):continue
 rel=f.relative_to('site').as_posix();url=BASE+('' if rel=='index.html' else rel[:-10] if rel.endswith('index.html') else rel);local.append((url,f))
urls=sorted(set(smurls+[u for u,f in local]));rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(fetch,urls));(OUT/'pages.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
summary={'sitemap_status':sm.status_code,'sitemap_urls':len(smurls),'local_html':len(local),'requested':len(rows),'statuses':dict(collections.Counter(x.get('status','error') for x in rows)),'missing_from_sitemap':[u for u,f in local if u not in smurls],'missing_ga':[x['url'] for x in rows if not x.get('ga4')],'missing_clarity':[x['url'] for x in rows if not x.get('clarity')],'missing_canonical':[x['url'] for x in rows if not x.get('canonical')],'bad_h1':[x['url'] for x in rows if len(x.get('h1',[]))!=1],'missing_alt_pages':[x['url'] for x in rows if x.get('missing_alt',0)],'missing_desc':[x['url'] for x in rows if not x.get('description')]}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in summary.items()},ensure_ascii=False));print('missing_ga examples',summary['missing_ga'][:8]);print('home',json.dumps(rows[[x['url'] for x in rows].index(BASE)],ensure_ascii=False)[:5000])
