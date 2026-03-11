#!/usr/bin/env python3
"""Fix units.json: remove non-unit entries, fix MAP weapon data with ammo counts."""
import requests
from bs4 import BeautifulSoup
import json
import time
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def fix_map_weapons(unit):
    """Re-check a unit's GameWith page for MAP weapon flags and ammo counts."""
    url = unit.get('source_url', '')
    if not url:
        return unit

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')

        # Find weapon data in the _stat divs
        # Structure: each weapon has a _stat div with label divs for RANGE, POWER, EN, etc.
        # MAP weapons have <div label="RANGE">MAP</div>
        # Ammo is <div label="弾数">N</div>

        # Find all weapon sections - they're in table cells with _stat class
        stat_divs = soup.find_all('div', class_='_stat')

        weapon_data = []
        for stat_div in stat_divs:
            range_div = stat_div.find('div', attrs={'label': 'RANGE'})
            ammo_div = stat_div.find('div', attrs={'label': '弾数'})

            if range_div:
                range_text = range_div.get_text(strip=True)
                is_map = (range_text == 'MAP')
                ammo = None
                if ammo_div:
                    ammo_text = ammo_div.get_text(strip=True)
                    try:
                        ammo = int(ammo_text)
                    except ValueError:
                        pass
                weapon_data.append({
                    'is_map': is_map,
                    'use_count': ammo
                })
            else:
                weapon_data.append({'is_map': False, 'use_count': None})

        # Match weapon_data to unit's weapons list
        # The weapon tables include both 通常 and 変形 weapons
        # We need to match by position
        weapons = unit.get('weapons', [])

        # Count how many weapon entries we found
        if len(weapon_data) >= len(weapons):
            for i, w in enumerate(weapons):
                if i < len(weapon_data):
                    w['is_map'] = weapon_data[i]['is_map']
                    if weapon_data[i]['use_count'] is not None:
                        w['use_count'] = weapon_data[i]['use_count']
                    elif 'use_count' not in w:
                        w['use_count'] = None
        else:
            # Fallback: search by weapon name in HTML
            for w in weapons:
                # Check if this weapon name appears near a MAP range
                name = re.escape(w['name'].replace('EX', '').strip())
                pattern = name + r'.*?label="RANGE">(MAP|\d)'
                match = re.search(pattern, html, re.DOTALL)
                if match and match.group(1) == 'MAP':
                    w['is_map'] = True
                    # Find ammo nearby
                    ammo_match = re.search(r'label="弾数">(\d+)', html[match.start():match.start()+500])
                    if ammo_match:
                        w['use_count'] = int(ammo_match.group(1))

    except Exception as e:
        print(f"  ERROR fetching {url}: {e}")

    return unit


def main():
    with open('public/units.json', 'r', encoding='utf-8') as f:
        units = json.load(f)

    print(f"Original units: {len(units)}")

    # Step 1: Filter to only EX units (actual mech units)
    ex_units = [u for u in units if '(EX)' in u.get('name', '')]
    print(f"EX units only: {len(ex_units)}")

    # Step 2: Fix MAP weapon data by re-checking each page
    for i, unit in enumerate(ex_units):
        print(f"[{i+1}/{len(ex_units)}] {unit['name']}...", end=' ', flush=True)
        fix_map_weapons(unit)
        map_count = sum(1 for w in unit.get('weapons', []) if w.get('is_map'))
        if map_count:
            ammos = [str(w.get('use_count', '?')) for w in unit.get('weapons', []) if w.get('is_map')]
            print(f"MAP={map_count} ammo={ammos}")
        else:
            print("OK")
        time.sleep(0.3)

    # Step 3: Save
    outpath = 'public/units.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(ex_units, f, ensure_ascii=False, indent=2)

    map_units = sum(1 for u in ex_units if any(w.get('is_map') for w in u.get('weapons', [])))
    print(f"\nDone! Saved {len(ex_units)} units to {outpath}")
    print(f"Units with MAP weapons: {map_units}")


if __name__ == '__main__':
    main()
