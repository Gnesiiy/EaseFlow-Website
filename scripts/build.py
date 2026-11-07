#!/usr/bin/env python3
"""Build the nine-language static site from copy/*.md and copy/release*.json."""
from pathlib import Path
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
EMAIL = 'easeflowsupport@163.com'
SITE_URL = 'https://gnesiiy.github.io/EaseFlow-Website/'
SLUGS = ('home', 'privacy', 'terms', 'support')
ROUTES = {
    'zh-Hans': '', 'zh-Hant': 'zh-Hant/', 'en-US': 'en/',
    'en-GB': 'en-GB/', 'ja': 'ja/', 'ko': 'ko/',
    'es': 'es/', 'fr': 'fr/', 'de': 'de/',
}
NAMES = {
    'zh-Hans': '简体中文', 'zh-Hant': '繁體中文', 'en-US': 'English (US)',
    'en-GB': 'English (UK)', 'ja': '日本語', 'ko': '한국어',
    'es': 'Español', 'fr': 'Français', 'de': 'Deutsch',
}
UI = {
    'zh-Hans': (['首页','隐私政策','使用条款','帮助与支持'], '返回首页','返回顶部','本页内容','跳至正文','主导航','页脚导航','网站语言','选择网站语言'),
    'zh-Hant': (['首頁','隱私權政策','使用條款','協助與支援'], '返回首頁','返回頂部','本頁內容','跳至內容','主要導覽','頁尾導覽','網站語言','選擇網站語言'),
    'en-US': (['Home','Privacy Policy','Terms of Use','Help & Support'], 'Back to home','Back to top','On this page','Skip to content','Main navigation','Footer navigation','Website language','Choose website language'),
    'en-GB': (['Home','Privacy Policy','Terms of Use','Help & Support'], 'Back to home','Back to top','On this page','Skip to content','Main navigation','Footer navigation','Website language','Choose website language'),
    'ja': (['ホーム','プライバシーポリシー','利用規約','ヘルプとサポート'], 'ホームに戻る','ページ上部へ','このページの内容','本文へ移動','メインナビゲーション','フッターナビゲーション','サイトの言語','サイトの言語を選択'),
    'ko': (['홈','개인정보 처리방침','이용 약관','도움말 및 지원'], '홈으로','맨 위로','이 페이지의 내용','본문으로 건너뛰기','기본 탐색','바닥글 탐색','웹사이트 언어','웹사이트 언어 선택'),
    'es': (['Inicio','Política de privacidad','Condiciones de uso','Ayuda y asistencia'], 'Volver al inicio','Volver arriba','En esta página','Saltar al contenido','Navegación principal','Navegación del pie','Idioma del sitio','Elegir idioma del sitio'),
    'fr': (['Accueil','Politique de confidentialité','Conditions d’utilisation','Aide et assistance'], 'Retour à l’accueil','Retour en haut','Sur cette page','Aller au contenu','Navigation principale','Navigation de pied de page','Langue du site','Choisir la langue du site'),
    'de': (['Start','Datenschutzrichtlinie','Nutzungsbedingungen','Hilfe & Support'], 'Zur Startseite','Nach oben','Auf dieser Seite','Zum Inhalt springen','Hauptnavigation','Fußnavigation','Website-Sprache','Website-Sprache wählen'),
}
# One release state controls every rendered version notice. Templates retain each
# locale's and page's precise scope; no page hard-codes the publication status.
RELEASE_NOTES = json.loads((ROOT / 'copy/release_notes.json').read_text(encoding='utf-8'))
assert set(RELEASE_NOTES) == set(ROUTES) and all(len(value) == 4 for value in RELEASE_NOTES.values())
RELEASE = json.loads((ROOT / 'copy/release.json').read_text(encoding='utf-8'))
assert set(RELEASE) == {'current_app_store_version','upcoming_version'}
assert re.fullmatch(r'v\d+\.\d+', RELEASE['current_app_store_version'])
assert RELEASE['upcoming_version'] is None or (
    re.fullmatch(r'v\d+\.\d+', RELEASE['upcoming_version'])
    and RELEASE['upcoming_version'] != RELEASE['current_app_store_version']
)

def release_note(lang, slug):
    templates = RELEASE_NOTES[lang]
    upcoming = RELEASE['upcoming_version']
    template = templates[{'privacy':0,'terms':1,'support':2}[slug]] if upcoming else templates[3]
    return template.format(current=RELEASE['current_app_store_version'], next=upcoming)

def load_copy(lang):
    source = (ROOT / 'copy' / f'{lang}.md').read_text(encoding='utf-8')
    parts = re.split(r'^<!-- (home|privacy|terms|support) -->\s*$', source, flags=re.M)
    assert not parts[0].strip() and len(parts) == 9, f'Missing page in {lang}'
    pages = {parts[i]: parts[i+1].strip() for i in range(1,len(parts),2)}
    assert tuple(pages) == SLUGS and all(pages.values()), lang
    for slug in SLUGS:
        assert pages[slug].startswith('# EaseFlow') or pages[slug].startswith('# '), (lang,slug)
        assert pages[slug].count('{{release_note}}') == (0 if slug == 'home' else 1), (lang,slug)
        if slug != 'home': pages[slug] = pages[slug].replace('{{release_note}}', release_note(lang,slug))
    return pages
