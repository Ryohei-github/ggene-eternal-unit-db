#!/usr/bin/env python3
"""Scrape supporter (サポーター) data from GameWith for Gジェネエターナル"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

LIST_URL = 'https://gamewith.jp/ggene-eternal/496120'

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')

def collect_supporter_links():
    """Collect all supporter detail page links."""
    soup = get_soup(LIST_URL)
    tables = soup.find_all('table')
    links = []
    seen = set()
    
    # On supporter list page, the supporter tables come after
    # the shared unit/chara nav tables. We need to identify them.
    # Supporter tables have names like ブライト(WB), フラウ etc.
    # The key is to find tables preceded by headings like "URサポーター一覧" etc.
    
    # Strategy: find all h3/h2 that mention サポーター, then get links from nearby tables
    # Alternative: just get all links and filter by checking if they're supporter pages
    
    # Let's find tables that contain supporter-specific entries
    # Supporters have short names without (EX) suffix typically
    # But safer to use heading context
    
    headings = soup.find_all(['h2', 'h3'])
    supporter_section = False
    supporter_tables = []
    
    for h in headings:
        text = h.get_text(strip=True)
        if 'サポーター' in text and '一覧' in text:
            supporter_section = True
            continue
    
    # Simpler approach: the supporter list page URL itself is the source
    # Tables 0-4 are shared navigation (units, characters)
    # Table 5+ are supporter-specific
    # Let's collect links from table 5 onwards, filtering out nav links
    
    for i, t in enumerate(tables):
        if i < 5:  # Skip shared nav tables
            continue
        anchors = t.find_all('a', href=re.compile(r'/ggene-eternal/\d+$'))
        for a in anchors:
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if not text or '一覧' in text or '関連' in text or len(text) > 50:
                continue
            if '<img' in str(a) and not text:
                continue
            full_url = href if href.startswith('http') else 'https://gamewith.jp' + href
            if full_url not in seen:
                seen.add(full_url)
                links.append({'name': text, 'url': full_url})
    
    return links


def parse_supporter_detail(url, name_hint):
    """Parse a supporter detail page."""
    soup = get_soup(url)
    data = {'name': name_hint, 'source_url': url}
    
    tables = soup.find_all('table')
    
    # Extract name from title
    title = soup.find('title')
    if title:
        title_text = title.get_text()
        m = re.match(r'【Gジェネエターナル】(.+?)の評価', title_text)
        if m:
            data['name'] = m.group(1).strip()
    
    for t in tables:
        rows = t.find_all('tr')
        flat = t.get_text(' ', strip=True)
        
        # Basic info: レア度 + HP + 攻撃力
        if 'レア度' in flat and 'HP' in flat and len(rows) <= 6:
            for row in rows:
                cells = row.find_all(['th', 'td'])
                cell_texts = [c.get_text(strip=True) for c in cells]
                
                for i, ct in enumerate(cell_texts):
                    if 'レア' in ct:
                        next_cell = cells[i+1] if i+1 < len(cells) else None
                        if next_cell:
                            img = next_cell.find('img')
                            if img and img.get('alt'):
                                data['rarity'] = img['alt'].strip()
                            elif i+1 < len(cell_texts) and cell_texts[i+1]:
                                data['rarity'] = cell_texts[i+1]
                    
                    if ct == 'HP' and i+1 < len(cell_texts):
                        try:
                            data['hp'] = int(cell_texts[i+1])
                        except ValueError:
                            data['hp'] = cell_texts[i+1]
                    
                    if ct == '攻撃力' and i+1 < len(cell_texts):
                        try:
                            data['attack'] = int(cell_texts[i+1])
                        except ValueError:
                            data['attack'] = cell_texts[i+1]
        
        # Rarity from image in basic info
        if 'レア度' in flat:
            imgs = t.find_all('img')
            for img in imgs:
                alt = img.get('alt', '')
                if alt in ['UR', 'SSR', 'SR', 'R']:
                    data['rarity'] = alt
        
        # Leader skill: single row with effect text mentioning ステータス or 上昇
        if ('ステータス' in flat or '上昇' in flat or '軽減' in flat) and len(rows) <= 3 and '対象ユニット' not in flat and 'HP' not in flat:
            text = flat.strip()
            if text and len(text) > 10:
                # Check if this looks like a leader skill
                # Leader skill format: "対象ユニットの全ステータスを25%上昇...【対象】：「機動戦士ガンダム」"
                data['leader_skill'] = text
        
        # Support skill table  
        # Look for tables with サポートスキル content
        if 'サポートスキル' in flat or ('発動' in flat and 'ターン' in flat):
            text = flat.strip()
            if len(text) > 10:
                data['support_skill'] = text
    
    # Better extraction: use heading context
    headings = soup.find_all(['h2', 'h3'])
    for h in headings:
        h_text = h.get_text(strip=True)
        
        if 'リーダースキル' in h_text:
            # Find next table or text block after this heading
            el = h.find_next(['table', 'p', 'div'])
            while el:
                text = el.get_text(strip=True)
                if text and len(text) > 5 and '対象ユニット' not in text:
                    # This should be the leader skill effect
                    if '上昇' in text or '軽減' in text or '回復' in text or '%' in text:
                        data['leader_skill'] = text
                        break
                if el.name == 'table':
                    # Leader skill might be in a table
                    for row in el.find_all('tr'):
                        rt = row.get_text(strip=True)
                        if ('上昇' in rt or '軽減' in rt or '回復' in rt or '%' in rt) and len(rt) > 10:
                            data['leader_skill'] = rt
                            break
                    if 'leader_skill' in data:
                        break
                el = el.find_next_sibling()
                if el and el.name in ['h2', 'h3']:
                    break
        
        if 'サポートスキル' in h_text:
            el = h.find_next(['table', 'p', 'div'])
            while el:
                text = el.get_text(strip=True)
                if text and len(text) > 5:
                    if 'ターン' in text or '発動' in text or '上昇' in text or '%' in text:
                        data['support_skill'] = text
                        break
                if el.name == 'table':
                    for row in el.find_all('tr'):
                        rt = row.get_text(strip=True)
                        if len(rt) > 10:
                            data['support_skill'] = rt
                            break
                    if 'support_skill' in data:
                        break
                el = el.find_next_sibling()
                if el and el.name in ['h2', 'h3']:
                    break
    
    # Extract target series from leader skill text
    if 'leader_skill' in data:
        m = re.search(r'【対象】[：:]「(.+?)」', data['leader_skill'])
        if m:
            data['target_series'] = m.group(1)
    
    # Rarity fallback from title
    if 'rarity' not in data and title:
        title_text = title.get_text()
        for r_val in ['UR', 'SSR', 'SR', 'R']:
            if f'({r_val})' in title_text or f'/{r_val}' in title_text:
                data['rarity'] = r_val
                break
    
    return data


def main():
    print("Collecting supporter links...")
    links = collect_supporter_links()
    print(f"Found {len(links)} supporter links")
    
    supporters = []
    for i, link in enumerate(links):
        try:
            print(f"[{i+1}/{len(links)}] Scraping {link['name']}...", end=' ', flush=True)
            sup = parse_supporter_detail(link['url'], link['name'])
            supporters.append(sup)
            has_ls = 'leader_skill' in sup
            has_ss = 'support_skill' in sup
            print(f"OK - rarity={sup.get('rarity','?')}, leader_skill={has_ls}, support_skill={has_ss}")
            time.sleep(0.5)
        except Exception as e:
            print(f"ERROR: {e}")
            supporters.append({'name': link['name'], 'source_url': link['url'], 'error': str(e)})
    
    outpath = '/Users/RH/Documents/5.File/5.Dev/GGeneDB/public/supporters.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(supporters, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone! Saved {len(supporters)} supporters to {outpath}")
    
    has_rarity = sum(1 for s in supporters if s.get('rarity'))
    has_ls = sum(1 for s in supporters if s.get('leader_skill'))
    has_ss = sum(1 for s in supporters if s.get('support_skill'))
    print(f"Rarity: {has_rarity}, Leader Skill: {has_ls}, Support Skill: {has_ss}")

if __name__ == '__main__':
    main()
