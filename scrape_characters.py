#!/usr/bin/env python3
"""Scrape character (キャラ) data from GameWith for Gジェネエターナル"""
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
    """Collect all character detail page links from the list page."""
    soup = get_soup(LIST_URL)
    tables = soup.find_all('table')
    links = []
    seen = set()
    
    # Tables with character links: typically indices 1,3,5 (UR, SSR, SR)
    # But let's be smart: find tables that contain links to /ggene-eternal/NNNNN
    # and whose cells have short text (character names, not articles)
    for t in tables:
        anchors = t.find_all('a', href=re.compile(r'/ggene-eternal/\d+$'))
        for a in anchors:
            href = a.get('href', '')
            text = a.get_text(strip=True)
            # Skip navigation links
            if '一覧' in text or '関連' in text or not text:
                continue
            # Skip if text contains img tag remnants or is too long (article links)
            if len(text) > 40 or '<img' in text.lower():
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
    
    for t in tables:
        rows = t.find_all('tr')
        flat = t.get_text(' ', strip=True)
        
        # Basic info table: has レアリティ or レア + タイプ
        if ('タイプ' in flat and ('レア' in flat or 'UR' in flat or 'SSR' in flat or 'SR' in flat)) and len(rows) <= 8:
            for row in rows:
                cells = row.find_all(['th', 'td'])
                cell_texts = [c.get_text(strip=True) for c in cells]
                
                for i, ct in enumerate(cell_texts):
                    if 'レア' in ct and i + 1 < len(cell_texts):
                        # Check for rarity images
                        next_cell = cells[i+1] if i+1 < len(cells) else None
                        if next_cell:
                            img = next_cell.find('img')
                            if img and img.get('alt'):
                                data['rarity'] = img['alt'].strip()
                            elif cell_texts[i+1]:
                                data['rarity'] = cell_texts[i+1]
                    
                    if ct == 'タイプ':
                        # Type might be in image alt
                        next_cell = cells[i+1] if i+1 < len(cells) else None
                        if next_cell:
                            img = next_cell.find('img')
                            if img and img.get('alt'):
                                data['chara_type'] = img['alt'].strip()
                            elif i+1 < len(cell_texts):
                                data['chara_type'] = cell_texts[i+1]
                    
                    if '入手方法' in ct and i + 1 < len(cell_texts):
                        data['obtain_method'] = cell_texts[i+1] if i+1 < len(cell_texts) else ''
                    
                    if '支援' in ct and ct != '支援' and i + 1 < len(cell_texts):
                        pass  # handled by type
                
                # Check for type in cell text directly
                for ct in cell_texts:
                    if ct in ['攻撃', '耐久', '支援']:
                        data['chara_type'] = ct
        
        # Series table: single row with series name
        if len(rows) == 1 and len(rows[0].find_all(['th', 'td'])) == 1:
            text = rows[0].get_text(strip=True)
            if 'ガンダム' in text or 'GENERATION' in text or 'シリーズ' in text or '∀' in text or '機動' in text:
                data['series'] = text
        
        # Stats table: has 戦闘力 + 射撃値/格闘値 etc
        if '射撃値' in flat and '格闘値' in flat and len(rows) <= 5:
            stats = {}
            for row in rows:
                cells = row.find_all(['th', 'td'])
                cell_texts = [c.get_text(strip=True) for c in cells]
                for i, ct in enumerate(cell_texts):
                    # Extract combat power from first cell like "戦闘力3739"
                    m = re.match(r'戦闘力(\d+)', ct)
                    if m:
                        stats['combat_power'] = int(m.group(1))
                    
                    stat_map = {
                        '射撃値': 'shooting',
                        '格闘値': 'melee', 
                        '覚醒値': 'awakening',
                        '守備力': 'defense',
                        '反応値': 'reaction',
                        '機動力': 'mobility'
                    }
                    if ct in stat_map and i + 1 < len(cell_texts):
                        try:
                            stats[stat_map[ct]] = int(cell_texts[i+1])
                        except ValueError:
                            stats[stat_map[ct]] = cell_texts[i+1]
            
            if stats:
                data['stats'] = stats
        
        # Skills table: alternating name(SP:N) and effect rows
        if re.search(r'SP:\d+', flat) and '射撃値' not in flat:
            skills = []
            i = 0
            while i < len(rows) - 1:
                name_text = rows[i].get_text(strip=True)
                effect_text = rows[i+1].get_text(strip=True) if i+1 < len(rows) else ''
                if re.search(r'SP:\d+', name_text):
                    # Extract SP cost
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
            if skills:
                data['skills'] = skills
        
        # Abilities table: alternating name and effect, no SP
        if ('Lv' in flat or 'アビリティ' in flat) and 'SP:' not in flat and '射撃値' not in flat and '一覧' not in flat:
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
            if abilities:
                data['abilities'] = abilities
    
    # Extract name from title if we got a better one
    title = soup.find('title')
    if title:
        title_text = title.get_text()
        m = re.match(r'【Gジェネエターナル】(.+?)の評価', title_text)
        if m:
            data['name'] = m.group(1).strip()
    
    # Try to get rarity from title if not found
    if 'rarity' not in data:
        if title:
            title_text = title.get_text()
            for r in ['UR', 'SSR', 'SR', 'R']:
                if f'({r}/' in title_text or f'({r})' in title_text:
                    data['rarity'] = r
                    break
    
    # Try to get type from title
    if 'chara_type' not in data:
        if title:
            title_text = title.get_text()
            for ct in ['攻撃', '耐久', '支援']:
                if f'/{ct})' in title_text:
                    data['chara_type'] = ct
                    break
    
    return data


def main():
    print("Collecting character links...")
    links = collect_chara_links()
    print(f"Found {len(links)} character links")
    
    characters = []
    for i, link in enumerate(links):
        try:
            print(f"[{i+1}/{len(links)}] Scraping {link['name']}...", end=' ', flush=True)
            chara = parse_chara_detail(link['url'], link['name'])
            characters.append(chara)
            print(f"OK - stats={'stats' in chara}, skills={len(chara.get('skills',[]))}, abilities={len(chara.get('abilities',[]))}")
            time.sleep(0.5)
        except Exception as e:
            print(f"ERROR: {e}")
            characters.append({'name': link['name'], 'source_url': link['url'], 'error': str(e)})
    
    outpath = '/Users/RH/Documents/5.File/5.Dev/GGeneDB/public/characters.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone! Saved {len(characters)} characters to {outpath}")
    
    # Summary
    has_stats = sum(1 for c in characters if 'stats' in c)
    has_skills = sum(1 for c in characters if c.get('skills'))
    has_abilities = sum(1 for c in characters if c.get('abilities'))
    has_rarity = sum(1 for c in characters if c.get('rarity'))
    print(f"Stats: {has_stats}, Skills: {has_skills}, Abilities: {has_abilities}, Rarity: {has_rarity}")

if __name__ == '__main__':
    main()