COPY = {lang: load_copy(lang) for lang in ROUTES}

def esc(value): return html.escape(value, quote=True)
def inline(value):
    value = esc(value)
    value = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)
    return value.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')
def markdown(value):
    out=[]; listing=False
    for line in value.splitlines():
        if not line.strip(): continue
        if line.startswith('- '):
            if not listing: out.append('<ul>'); listing=True
            out.append('<li>'+inline(line[2:])+'</li>'); continue
        if listing: out.append('</ul>'); listing=False
        match=re.match(r'^(#{1,4}) (.*)',line)
        if match: out.append(f'<h{len(match[1])}>{inline(match[2])}</h{len(match[1])}>')
        else: out.append('<p>'+inline(line)+'</p>')
    if listing: out.append('</ul>')
    return '\n'.join(out)

ICONS = [
    '<path d="M12 3 4.5 6v5.5c0 4.2 3.2 7.3 7.5 9.5 4.3-2.2 7.5-5.3 7.5-9.5V6L12 3Z"/><path d="m8.5 12 2.3 2.3 4.7-4.8"/>',
    '<path d="M7 3h7l4 4v14H6V3h1Z"/><path d="M14 3v5h4M9 12h6M9 16h5"/>',
    '<path d="M5 13v-3a7 7 0 0 1 14 0v3M5 11H3v6h4v-6H5Zm14 0h2v6h-4v-6h2ZM19 17v2l-5 2h-3"/>'
]
def icon(i): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[i]}</svg>'
ARROW='<span aria-hidden="true">↗</span>'

