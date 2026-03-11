#!/usr/bin/env python3
"""Scrape character (キャラ) data from GameWith for Gジェネエターナル - v2 fixed"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import sys

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

LIST_URL = 'https://gamewith.jp/ggene-eternal/496163'

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')

def collect_chara_links():
    """Collect character detail page links from data tables (10+ links), skip nav tables."""
    soup = get_soup(LIST_URL)

    links = []
    seen = set()
    skip_keywords = ['一覧', '関連', 'おすすめ', 'ランキング', 'やり方', '編成',
                     '攻略', '掲示板', '招待', '周回', 'リセマラ', '最強',
                     '効率', '毎日', 'スカウト', '開発', '解体', '金策',
                     '戦闘力の上げ方', 'レベル上げ', '鹵獲', '序盤']

    tables = soup.find_all('table')
    for t in tables:
        anchors = t.find_all('a', href=re.compile(r'/ggene-eternal/\d+$'))
        # Data tables have 10+ character links; nav/article tables have fewer
        if len(anchors) < 10:
            continue

        for a in anchors:
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if not text or len(text) > 40:
                continue
            if any(kw in text for kw in skip_keywords):
                continue
            full_url = href if href.startswith('http') else 'https://gamewith.jp' + href
            if full_url not in seen:
                seen.add(full_url)
                links.append({'name': text, 'url': full_url})

    return links

def parse_chara_detail(url, name_hint):
    """Parse a character detail page."""
    soup = get_soup(url)
    data = {'name': name_hint, 'source_url': url}

    tables = soup.find_all('table')

    # Extract name from title first
    title = soup.find('title')
    if title:
        title_text = title.get_text()
        m = re.match(r'【Gジェネエターナル】(.+?)の評価', title_text)
        if m:
            raw_name = m.group(1).strip()
            # Clean name: remove (UR/攻撃) suffix
            raw_name = re.sub(r'\((?:UR|SSR|SR|R)/(?:攻撃|耐久|支援)\)', '', raw_name).strip()
            data['name'] = raw_name

        # Extract rarity and type from title
        for r in ['UR', 'SSR', 'SR', 'R']:
            if f'({r}/' in title_text or f'/{r})' in title_text:
                data['rarity'] = r
                break
        for ct in ['攻撃', '耐久', '支援']:
            if f'/{ct})' in title_text:
                data['chara_type'] = ct
                break

    stats_found = False

    for t in tables:
        rows = t.find_all('tr')
        flat = t.get_text(' ', strip=True)

        # Basic info table: has タイプ + レア
        if ('タイプ' in flat and ('レア' in flat or 'UR' in flat or 'SSR' in flat)) and len(rows) <= 8:
            for row in rows:
                cells = row.find_all(['th', 'td'])
                cell_texts = [c.get_text(strip=True) for c in cells]

                for i, ct in enumerate(cell_texts):
                    if 'レア' in ct and i + 1 < len(cell_texts):
                        next_cell = cells[i+1] if i+1 < len(cells) else None
                        if next_cell:
                            img = next_cell.find('img')
                            if img and img.get('alt'):
                                data['rarity'] = img['alt'].strip()
                            elif cell_texts[i+1] and cell_texts[i+1] in ['UR','SSR','SR','R']:
                                data['rarity'] = cell_texts[i+1]

                    if '入手方法' in ct and i + 1 < len(cell_texts):
                        data['obtain_method'] = cell_texts[i+1]

                    if ct == 'タイプ':
                        next_cell = cells[i+1] if i+1 < len(cells) else None
                        if next_cell:
                            img = next_cell.find('img')
                            if img and img.get('alt'):
                                data['chara_type'] = img['alt'].strip()
                            elif i+1 < len(cell_texts) and cell_texts[i+1] in ['攻撃','耐久','支援']:
                                data['chara_type'] = cell_texts[i+1]

                # Direct type text in cells
                for ct in cell_texts:
                    if ct in ['攻撃', '耐久', '支援']:
                        data['chara_type'] = ct

        # Series table: single-row table with series name
        if len(rows) == 1 and len(rows[0].find_all(['th', 'td'])) == 1:
            text = rows[0].get_text(strip=True)
            if 'ガンダム' in text or 'GENERATION' in text or 'シリーズ' in text or '∀' in text or '機動' in text:
                data['series'] = text

        # Stats table: has 射撃値 AND 守備力 (both must be present to avoid false positives)
        # Must have actual numeric values (th-td pairs)
        if '射撃値' in flat and '守備力' in flat and len(rows) <= 5:
            stats = {}
            has_numeric = False
            for row in rows:
                cells = row.find_all(['th', 'td'])
                # Process th-td pairs
                i = 0
                while i < len(cells):
                    cell = cells[i]
                    txt = cell.get_text(strip=True)

                    # Combat power: td with 戦闘力NNNN
                    m = re.match(r'戦闘力(\d+)', txt)
                    if m:
                        stats['combat_power'] = int(m.group(1))
                        has_numeric = True
                        i += 1
                        continue

                    stat_map = {
                        '射撃値': 'shooting', '格闘値': 'melee',
                        '覚醒値': 'awakening', '守備力': 'defense',
                        '反応値': 'reaction', '機動力': 'mobility'
                    }

                    if txt in stat_map and i + 1 < len(cells):
                        val_text = cells[i+1].get_text(strip=True)
                        try:
                            stats[stat_map[txt]] = int(val_text)
                            has_numeric = True
                        except ValueError:
                            pass  # Skip non-numeric values
                        i += 2
                        continue

                    i += 1

            if stats and has_numeric and not stats_found:
                data['stats'] = stats
                stats_found = True

        # Skills table: has SP:N pattern, NOT in stats area
        if re.search(r'SP:\d+', flat) and '射撃値' not in flat and '守備力' not in flat:
            skills = []
            i = 0
            while i < len(rows) - 1:
                name_text = rows[i].get_text(strip=True)
                effect_text = rows[i+1].get_text(strip=True) if i+1 < len(rows) else ''
                if re.search(r'SP:\d+', name_text):
                    sp_match = re.search(r'SP:(\d+)', name_text)
                    sp_cost = int(sp_match.group(1)) if sp_match else None
                    skills.append({
                        'name': name_text,
                        'effect': effect_text,
                        'sp_cost': sp_cost
                    })
                    i += 2
                else:
                    i += 1
            if skills and 'skills' not in data:
                data['skills'] = skills

        # Abilities table: has Lv or アビリティ, no SP, no stats
        if ('Lv' in flat or 'アビリティ' in flat) and 'SP:' not in flat and '射撃値' not in flat and '一覧' not in flat and '守備力' not in flat:
            abilities = []
            i = 0
            while i < len(rows) - 1:
                name_text = rows[i].get_text(strip=True)
                effect_text = rows[i+1].get_text(strip=True) if i+1 < len(rows) else ''
                if 'Lv' in name_text or 'EXキャラアビリティ' in name_text:
                    abilities.append({
                        'name': name_text,
                        'effect': effect_text
                    })
                    i += 2
                else:
                    i += 1
            if abilities and 'abilities' not in data:
                data['abilities'] = abilities

    return data


def main():
    print("Collecting character links...")
    links = collect_chara_links()
    print(f"Found {len(links)} character links")

    if not links:
        print("ERROR: No links found!")
        sys.exit(1)

    characters = []
    for i, link in enumerate(links):
        try:
            print(f"[{i+1}/{len(links)}] Scraping {link['name']}...", end=' ', flush=True)
            chara = parse_chara_detail(link['url'], link['name'])
            characters.append(chara)
            s = chara.get('stats', {})
            print(f"OK - rarity={chara.get('rarity','?')}, stats={len(s)}, skills={len(chara.get('skills',[]))}, abilities={len(chara.get('abilities',[]))}")
            time.sleep(0.5)
        except Exception as e:
            print(f"ERROR: {e}")
            characters.append({'name': link['name'], 'source_url': link['url'], 'error': str(e)})

    outpath = '/Users/RH/Documents/5.File/5.Dev/GGeneDB/public/characters.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Saved {len(characters)} characters to {outpath}")

    has_stats = sum(1 for c in characters if c.get('stats'))
    has_skills = sum(1 for c in characters if c.get('skills'))
    has_abilities = sum(1 for c in characters if c.get('abilities'))
    has_rarity = sum(1 for c in characters if c.get('rarity'))
    has_series = sum(1 for c in characters if c.get('series'))
    print(f"Stats: {has_stats}, Skills: {has_skills}, Abilities: {has_abilities}, Rarity: {has_rarity}, Series: {has_series}")

if __name__ == '__main__':
    main()
