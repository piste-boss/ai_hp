from pathlib import Path
from bs4 import BeautifulSoup as S
p=Path('site/index.html');s=S(p.read_text(),'html.parser')
if 'redesign-home' in s.body.get('class',[]):raise SystemExit('Design already applied')
s.body['class']=s.body.get('class',[])+['redesign-home']
# Keep existing metadata, analytics, legal links and contact fields.
for link in s.select('link[rel=preload][as=image]'):link.decompose()
pre=s.new_tag('link',rel='preload',href='/images/redesign-ascent-1200.webp');pre['as']='image';pre['fetchpriority']='high';s.head.append(pre)
css=s.new_tag('link',rel='stylesheet',href='/css/redesign-20260910.css');s.head.append(css)
logo=s.select_one('.header-logo');logo.clear();logo.append(S('<img src="/images/logo.webp" alt="" width="240" height="240"><span class="rd-wordmark">PISTE AI<small>EVANGELISTS</small></span>','html.parser'))
nav=s.select_one('.header-nav');nav.clear();nav.append(S('<a href="#services">支援内容</a><a href="#plans">料金プラン</a><a href="#profile">私たちについて</a><a href="/blog/">AI活用コラム</a><a href="#contact" class="header-cta">無料相談 <span aria-hidden="true">↗</span></a>','html.parser'))
s.select_one('.mobile-nav')['id']='mobile-menu';s.select_one('.hamburger')['aria-controls']='mobile-menu';s.select_one('.hamburger')['aria-expanded']='false'
hero=S('''<section class="rd-hero"><div class="container rd-hero-grid"><div class="rd-hero-copy"><p class="rd-eyebrow"><span></span> YOUR AI IMPLEMENTATION PARTNER</p><h1>AIを、<br>仕事の<span class="rd-accent">力</span>に。</h1><p class="rd-hero-description">企業のAI導入を、現場で使える形まで。<br>相談から実装、運用の定着まで、<br>あなたの隣で、一緒に進めます。</p><div class="rd-hero-actions"><a href="#contact" class="btn-primary">まずは無料で相談する <span aria-hidden="true">↗</span></a><a href="#services" class="rd-text-link">支援内容を見る <span aria-hidden="true">↓</span></a></div><p class="rd-hero-note">中小企業・個人事業主のための、マンツーマンAI導入支援</p></div><figure class="rd-hero-art"><img src="/images/redesign-ascent-1200.webp" srcset="/images/redesign-ascent-640.webp 640w, /images/redesign-ascent-1200.webp 1122w" sizes="(max-width: 700px) 100vw, 46vw" width="1122" height="1402" alt="一歩ずつ上へ伸びる金色の道を表現したコンセプトアート" fetchpriority="high" loading="eager"><figcaption><span>TOGETHER,<br>ONE STEP AHEAD.</span><span class="rd-art-number">01 — ∞</span></figcaption></figure></div><div class="container rd-trust"><p>愛知県碧南市から、全国へ。</p><div><span>全国オンライン対応</span><span>相談・実装・定着を一貫支援</span><span>Anthropic 公式パートナーネットワーク認定企業</span></div></div></section>''','html.parser').section
s.select_one('section.hero').replace_with(hero)
intro=s.select_one('.intro');intro.select_one('h2').clear();intro.select_one('h2').append(S('AIを「試した」から、<br>毎日の「使える」へ。','html.parser'))
intro.select_one('.intro-grid').append(S('''<figure class="rd-work-image"><img src="/images/redesign-workshop-1200.webp" srcset="/images/redesign-workshop-640.webp 640w, /images/redesign-workshop-1200.webp 1200w" sizes="(max-width:700px) 100vw, 50vw" width="1200" height="800" loading="lazy" alt="ノートとパソコンを使って業務の流れを一緒に整理する様子を描いたイメージ"><figcaption>大切なのは、あなたの業務に合うこと。<small>AI生成によるイメージ</small></figcaption></figure>''','html.parser'))
# Compact service presentation with large editorial numerals.
for i,item in enumerate(s.select('.service-item'),1):
 item['class']=['service-item'];item.select_one('.service-image').decompose()
 marker=s.new_tag('div',attrs={'class':'rd-service-number','aria-hidden':'true'});marker.string=f'0{i}';item.insert(0,marker)
 span=item.select_one('.service-text > span')
 if span:span.decompose()
 a=s.new_tag('a',href='#contact',attrs={'class':'rd-service-link'});a.string='この支援について相談する ↗';item.append(a)
# Preserve detailed training text inside a native disclosure.
training=s.select_one('#training');details=s.new_tag('details',attrs={'class':'rd-training-details'});summary=s.new_tag('summary');summary.string='研修の概要・学習ロードマップを見る';details.append(summary)
for block in list(training.select('.training-overview,.training-roadmap')):details.append(block.extract())
training.select_one('.training-cta').insert_before(details)
# Reuse all existing news content as accessible native disclosures.
news=s.select_one('#news');items=[]
for item in news.select('.news-item'):
 d=s.new_tag('details',attrs={'class':'rd-news-item'});summary=s.new_tag('summary');date=item.find('p',recursive=False);h=item.find('h3');detail=item.select_one('.news-detail')
 if date:
  stamp=s.new_tag('span',attrs={'class':'rd-news-date'});stamp.string=date.get_text(' ',strip=True);summary.append(stamp)
 if h:
  for icon in h.select('span'):icon.decompose()
  title=s.new_tag('span',attrs={'class':'rd-news-title'});title.string=h.get_text(' ',strip=True);summary.append(title)
 d.append(summary)
 if detail:
  detail.attrs={'class':'rd-news-body'};d.append(detail.extract())
 items.append(d)
lst=news.select_one('.news-list');lst.clear();lst.attrs={'class':'news-list'}
for item in items:lst.append(item)
for b in news.select('#newsMoreBtn,.news-item-hidden'):b.decompose()
# Preserve the existing form semantics and add context beside it.
copy=s.select_one('.contact-copy');copy.select_one('h2').clear();copy.select_one('h2').append(S('次の一歩を、<br>一緒に。','html.parser'))
copy.append(S('<p class="rd-contact-lead">「何から始めればいい？」からで大丈夫です。<br>いまの業務やお困りごとを、お聞かせください。</p><p class="rd-contact-note">ご相談内容を確認し、担当者よりご連絡します。</p><a class="rd-contact-line" href="https://lin.ee/Pul5f6V" target="_blank" rel="noopener">LINEで気軽に相談する ↗</a>','html.parser'))
# Menu hierarchy and section sequence.
main=s.main
sections={x.get('id') or x.get('class',[''])[1] if len(x.get('class',[]))>1 else x.get('id') or x.get('class',[''])[0]:x for x in main.find_all('section',recursive=False)}
order=[hero,intro,s.select_one('.problems'),s.select_one('#services'),s.select_one('#spot'),s.select_one('#plans'),s.select_one('#flow'),s.select_one('#profile'),s.select_one('#media'),s.select_one('#training'),s.select_one('#blog'),s.select_one('#news'),s.select_one('#line-cta'),s.select_one('#contact')]
for x in order:
 if x:main.append(x.extract())
# Remove redundant inline appearance, retaining functional style attributes.
for n in s.select('#news .section-title,#news .section-heading'):
 n.attrs.pop('style',None)
s.select_one('#line-cta .section-heading').string='まずは、無料ガイドから。'
p.write_text(str(s))
print('Redesigned homepage; news disclosures:',len(items))