def page(slug, lang):
    ui=UI[lang]; labels=ui[0]; idx=SLUGS.index(slug)
    location=Path(ROUTES[lang]) / (slug if slug!='home' else '')
    base='../'*len(location.parts) or './'
    def link(target_slug,target_lang=lang):
        return base+ROUTES[target_lang]+(target_slug+'/' if target_slug!='home' else '')
    def absolute(target_slug,target_lang=lang):
        return SITE_URL+ROUTES[target_lang]+(target_slug+'/' if target_slug!='home' else '')
    logo=f'<img class="brand-icon" src="{base}assets/brand-icon-96.png" alt="" width="37" height="37">'
    raw=COPY[lang][slug]; lines=raw.splitlines(); title=lines[0][2:]; body='\n'.join(lines[1:]).strip()
    if slug=='home':
        blocks=body.split('\n\n')
        assert len(blocks)==5, (lang,slug,len(blocks))
        tagline=blocks[0].strip('*'); intro=blocks[1]; explore=blocks[2].strip('*')
        if lang in ('zh-Hans','zh-Hant'):
            segments=re.findall(r'.*?[，。]',tagline)
            tagline_html=''.join('<span class="tagline-line">'+esc(t)+'</span>' for t in segments) if ''.join(segments)==tagline else esc(tagline)
        else: tagline_html=esc(tagline)
        cards=[]
        for i,line in enumerate(blocks[3].splitlines()):
            match=re.fullmatch(r'- \*\*(.*?)\*\* — (.*)',line); assert match, (lang,line)
            cards.append(f'<a class="entry-card" href="{link(SLUGS[i+1])}"><div class="card-top"><span class="icon">{icon(i)}</span><span class="card-number">0{i+1}</span></div><h3>{esc(match[1])} {ARROW}</h3><p>{esc(match[2])}</p></a>')
        content=f'<section class="hero" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow">EaseFlow</p><h1 id="hero-title">{tagline_html}</h1><p class="hero-description">{inline(intro)}</p><a class="text-link" href="#explore">{esc(explore)}<span aria-hidden="true">↓</span></a></div><div class="hero-art" aria-hidden="true"><img src="{base}assets/flow.svg" alt="" width="560" height="470"><div class="art-caption"><span class="small-mark">{logo}</span><span>EaseFlow</span><span class="art-line"></span></div></div></section><section id="explore" class="explore"><div class="section-heading"><h2>{esc(explore)}</h2><span aria-hidden="true">01 — 03</span></div><div class="entry-grid">{"".join(cards)}</div></section><div class="home-contact"><span class="contact-dot" aria-hidden="true"></span>{markdown(blocks[4])}{ARROW}</div>'
        description=intro
    else:
        sections=re.split(r'^### (.*)$',body,flags=re.M)
        prelude=sections[0].strip(); toc=[]; articles=[]
        assert len(sections)>1 and len(sections)%2==1, (lang,slug)
        for j in range(1,len(sections),2):
            heading,text=sections[j],sections[j+1].strip(); n=(j+1)//2; anchor=f'section-{n}'
            toc.append(f'<a href="#{anchor}">{esc(heading)}</a>')
            if slug=='support' and n==1:
                faq=re.split(r'^#### (.*)$',text,flags=re.M)
                assert not faq[0].strip() and len(faq)==25, (lang,slug,len(faq))
                section_html=''.join(f'<details><summary>{inline(faq[k])}<span aria-hidden="true">+</span></summary><div class="answer">{markdown(faq[k+1])}</div></details>' for k in range(1,len(faq),2))
            else: section_html=markdown(text)
            articles.append(f'<section class="document-section" id="{anchor}"><h2>{inline(heading)}</h2>{section_html}</section>')
        content=f'<div class="page-intro"><a class="back-link" href="{link("home")}"><span aria-hidden="true">←</span> {esc(ui[1])}</a><div class="page-heading"><span class="icon">{icon(idx-1)}</span></div><h1>{esc(title)}</h1><div class="prelude">{markdown(prelude)}</div></div><div class="document-layout"><aside class="contents"><p>{esc(ui[3])}</p><nav aria-label="{esc(ui[3])}">{"".join(toc)}</nav><a class="sidebar-contact" href="mailto:{EMAIL}">{icon(2)}<span>{esc(labels[3])}</span>{ARROW}</a></aside><article class="document">{"".join(articles)}</article></div><div class="document-bottom"><a class="back-link" href="{link("home")}">← {esc(ui[1])}</a><a class="back-link" href="#top">{esc(ui[2])} ↑</a></div>'
        seo_lines = [line.strip().strip('*') for line in (prelude if slug=='support' else sections[2]).splitlines() if line.strip()]
        description = f'{title}. ' + ' '.join(seo_lines[:2])
    description=re.sub(r'\*','',description).strip()[:160]
    current_page='aria-current="page"'
    current_lang='aria-current="true"'
    nav=''.join(f'<a href="{link(s)}" {current_page if s==slug else ""}>{esc(labels[i])}</a>' for i,s in enumerate(SLUGS[1:],1))
    options=''.join(f'<a lang="{l}" hreflang="{l}" aria-label="{esc(NAMES[l])}" href="{link(slug,l)}" {current_lang if l==lang else ""}>{esc(NAMES[l])}</a>' for l in ROUTES)
    alternates=''.join(f'<link rel="alternate" hreflang="{l}" href="{absolute(slug,l)}">' for l in ROUTES)
    alternates+=f'<link rel="alternate" hreflang="x-default" href="{absolute(slug,"zh-Hans")}">'
    footer=''.join(f'<a href="{link(s)}">{esc(labels[i])}</a>' for i,s in enumerate(SLUGS[1:],1))
    doc=f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#f7f6f2"><title>{esc(labels[0] if slug=="home" else title)} · EaseFlow</title><link rel="canonical" href="{absolute(slug)}">{alternates}<link rel="icon" href="{base}assets/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" href="{base}assets/favicon-32x32.png" type="image/png" sizes="32x32"><link rel="icon" href="{base}assets/favicon-16x16.png" type="image/png" sizes="16x16"><link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png" sizes="180x180"><link rel="stylesheet" href="{base}assets/styles.css?v=9lang3"><script src="{base}assets/site.js?v=9lang3" defer></script></head>
<body id="top" class="page-{slug}"><a class="skip-link" href="#main">{esc(ui[4])}</a><header class="site-header"><div class="header-inner"><a class="brand" href="{link('home')}" aria-label="EaseFlow · {esc(labels[0])}">{logo}<span>EaseFlow</span></a><nav class="primary-nav" aria-label="{esc(ui[5])}">{nav}</nav><details class="language-switch"><summary aria-label="{esc(ui[8])}"><span class="language-glyph" aria-hidden="true">文</span><span>{esc(NAMES[lang])}</span><span class="language-chevron" aria-hidden="true">⌄</span></summary><nav class="language-options" aria-label="{esc(ui[7])}">{options}</nav></details></div></header><main id="main" class="shell">{content}</main><footer class="site-footer"><div class="footer-inner"><a class="brand footer-brand" href="{link('home')}">{logo}<span>EaseFlow</span></a><nav aria-label="{esc(ui[6])}">{footer}</nav><a class="footer-email" href="mailto:{EMAIL}">{EMAIL}</a></div></footer></body></html>'''
    dest=OUT/location/'index.html'; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(doc,encoding='utf-8')

if OUT.is_symlink(): raise SystemExit('Refusing symlinked dist directory')
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT/'assets',OUT/'assets',ignore=shutil.ignore_patterns('.*','__pycache__','*.pyc','*.tmp','*.log','*.bak'))
for slug in SLUGS:
    for lang in ROUTES: page(slug,lang)
(OUT/'.nojekyll').touch()
print('Built 36 static pages across 9 languages in dist/.')
