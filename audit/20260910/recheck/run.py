from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,unquote
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import requests,json,re,xml.etree.ElementTree as E
BASE='https://www.piste-ai.com';OUT=Path('audit/20260910/recheck')
class Page(HTMLParser):
 def __init__(self):super().__init__();self.tags=[];self.values={};self.active=None;self.buf=''
 def handle_starttag(self,t,a):
  d=dict(a);self.tags.append((t,d))
  if t in ('title','h1') or (t=='script' and d.get('type')=='application/ld+json'):self.active=t;self.buf=''
 def handle_data(self,d):
  if self.active:self.buf+=d
 def handle_endtag(self,t):
  if t==self.active:self.values.setdefault(t,[]).append(self.buf.strip());self.active=None

def get(url):
 try:
  r=requests.get(url,timeout=30);p=Page();p.feed(r.text)
  meta=lambda attr,val:[a.get('content',a.get('href','')) for t,a in p.tags if a.get(attr)==val and t in ('link','meta')]
  imgs=[a for t,a in p.tags if t=='img'];scripts=[a.get('src','') for t,a in p.tags if t=='script'];ld=[];ld_errors=[]
  for v in p.values.get('script',[]):
   try:ld.append(json.loads(v))
   except ValueError:ld_errors.append(v[:100])
  row={'url':url,'status':r.status_code,'final':r.url,'bytes':len(r.content),'title':p.values.get('title',[]),'h1':p.values.get('h1',[]),'canonical':meta('rel','canonical'),'description':meta('name','description'),'og_image':meta('property','og:image'),'noindex':'noindex' in (','.join(meta('name','robots'))+r.headers.get('x-robots-tag','')),'scripts':scripts,'json_ld_count':len(ld),'json_ld_errors':ld_errors,'missing_alt':sum('alt' not in a for a in imgs),'missing_dimensions':sum(not a.get('width') or not a.get('height') for a in imgs),'images':imgs,'links':[a['href'] for t,a in p.tags if t=='a' and 'href'in a],'ids':[a['id'] for t,a in p.tags if 'id'in a]}
  if url==BASE+'/':(OUT/'home.html').write_text(r.text)
  return row
 except Exception as e:return {'url':url,'error':type(e).__name__}
sm=requests.get(BASE+'/sitemap.xml',timeout=30);(OUT/'sitemap.xml').write_text(sm.text);ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'};urls=[x.text for x in E.fromstring(sm.content).findall('s:url/s:loc',ns)]
rows=list(ThreadPoolExecutor(max_workers=6).map(get,urls));byurl={r['url']:r for r in rows};broken=[]
for row in rows:
 for href in row.get('links',[]):
  u=urlsplit(urljoin(row['url'],href))
  if u.netloc!='www.piste-ai.com':continue
  target=u._replace(query='',fragment='').geturl()
  if target in byurl and u.fragment and unquote(u.fragment) not in byurl[target].get('ids',[]):broken.append({'page':row['url'],'href':href})
summary={'sitemap_urls':len(urls),'duplicate_sitemap_urls':len(urls)-len(set(urls)),'statuses':dict(Counter(r.get('status','error') for r in rows)),'bad_canonical':[r['url'] for r in rows if r.get('canonical')!=[r['url']]],'bad_h1':[r['url'] for r in rows if len(r.get('h1',[]))!=1],'missing_description':[r['url'] for r in rows if not r.get('description')],'missing_og_image':[r['url'] for r in rows if not r.get('og_image')],'bad_measurement_loader':[r['url'] for r in rows if r.get('scripts',[]).count('/js/analytics.js')!=1],'noindex':[r['url'] for r in rows if r.get('noindex')],'invalid_json_ld':[r['url'] for r in rows if r.get('json_ld_errors')],'missing_alt_pages':[r['url'] for r in rows if r.get('missing_alt')],'missing_dimensions_pages':[r['url'] for r in rows if r.get('missing_dimensions')],'broken_fragments':broken}
(OUT/'pages.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
