#!/usr/bin/env python3
"""Validate all 36 localized pages and GitHub Pages project URLs."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
EMAIL='easeflowsupport@163.com'
SITE_URL='https://gnesiiy.github.io/EaseFlow-Website/'
ROUTES={'zh-Hans':'','zh-Hant':'zh-Hant/','en-US':'en/','en-GB':'en-GB/','ja':'ja/','ko':'ko/','es':'es/','fr':'fr/','de':'de/'}
PAGES={'home':'','privacy':'privacy/','terms':'terms/','support':'support/'}
ASSETS={'AppIcon-1024.png','brand-icon-96.png','apple-touch-icon.png','favicon.ico','favicon-16x16.png','favicon-32x32.png','favicon-48x48.png','flow.svg','styles.css','site.js'}

class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.lang=None; self.title=''; self.description=''; self.headings=0
        self.links=[]; self.ids=set(); self.text=[]; self.alternates={}; self.canonical=[]
        self.switches={}; self.current=[]; self.icons=[]; self.favicons=[]
        self.details=0; self.summaries=0; self.menu=False; self.menu_label=None
        self._in_title=False; self._in_menu=False
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='html': self.lang=a.get('lang')
        if tag=='title': self._in_title=True
        if tag=='h1': self.headings+=1
        if tag=='details':
            if 'language-switch' in a.get('class','').split(): self.menu=True; self._in_menu=True
            else: self.details+=1
        if tag=='summary':
            if self._in_menu: self.menu_label=a.get('aria-label')
            else: self.summaries+=1
        if tag=='meta' and a.get('name')=='description': self.description=a.get('content','')
        if tag=='link':
            if a.get('rel')=='alternate':
                assert a.get('hreflang') not in self.alternates
                self.alternates[a.get('hreflang')]=a.get('href')
            if a.get('rel')=='canonical': self.canonical.append(a.get('href'))
            if a.get('rel') in ('icon','apple-touch-icon'): self.favicons.append(a.get('href'))
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id {a["id"]}'
            self.ids.add(a['id'])
        for key in ('href','src'):
            if key in a: self.links.append(a[key])
        if tag=='a' and self._in_menu:
            assert a.get('aria-label'), 'Missing language option label'
            assert a.get('lang') not in self.switches
            self.switches[a.get('lang')]=a.get('href')
            if a.get('aria-current')=='true': self.current.append(a.get('lang'))
        if tag=='img' and 'brand-icon' in a.get('class','').split(): self.icons.append(a.get('src'))
    def handle_endtag(self, tag):
        if tag=='title': self._in_title=False
        if tag=='details' and self._in_menu: self._in_menu=False
    def handle_data(self, value):
        if self._in_title: self.title+=value
        self.text.append(value)

def compact(value): return re.sub(r'\s+','',value)
def copy_pages(lang):
    source=(ROOT/'copy'/f'{lang}.md').read_text(encoding='utf-8')
    parts=re.split(r'^<!-- (home|privacy|terms|support) -->\s*$',source,flags=re.M)
    assert len(parts)==9 and not parts[0].strip(), lang
    return {parts[i]:parts[i+1].strip() for i in range(1,len(parts),2)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-path',default='/EaseFlow-Website/')
    args=parser.parse_args(); base=args.base_path
    assert base.startswith('/') and base.endswith('/') and '..' not in base
    origin='https://gnesiiy.github.io'
    expected={f'{prefix}{route}index.html' for prefix in ROUTES.values() for route in PAGES.values()}
    expected|={f'assets/{name}' for name in ASSETS}|{'.nojekyll'}
    actual={p.relative_to(DIST).as_posix() for p in DIST.rglob('*') if p.is_file()}
    assert actual==expected, f'Unexpected/missing output: {actual ^ expected}'
    assert not any(p.is_symlink() for p in DIST.rglob('*'))
    docs={name:Document((DIST/name).read_text(encoding='utf-8')) for name in sorted(expected) if name.endswith('.html')}
    checked=0
    for lang,prefix in ROUTES.items():
        source=copy_pages(lang)
        assert set(source)==set(PAGES)
        assert [len(re.findall(r'^### ',source[s],re.M)) for s in PAGES]==[0,9,8,3], lang
        assert len(re.findall(r'^#### ',source['support'],re.M))==12, lang
        for slug,route in PAGES.items():
            name=f'{prefix}{route}index.html'; doc=docs[name]
            page_url=origin+base+prefix+route
            published=SITE_URL+prefix+route
            assert doc.lang==lang and doc.headings==1 and doc.title.endswith(' · EaseFlow'), name
            if slug!='home': assert doc.title.startswith(source[slug].splitlines()[0][2:]), name
            assert len(doc.description)>len(doc.title) and '{{' not in doc.description, name
            assert doc.canonical==[published], name
            assert doc.menu and doc.menu_label and doc.current==[lang], name
            assert len(doc.icons)==(3 if slug=='home' else 2) and all(x.endswith('/assets/brand-icon-96.png') for x in doc.icons),name
            assert len(doc.favicons)==4, name
            assert set(doc.alternates)==set(ROUTES)|{'x-default'}, name
            assert set(doc.switches)==set(ROUTES), name
            for target_lang,target_prefix in ROUTES.items():
                target=SITE_URL+target_prefix+route
                assert doc.alternates[target_lang]==target, (name,target_lang)
                assert urljoin(page_url,doc.switches[target_lang])==origin+base+target_prefix+route,(name,target_lang)
            assert doc.alternates['x-default']==SITE_URL+route,name
            if slug=='support': assert doc.details==doc.summaries==12,name
            else: assert doc.details==doc.summaries==0,name
            text=compact(''.join(doc.text))
            assert not re.search(r'\{\{[^}]+\}\}|PetDrinkDiary',text),name
            for line in source[slug].splitlines():
                if not line.strip() or line.startswith('<!--'): continue
                line=re.sub(r'^(?:#{1,4}\s+|-\s+)','',line).replace('**','').strip()
                if not line: continue
                fragments=line.split(' — ') if slug=='home' else [line]
                for fragment in fragments:
                    assert compact(fragment) in text, f'Missing localized copy in {name}: {fragment}'
            if slug=='privacy': assert 'PanXinYue' in text,name
            assert f'mailto:{EMAIL}' in doc.links,name
            local_targets=set()
            for href in doc.links:
                if href.startswith('mailto:'):
                    assert href==f'mailto:{EMAIL}',(name,href)
                    continue
                if href.startswith(SITE_URL):
                    assert href in doc.alternates.values() or href in doc.canonical,(name,href)
                    continue
                assert not urlsplit(href).scheme and not href.startswith('/'),(name,href)
                target=urlsplit(urljoin(page_url,href))
                assert target.netloc=='gnesiiy.github.io' and target.path.startswith(base),(name,href)
                relative=unquote(target.path[len(base):])
                if not relative or relative.endswith('/'): relative+='index.html'
                assert relative in expected,(name,href)
                if target.fragment: assert relative in docs and unquote(target.fragment) in docs[relative].ids,(name,href)
                local_targets.add(relative); checked+=1
            assert {f'{prefix}{r}index.html' for r in PAGES.values()} <= local_targets,name
    assert copy_pages('en-US')!=copy_pages('en-GB'),'English locales must be maintained independently'
    print('PASS: 36 pages, 9 complete locale sources, 12 FAQ entries per language, and email.')
    print(f'PASS: language menus, current-page switching, canonical/hreflang, copy, and {checked} local links/assets/anchors under {base}.')

if __name__=='__main__': main()
