#!/usr/bin/env python3
"""Validate the release artifact and URLs under the GitHub Pages project path.

Uses only Python's standard library. No browser, server, or network is required.
"""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
EMAIL = 'easeflowsupport@163.com'
PAGES = ['', 'privacy/', 'terms/', 'support/']
ASSETS = {
    'AppIcon-1024.png', 'brand-icon-96.png', 'apple-touch-icon.png',
    'favicon.ico', 'favicon-16x16.png', 'favicon-32x32.png',
    'favicon-48x48.png', 'flow.svg', 'styles.css', 'site.js',
}


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.text, self.switches = [], set(), [], {}
        self.lang, self.headings, self.icons, self.favicons = '', 0, [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        if tag == 'h1':
            self.headings += 1
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate ID: {a["id"]}'
            self.ids.add(a['id'])
        for key in ('href', 'src'):
            if key in a:
                self.links.append(a[key])
        if tag == 'a' and a.get('lang') in ('en', 'zh-Hans'):
            self.switches[a['lang']] = a['href']
        if tag == 'img' and 'brand-icon' in a.get('class', '').split():
            self.icons.append(a['src'])
        if tag == 'link' and a.get('rel') in ('icon', 'apple-touch-icon'):
            self.favicons.append(a['href'])

    def handle_data(self, text):
        self.text.append(text)


def compact(text):
    return re.sub(r'\s+', '', text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-path', default='/EaseFlow-Website/')
    args = parser.parse_args()
    base = args.base_path
    assert base.startswith('/') and base.endswith('/') and '..' not in base
    origin = 'https://gnesiiy.github.io'
    expected = {f'{prefix}{page}index.html' for prefix in ('', 'en/') for page in PAGES}
    expected |= {f'assets/{name}' for name in ASSETS} | {'.nojekyll'}
    actual = {p.relative_to(DIST).as_posix() for p in DIST.rglob('*') if p.is_file()}
    assert actual == expected, f'Unexpected/missing artifact files: {actual ^ expected}'
    assert not any(p.is_symlink() for p in DIST.rglob('*')), 'Symlinks in artifact'
    docs = {name: Document((DIST / name).read_text(encoding='utf-8'))
            for name in sorted(expected) if name.endswith('.html')}
    source = (ROOT / 'EaseFlow_Website_Copy_zh_en.md').read_text(encoding='utf-8')
    blocks = re.split(r'^# 0[1-4] .*$', source, flags=re.M)[1:]
    assert len(blocks) == 4
    checked = 0
    for index, route in enumerate(PAGES):
        parts = re.split(r'^## (zh-Hans|en)\s*$', blocks[index], flags=re.M)
        for lang, prefix in [('zh-Hans', ''), ('en', 'en/')]:
            name = f'{prefix}{route}index.html'
            doc = docs[name]
            page_url = origin + base + prefix + route
            assert doc.lang == lang and doc.headings == 1, name
            assert len(doc.icons) == (3 if index == 0 else 2), name
            assert all(x.endswith('/assets/brand-icon-96.png') for x in doc.icons), name
            assert len(doc.favicons) == 4, name
            text = compact(''.join(doc.text))
            assert not re.search(r'\[[^\]]+\]|PetDrinkDiary', text), name
            raw = parts[parts.index(lang) + 1]
            for line in raw.splitlines():
                if not line.strip() or line == '---':
                    continue
                line = re.sub(r'^(#{1,4} |- )', '', line).replace('**', '')
                for fragment in (line.split(' — ') if index == 0 else [line]):
                    assert compact(fragment) in text, f'Missing copy in {name}: {fragment}'
            if route == 'privacy/':
                assert 'PanXinYue' in text, name
            if route in ('privacy/', 'terms/'):
                assert compact('October 2026' if lang == 'en' else '2026 年 10 月') in text, name
            assert set(doc.switches) == {'en', 'zh-Hans'}, name
            for target_lang, href in doc.switches.items():
                target_prefix = 'en/' if target_lang == 'en' else ''
                assert urljoin(page_url, href) == origin + base + target_prefix + route, name
            assert f'mailto:{EMAIL}' in doc.links, name
            for href in doc.links:
                if href.startswith('mailto:'):
                    assert href == f'mailto:{EMAIL}', name
                    continue
                assert not urlsplit(href).scheme and not href.startswith('/'), (name, href)
                target = urlsplit(urljoin(page_url, href))
                assert target.netloc == 'gnesiiy.github.io' and target.path.startswith(base), (name, href)
                relative = unquote(target.path[len(base):])
                if relative.endswith('/') or not relative:
                    relative += 'index.html'
                assert relative in expected, (name, href)
                if target.fragment:
                    assert relative in docs and unquote(target.fragment) in docs[relative].ids, (name, href)
                checked += 1
    print(f'PASS: 8 bilingual pages; approved copy, language URLs, icons and email verified.')
    print(f'PASS: {checked} links/assets/anchors under {base}; {len(actual)} release files, no extra artifacts.')


if __name__ == '__main__':
    main()
