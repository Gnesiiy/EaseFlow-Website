#!/usr/bin/env python3
"""Generate dependency-free static pages from the approved bilingual copy."""
from pathlib import Path
import re, html, shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'EaseFlow_Website_Copy_zh_en.md'
OUT = ROOT / 'dist'
EMAIL = 'easeflowsupport@163.com'
SLUGS = ['home', 'privacy', 'terms', 'support']
LABELS = {'zh-Hans': ['首页', '隐私政策', '使用条款', '帮助与支持'], 'en': ['Home', 'Privacy Policy', 'Terms of Use', 'Help & Support']}
COPY = {}
for slug, block in zip(SLUGS, re.split(r'^# 0[1-4] · .*$', SOURCE.read_text(), flags=re.M)[1:]):
    parts = re.split(r'^## (zh-Hans|en)\s*$', block, flags=re.M)
    for i in range(1, len(parts), 2):
        COPY[slug, parts[i]] = re.sub(r'\n---\s*$', '', parts[i+1].strip()).strip()
assert len(COPY) == 8, 'Expected four complete bilingual pages'

def inline(s):
    s = html.escape(s)
    s = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(\[[^\]]+\])', r'<mark class="pending">\1</mark>', s)
    return s.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')

def markdown(s):
    result, in_list = [], False
    for line in s.splitlines():
        if not line.strip(): continue
        if line.startswith('- '):
            if not in_list: result.append('<ul>'); in_list = True
            result.append('<li>' + inline(line[2:]) + '</li>'); continue
        if in_list: result.append('</ul>'); in_list = False
        match = re.match(r'^(#{1,4}) (.*)', line)
        if match:
            n = len(match[1]); result.append(f'<h{n}>{inline(match[2])}</h{n}>')
        else: result.append('<p>' + inline(line) + '</p>')
    if in_list: result.append('</ul>')
    return '\n'.join(result)

ICONS = [
    '<path d="M12 3 4.5 6v5.5c0 4.2 3.2 7.3 7.5 9.5 4.3-2.2 7.5-5.3 7.5-9.5V6L12 3Z"/><path d="m8.5 12 2.3 2.3 4.7-4.8"/>',
    '<path d="M7 3h7l4 4v14H6V3h1Z"/><path d="M14 3v5h4M9 12h6M9 16h5"/>',
    '<path d="M5 13v-3a7 7 0 0 1 14 0v3M5 11H3v6h4v-6H5Zm14 0h2v6h-4v-6h2ZM19 17v2l-5 2h-3"/>'
]
def icon(i): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[i]}</svg>'
ARROW = '<span aria-hidden="true">↗</span>'

def page(slug, lang):
    en = lang == 'en'; labels = LABELS[lang]; idx = SLUGS.index(slug)
    location = Path('en' if en else '') / (slug if slug != 'home' else '')
    depth = len(location.parts)
    base = '../' * depth or './'
    logo = f'<img class="brand-icon" src="{base}assets/brand-icon-96.png" alt="" width="37" height="37">'
    def link(s, target_lang=lang):
        return base + ('en/' if target_lang == 'en' else '') + (s + '/' if s != 'home' else '')
    current_page = 'aria-current="page"'
    current_lang = 'aria-current="true"'
    nav = ''.join(f'<a href="{link(s)}" {current_page if s == slug else ""}>{labels[i]}</a>' for i,s in enumerate(SLUGS[1:],1))
    switch = ''.join(f'<a lang="{l}" hreflang="{l}" href="{link(slug,l)}" {current_lang if l == lang else ""}>{label}</a>' for l,label in [('zh-Hans','中文'),('en','EN')])
    raw = COPY[slug,lang]; lines = raw.splitlines(); title = lines[0][2:]; body = '\n'.join(lines[1:]).strip()
    if slug == 'home':
        blocks = body.split('\n\n'); tagline = blocks[0].strip('*'); intro = blocks[1]; explore = blocks[2].strip('*')
        tagline_html = html.escape(tagline) if en else ''.join('<span class="tagline-line">' + html.escape(t) + '</span>' for t in re.findall(r'.*?[，。]', tagline))
        cards = []
        for i,line in enumerate(blocks[3].splitlines()):
            m = re.fullmatch(r'- \*\*(.*?)\*\* — (.*)',line); assert m
            cards.append(f'<a class="entry-card" href="{link(SLUGS[i+1])}"><div class="card-top"><span class="icon">{icon(i)}</span><span class="card-number">0{i+1}</span></div><h3>{m[1]} {ARROW}</h3><p>{m[2]}</p></a>')
        content = f'''<section class="hero" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow">EaseFlow</p><h1 id="hero-title">{tagline_html}</h1><p class="hero-description">{intro}</p><a class="text-link" href="#explore">{explore}<span aria-hidden="true">↓</span></a></div><div class="hero-art" aria-hidden="true"><img src="{base}assets/flow.svg" alt="" width="560" height="470"><div class="art-caption"><span class="small-mark">{logo}</span><span>EaseFlow</span><span class="art-line"></span></div></div></section><section id="explore" class="explore"><div class="section-heading"><h2>{explore}</h2><span aria-hidden="true">01 — 03</span></div><div class="entry-grid">{''.join(cards)}</div></section><div class="home-contact"><span class="contact-dot" aria-hidden="true"></span>{markdown(blocks[4])}{ARROW}</div>'''
    else:
        sections = re.split(r'^### (.*)$', body, flags=re.M)
        prelude = sections[0].strip()
        toc, articles = [], []
        for j in range(1,len(sections),2):
            heading, text = sections[j], sections[j+1].strip(); n=(j+1)//2
            anchor = f'section-{n}'
            toc.append(f'<a href="#{anchor}">{html.escape(heading)}</a>')
            if slug == 'support' and n == 1:
                faq = re.split(r'^#### (.*)$',text,flags=re.M); assert not faq[0].strip()
                text_html = ''.join(f'<details><summary>{inline(faq[k])}<span aria-hidden="true">+</span></summary><div class="answer">{markdown(faq[k+1])}</div></details>' for k in range(1,len(faq),2))
            else: text_html = markdown(text)
            articles.append(f'<section class="document-section" id="{anchor}"><h2>{inline(heading)}</h2>{text_html}</section>')
        note = ''  # Publication details have been confirmed in the approved copy.
        content = f'''<div class="page-intro"><a class="back-link" href="{link('home')}"><span aria-hidden="true">←</span> {'Back to home' if en else '返回首页'}</a><div class="page-heading"><span class="icon">{icon(idx-1)}</span>{note}</div><h1>{title}</h1><div class="prelude">{markdown(prelude)}</div></div><div class="document-layout"><aside class="contents"><p>{'On this page' if en else '本页内容'}</p><nav aria-label="{'On this page' if en else '本页目录'}">{''.join(toc)}</nav><a class="sidebar-contact" href="mailto:{EMAIL}">{icon(2)}<span>{labels[3]}</span>{ARROW}</a></aside><article class="document">{''.join(articles)}</article></div><div class="document-bottom"><a class="back-link" href="{link('home')}">← {'Back to home' if en else '返回首页'}</a><a class="back-link" href="#top">{'Back to top' if en else '返回顶部'} ↑</a></div>'''
    description = COPY['home',lang].split('\n\n')[2] if slug == 'home' else labels[idx] + ' · EaseFlow'
    footer_nav = ''.join(f'<a href="{link(s)}">{labels[i]}</a>' for i,s in enumerate(SLUGS[1:],1))
    doc = f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{html.escape(description,quote=True)}"><meta name="theme-color" content="#f7f6f2"><title>{labels[idx]} · EaseFlow</title><link rel="icon" href="{base}assets/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" href="{base}assets/favicon-32x32.png" type="image/png" sizes="32x32"><link rel="icon" href="{base}assets/favicon-16x16.png" type="image/png" sizes="16x16"><link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png" sizes="180x180"><link rel="stylesheet" href="{base}assets/styles.css"><link rel="alternate" hreflang="zh-Hans" href="{link(slug,'zh-Hans')}"><link rel="alternate" hreflang="en" href="{link(slug,'en')}"><script src="{base}assets/site.js" defer></script></head>
<body id="top" class="page-{slug}"><a class="skip-link" href="#main">{'Skip to content' if en else '跳至正文'}</a><header class="site-header"><div class="header-inner"><a class="brand" href="{link('home')}" aria-label="EaseFlow · {labels[0]}">{logo}<span>EaseFlow</span></a><nav class="primary-nav" aria-label="{'Main navigation' if en else '主导航'}">{nav}</nav><nav class="language-switch" aria-label="{'Website language' if en else '网站语言'}">{switch}</nav></div></header><main id="main" class="shell">{content}</main><footer class="site-footer"><div class="footer-inner"><a class="brand footer-brand" href="{link('home')}">{logo}<span>EaseFlow</span></a><nav aria-label="{'Footer navigation' if en else '页脚导航'}">{footer_nav}</nav><a class="footer-email" href="mailto:{EMAIL}">{EMAIL}</a></div></footer></body></html>'''
    dest = OUT / location / 'index.html'; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(doc)

# dist is disposable build output. Rebuild it cleanly so stale files cannot ship.
if OUT.is_symlink():
    raise SystemExit('Refusing to build into a symlinked dist directory.')
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT/'assets', OUT/'assets', ignore=shutil.ignore_patterns(
    '.*', '__pycache__', '*.pyc', '*.tmp', '*.log', '*.bak'
))
for slug in SLUGS:
    for lang in LABELS: page(slug,lang)
(OUT/'.nojekyll').touch()
print('Built 8 static pages in dist/ from the approved copy.')
