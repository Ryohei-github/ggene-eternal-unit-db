#!/usr/bin/env python3
"""
WikiWiki Gジェネエターナル Scraper
Scrapes all unit/character/supporter data from wikiwiki.jp/gget/
Images are mapped from existing GameWith data (units.json).
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import sys
import os
import urllib.parse

BASE_URL = "https://wikiwiki.jp/gget/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.9",
}
DELAY = 3.0  # seconds between requests (wikiwiki rate-limits aggressively)

# -------------------------------------------------------------------
# Utility helpers
# -------------------------------------------------------------------

def fetch_page(url, retries=5):
    """Fetch a page with retry logic and exponential backoff for 429."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 429:
                wait = min(10 * (attempt + 1), 60)
                print(f"  [WARN] 429 rate-limited, waiting {wait}s (attempt {attempt+1})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.exceptions.HTTPError as e:
            if "429" in str(e):
                wait = min(10 * (attempt + 1), 60)
                print(f"  [WARN] 429 rate-limited, waiting {wait}s (attempt {attempt+1})")
                time.sleep(wait)
                continue
            print(f"  [WARN] Attempt {attempt+1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(5)
        except Exception as e:
            print(f"  [WARN] Attempt {attempt+1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(5)
    return None


def clean_number(text):
    """Parse number from text like '100,598' -> 100598."""
    if not text:
        return 0
    text = text.strip().replace(",", "").replace("，", "")
    try:
        return int(text)
    except ValueError:
        return 0


def normalize_terrain(val):
    """Normalize terrain symbols: ◯→◯, ▲/△→△, ー/—/×→-"""
    val = val.strip()
    if val in ("◯", "○", "〇"):
        return "◯"
    if val in ("▲", "△"):
        return "△"
    if val in ("ー", "—", "×", "-", ""):
        return "-"
    return val


def extract_rarity_from_name(page_name):
    """Extract rarity from page name like 'ガンダムEz8(EX)【UR】' -> 'UR'"""
    m = re.search(r'【(ULT|UR|SSR|SR|R|N)】', page_name)
    return m.group(1) if m else ""


def extract_unit_name(page_name):
    """Extract unit name without rarity: 'ガンダムEz8(EX)【UR】' -> 'ガンダムEz8(EX)'"""
    return re.sub(r'【(ULT|UR|SSR|SR|R|N)】', '', page_name).strip()


# -------------------------------------------------------------------
# Load existing image mappings
# -------------------------------------------------------------------

def load_image_map(json_path):
    """Load name→image mapping from existing units.json."""
    if not os.path.exists(json_path):
        print(f"[INFO] No existing {json_path} found, images will be empty.")
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for item in data:
        name = item.get("name", "")
        image = item.get("image", "")
        if name and image:
            mapping[name] = image
    print(f"[INFO] Loaded {len(mapping)} image mappings from {json_path}")
    return mapping


# -------------------------------------------------------------------
# Unit List Page Scraping
# -------------------------------------------------------------------

def scrape_unit_list():
    """Scrape the unit list page to get all unit URLs and basic rarity info."""
    url = BASE_URL + urllib.parse.quote("ユニットリスト")
    print(f"[INFO] Fetching unit list: {url}")
    soup = fetch_page(url)
    if not soup:
        print("[ERROR] Failed to fetch unit list page")
        return []

    units = []
    seen = set()
    for a in soup.select("table th a, table td a"):
        href = a.get("href", "")
        if "/gget/" in href and "ユニットリスト/" in urllib.parse.unquote(href):
            full_url = urllib.parse.urljoin("https://wikiwiki.jp", href)
            if full_url not in seen:
                seen.add(full_url)
                page_name = urllib.parse.unquote(href.split("/gget/")[-1]).replace("ユニットリスト/", "")
                units.append({
                    "url": full_url,
                    "page_name": page_name,
                    "name": extract_unit_name(page_name),
                    "rarity": extract_rarity_from_name(page_name),
                })
    print(f"[INFO] Found {len(units)} unit links")
    return units


# -------------------------------------------------------------------
# Individual Unit Page Parsing
# -------------------------------------------------------------------

def parse_unit_page(soup, page_name):
    """Parse a single unit detail page from WikiWiki."""
    tables = soup.select("table")
    if len(tables) < 3:
        return None

    result = {}

    # --- Table 0: Basic info (type, combat power, terrain) ---
    t0 = tables[0]
    rows0 = t0.select("tr")

    # Type (攻撃型, 耐久型, etc.)
    type_cell = rows0[0].select("th")
    if type_cell:
        raw_type = type_cell[-1].get_text(strip=True)
        result["type"] = raw_type.replace("型", "")

    # Combat power
    for row in rows0:
        th = row.select_one("th")
        td = row.select_one("td")
        if th and td and "戦闘力" in th.get_text():
            result["combat_power"] = clean_number(td.get_text())

    # Terrain
    terrain_row_idx = None
    for i, row in enumerate(rows0):
        ths = row.select("th")
        if len(ths) >= 5 and "宇宙" in ths[0].get_text():
            terrain_row_idx = i
            break
    if terrain_row_idx is not None and terrain_row_idx + 1 < len(rows0):
        terrain_vals = rows0[terrain_row_idx + 1].select("td")
        terrain_keys = ["宇宙", "空中", "地上", "水上", "水中"]
        result["terrain"] = {}
        for j, key in enumerate(terrain_keys):
            if j < len(terrain_vals):
                result["terrain"][key] = normalize_terrain(terrain_vals[j].get_text(strip=True))
            else:
                result["terrain"][key] = "-"

    # --- Table 1: Mechanism (shield, large, transform) ---
    if len(tables) > 1:
        t1 = tables[1]
        mechanism_parts = []
        for row in t1.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td:
                label = th.get_text(strip=True)
                val = td.get_text(strip=True)
                if val in ("◯", "○", "〇"):
                    mechanism_parts.append(label)
        result["mechanism"] = "・".join(mechanism_parts) if mechanism_parts else ""

    # --- Table 2: Stats by limit break (★) or evolution stage (段階 for ULT) ---
    stats_table = None
    is_stage_table = False
    for t in tables:
        headers = [th.get_text(strip=True) for th in t.select("tr:first-child th, tr:first-child td")]
        if "★の数" in headers or "☆の数" in headers:
            stats_table = t
            break
        if "段階" in headers and "HP" in headers:
            stats_table = t
            is_stage_table = True
            break

    result["stats_by_star"] = []
    if stats_table:
        rows = stats_table.select("tr")
        header_cells = rows[0].select("th, td")
        col_names = [c.get_text(strip=True) for c in header_cells]

        for row_idx, row in enumerate(rows[1:]):
            cells = row.select("th, td")
            if len(cells) < len(col_names):
                continue
            entry = {}
            for k, cell in zip(col_names, cells):
                val = cell.get_text(strip=True)
                if k in ("★の数", "☆の数"):
                    entry["star"] = val.count("★") + val.count("☆")
                    if val in ("無し", "なし", "無", "0"):
                        entry["star"] = 0
                elif k == "段階":
                    # ULT stage table: "1段階SSR", "2段階UR", "3段階ULT"
                    entry["star"] = row_idx
                elif k == "LV":
                    entry["lv"] = clean_number(val)
                elif k == "HP":
                    entry["hp"] = clean_number(val)
                elif k == "EN":
                    entry["en"] = clean_number(val)
                elif k in ("移動力", "移動"):
                    entry["mobility"] = clean_number(val)
                elif k in ("攻撃力", "攻撃"):
                    entry["attack"] = clean_number(val)
                elif k in ("防御力", "防御"):
                    entry["defense"] = clean_number(val)
                elif k in ("機動力", "機動"):
                    entry["agility"] = clean_number(val)
            if entry.get("hp", 0) > 0:
                result["stats_by_star"].append(entry)

    # Max star stats as main stats (for backward compat)
    if result["stats_by_star"]:
        max_star = result["stats_by_star"][-1]
        result["stats"] = {
            "hp": max_star.get("hp", 0),
            "en": max_star.get("en", 0),
            "attack": max_star.get("attack", 0),
            "defense": max_star.get("defense", 0),
            "mobility": max_star.get("mobility", 0),
            "agility": max_star.get("agility", 0),
        }

    # --- Table 3: Series, Tags, Obtain PL ---
    info_table = None
    for t in tables:
        for row in t.select("tr"):
            th = row.select_one("th")
            if th and "シリーズ" in th.get_text():
                info_table = t
                break
        if info_table:
            break

    result["series"] = []
    result["tags"] = []
    result["obtain"] = ""

    if info_table:
        for row in info_table.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if not th or not td:
                continue
            label = th.get_text(strip=True)
            val = td.get_text(strip=True)
            if label == "シリーズ":
                # Split by newlines or 『...』 patterns
                series_raw = re.findall(r'『([^』]+)』', val)
                if series_raw:
                    result["series"] = series_raw
                else:
                    result["series"] = [s.strip() for s in val.split("/") if s.strip()]
            elif label == "タグ":
                result["tags"] = [t.strip() for t in re.split(r'\s*/\s*', val) if t.strip()]
            elif label in ("入手PL", "入手"):
                result["obtain"] = val

    # --- Table 4: Abilities ---
    ability_table = None
    for t in tables:
        first_row = t.select_one("tr")
        if first_row:
            first_text = first_row.get_text(strip=True)
            if first_text == "アビリティ":
                ability_table = t
                break

    result["abilities"] = []
    if ability_table:
        for row in ability_table.select("tr")[1:]:
            cells = row.select("th, td")
            if len(cells) >= 2:
                name = cells[0].get_text(strip=True)
                desc = cells[1].get_text(strip=True)
                if name and desc:
                    result["abilities"].append({"name": name, "desc": desc})
            elif len(cells) == 1:
                # Some abilities span full row as a condition
                text = cells[0].get_text(strip=True)
                if text and result["abilities"]:
                    result["abilities"][-1]["desc"] += " " + text

    # --- Tables 5+: Weapons ---
    result["weapons"] = []
    weapon_start = False
    for t in tables:
        first_row = t.select_one("tr")
        if not first_row:
            continue
        first_text = first_row.get_text(strip=True)

        # Weapon tables have weapon name in first row, then 種別/射程/POW/EN/命中/CL headers
        rows = t.select("tr")
        if len(rows) < 2:
            continue

        # Check if second row has weapon headers
        second_row_text = rows[1].get_text(strip=True) if len(rows) > 1 else ""
        if "種別" in second_row_text and "POW" in second_row_text:
            weapon = {}
            weapon["name"] = first_text.strip()

            # Parse weapon stats from third row
            if len(rows) >= 3:
                data_cells = rows[2].select("th, td")
                headers = [c.get_text(strip=True) for c in rows[1].select("th, td")]

                for h, cell in zip(headers, data_cells):
                    val = cell.get_text(strip=True)
                    if h == "種別":
                        parts = val.split("/")
                        if len(parts) >= 2:
                            weapon["attribute"] = parts[0].strip()
                            weapon["weapon_type"] = "/".join(p.strip() for p in parts[1:])
                        else:
                            weapon["attribute"] = val
                            weapon["weapon_type"] = ""
                    elif h == "射程":
                        weapon["range"] = val
                    elif h == "POW":
                        weapon["power"] = val
                    elif h == "EN":
                        weapon["en"] = val
                    elif h == "命中":
                        weapon["hit"] = val
                    elif h in ("CL", "クリ"):
                        weapon["critical"] = val
                    elif h == "弾数":
                        weapon["ammo"] = val

            # Effect/restriction from remaining rows
            effects = []
            for row in rows[3:]:
                text = row.get_text(strip=True)
                if text:
                    effects.append(text)
            weapon["effect"] = " ".join(effects) if effects else ""
            weapon["restriction"] = ""

            # Detect EX/MAP from name
            if "MAP" in weapon["name"].upper():
                weapon["range"] = "MAP"
            if weapon.get("name"):
                # Use ammo from 弾数 header if available, otherwise try extracting from effect
                if not weapon.get("ammo"):
                    ammo_match = re.search(r'(\d+)発', weapon.get("effect", ""))
                    weapon["ammo"] = ammo_match.group(1) if ammo_match else ""

                result["weapons"].append(weapon)

    return result


# -------------------------------------------------------------------
# Pilot/Character List Page Scraping
# -------------------------------------------------------------------

def scrape_pilot_list():
    """Scrape the pilot list page to get all character URLs."""
    url = BASE_URL + urllib.parse.quote("パイロットリスト")
    print(f"[INFO] Fetching pilot list: {url}")
    soup = fetch_page(url)
    if not soup:
        print("[ERROR] Failed to fetch pilot list page")
        return []

    pilots = []
    seen = set()
    for a in soup.select("table th a, table td a"):
        href = a.get("href", "")
        decoded = urllib.parse.unquote(href)
        if "/gget/" in href and "パイロットリスト/" in decoded:
            full_url = urllib.parse.urljoin("https://wikiwiki.jp", href)
            if full_url not in seen:
                seen.add(full_url)
                page_name = decoded.split("/gget/")[-1].replace("パイロットリスト/", "")
                pilots.append({
                    "url": full_url,
                    "page_name": page_name,
                    "name": extract_unit_name(page_name),
                    "rarity": extract_rarity_from_name(page_name),
                })
    print(f"[INFO] Found {len(pilots)} pilot links")
    return pilots


def scrape_supporter_list():
    """Scrape the supporter list page to get all supporter URLs."""
    url = BASE_URL + urllib.parse.quote("サポーターリスト")
    print(f"[INFO] Fetching supporter list: {url}")
    soup = fetch_page(url)
    if not soup:
        print("[ERROR] Failed to fetch supporter list page")
        return []

    supporters = []
    seen = set()
    for a in soup.select("table th a, table td a"):
        href = a.get("href", "")
        decoded = urllib.parse.unquote(href)
        if "/gget/" in href and "サポーターリスト/" in decoded:
            full_url = urllib.parse.urljoin("https://wikiwiki.jp", href)
            if full_url not in seen:
                seen.add(full_url)
                page_name = decoded.split("/gget/")[-1].replace("サポーターリスト/", "")
                supporters.append({
                    "url": full_url,
                    "page_name": page_name,
                    "name": extract_unit_name(page_name),
                    "rarity": extract_rarity_from_name(page_name),
                })
    print(f"[INFO] Found {len(supporters)} supporter links")
    return supporters


# -------------------------------------------------------------------
# Character/Pilot Page Parsing
# -------------------------------------------------------------------

def parse_pilot_page(soup, page_name):
    """Parse a single pilot/character detail page."""
    tables = soup.select("table")
    if not tables:
        return None

    result = {}

    # Look for stats table with 射撃/格闘/覚醒/守備/反応
    # Wiki format: 4-row table with alternating header/data rows
    # Row 0: [射撃, 格闘, 覚醒]  Row 1: [634, 551, 897]
    # Row 2: [守備, 反応, SP]    Row 3: [541, 727, 15]
    for t in tables:
        all_text = t.get_text()
        if "射撃" in all_text and "格闘" in all_text:
            rows = t.select("tr")
            entry = {}
            i = 0
            while i < len(rows) - 1:
                header_cells = rows[i].select("th, td")
                data_cells = rows[i + 1].select("th, td")
                header_names = [c.get_text(strip=True) for c in header_cells]
                # Check if this row looks like a header row (contains stat names)
                stat_names = {"射撃", "格闘", "覚醒", "守備", "反応", "SP", "射撃値", "格闘値", "覚醒値", "守備値", "反応値"}
                if any(h in stat_names for h in header_names):
                    for k, cell in zip(header_names, data_cells):
                        val = cell.get_text(strip=True)
                        if k in ("射撃", "射撃値"):
                            entry["shooting"] = clean_number(val)
                        elif k in ("格闘", "格闘値"):
                            entry["melee"] = clean_number(val)
                        elif k in ("覚醒", "覚醒値"):
                            entry["awakening"] = clean_number(val)
                        elif k in ("守備", "守備値", "防御"):
                            entry["defense"] = clean_number(val)
                        elif k in ("反応", "反応値"):
                            entry["reaction"] = clean_number(val)
                        elif k == "SP":
                            entry["sp"] = clean_number(val)
                    i += 2  # Skip data row
                else:
                    i += 1
            if entry.get("shooting", 0) > 0:
                result["stats"] = entry
            break

    # Type
    for t in tables:
        rows = t.select("tr")
        for row in rows:
            th = row.select_one("th")
            if th and ("型" in th.get_text() or th.get_text(strip=True) in ("射撃型", "格闘型", "覚醒型", "守備型")):
                result["chara_type"] = th.get_text(strip=True).replace("型", "")
                break
        if "chara_type" in result:
            break

    # Combat power
    for t in tables:
        for row in t.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td and "戦闘力" in th.get_text():
                result["combat_power"] = clean_number(td.get_text())
                break

    # Series, Tags
    result["series"] = []
    result["tags"] = []
    for t in tables:
        for row in t.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if not th or not td:
                continue
            label = th.get_text(strip=True)
            val = td.get_text(strip=True)
            if label == "シリーズ":
                series_raw = re.findall(r'『([^』]+)』', val)
                result["series"] = series_raw if series_raw else [s.strip() for s in val.split("/") if s.strip()]
            elif label == "タグ":
                result["tags"] = [t.strip() for t in re.split(r'\s*/\s*', val) if t.strip()]

    # Skills
    # Wiki format: title row [スキル], header row [名称, SP, 効果], then data rows
    result["skills"] = []
    for t in tables:
        first_row = t.select_one("tr")
        if first_row and "スキル" in first_row.get_text(strip=True):
            for row in t.select("tr")[1:]:
                cells = row.select("th, td")
                if len(cells) >= 2:
                    name = cells[0].get_text(strip=True)
                    # Skip sub-header rows
                    if name in ("名称", "スキル名", "名前"):
                        continue
                    if len(cells) >= 3:
                        # 3-column format: [名称, SP, 効果]
                        sp_text = cells[1].get_text(strip=True)
                        effect = cells[2].get_text(strip=True)
                        sp_val = int(sp_text) if sp_text.isdigit() else 0
                    else:
                        # 2-column fallback
                        desc = cells[1].get_text(strip=True)
                        sp_val = 0
                        if desc.isdigit():
                            sp_val = int(desc)
                            effect = ""
                        else:
                            effect = desc
                    result["skills"].append({
                        "name": name,
                        "effect": effect,
                        "sp_cost": sp_val,
                    })
            break

    # Abilities
    # Wiki format: title [アビリティ], then rows of [name, desc, (optional condition)]
    # EXアビリティ uses rowspan - first row has "EXアビリティ" in name col,
    # subsequent rows in the EX block only have [effect, unit/condition]
    result["abilities"] = []
    for t in tables:
        first_row = t.select_one("tr")
        if first_row and first_row.get_text(strip=True) == "アビリティ":
            in_ex_block = False
            for row in t.select("tr")[1:]:
                cells = row.select("th, td")
                if not cells:
                    continue

                if len(cells) >= 3:
                    # 3-column row: [name, desc, condition]
                    name = cells[0].get_text(strip=True)
                    desc = cells[1].get_text(strip=True)
                    condition = cells[2].get_text(strip=True)
                    if name in ("EXアビリティ", "EXキャラアビリティ"):
                        in_ex_block = True
                        # First EX ability effect is in desc
                        if desc:
                            result["abilities"].append({
                                "name": "EXアビリティ",
                                "desc": desc,
                                "condition": condition
                            })
                    elif name:
                        in_ex_block = False
                        if desc:
                            result["abilities"].append({
                                "name": name,
                                "desc": desc,
                                "condition": condition
                            })
                elif len(cells) == 2:
                    c0 = cells[0].get_text(strip=True)
                    c1 = cells[1].get_text(strip=True)
                    if in_ex_block:
                        # Continuation of EX block: [effect, unit/condition]
                        if c0:
                            result["abilities"].append({
                                "name": "EXアビリティ",
                                "desc": c0,
                                "condition": c1
                            })
                    else:
                        # Normal 2-column ability
                        if c0 in ("EXアビリティ", "EXキャラアビリティ"):
                            in_ex_block = True
                            if c1:
                                result["abilities"].append({
                                    "name": "EXアビリティ",
                                    "desc": c1,
                                    "condition": ""
                                })
                        elif c0 and c1:
                            result["abilities"].append({
                                "name": c0,
                                "desc": c1,
                                "condition": ""
                            })
                elif len(cells) == 1:
                    # Single cell - might be EX block continuation
                    text = cells[0].get_text(strip=True)
                    if text and in_ex_block:
                        result["abilities"].append({
                            "name": "EXアビリティ",
                            "desc": text,
                            "condition": ""
                        })
            break

    return result


# -------------------------------------------------------------------
# Supporter Page Parsing
# -------------------------------------------------------------------

def parse_supporter_page(soup, page_name):
    """Parse a single supporter detail page."""
    tables = soup.select("table")
    if not tables:
        return None

    result = {}
    result["abilities"] = []

    # Supporters typically have effect descriptions
    for t in tables:
        for row in t.select("tr"):
            cells = row.select("th, td")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if label in ("効果", "スキル効果"):
                    result["abilities"].append({"name": label, "desc": val})
                elif label == "シリーズ":
                    series_raw = re.findall(r'『([^』]+)』', val)
                    result["series"] = series_raw if series_raw else [s.strip() for s in val.split("/") if s.strip()]
                elif label == "タグ":
                    result["tags"] = [t.strip() for t in re.split(r'\s*/\s*', val) if t.strip()]

    if "series" not in result:
        result["series"] = []
    if "tags" not in result:
        result["tags"] = []

    return result


# -------------------------------------------------------------------
# Main Scraping Logic
# -------------------------------------------------------------------

def build_output_unit(idx, unit_info, parsed, image_map):
    """Build final unit JSON object matching frontend expectations."""
    name = unit_info["name"]
    image = image_map.get(name, "")

    output = {
        "id": idx,
        "name": name,
        "image": image,
        "rarity": unit_info["rarity"],
        "type": parsed.get("type", ""),
        "obtain": parsed.get("obtain", ""),
        "series": parsed.get("series", []),
        "tags": parsed.get("tags", []),
        "normal": {
            "combat_power": parsed.get("combat_power", 0),
            "terrain": parsed.get("terrain", {"宇宙": "-", "空中": "-", "地上": "-", "水上": "-", "水中": "-"}),
            "stats": parsed.get("stats", {"hp": 0, "en": 0, "attack": 0, "defense": 0, "mobility": 0, "agility": 0}),
            "abilities": parsed.get("abilities", []),
            "mechanism": parsed.get("mechanism", ""),
        },
        "stats_by_star": parsed.get("stats_by_star", []),
        "normal_weapons": parsed.get("weapons", []),
        "transformed": False,
        "transformed_weapons": [],
    }
    return output


def build_output_chara(idx, pilot_info, parsed, image_map):
    """Build character JSON matching frontend expectations."""
    name = pilot_info["name"]
    image = image_map.get(name, "")

    # Character entries need 'キャラ' tag for frontend separation
    tags = parsed.get("tags", [])
    if "キャラ" not in tags:
        tags = ["キャラ"] + tags

    stats = parsed.get("stats", {})

    output = {
        "id": idx,
        "name": name,
        "image": image,
        "rarity": pilot_info["rarity"],
        "type": parsed.get("chara_type", ""),
        "obtain": "",
        "series": parsed.get("series", []),
        "tags": tags,
        "normal": {
            "combat_power": parsed.get("combat_power", 0),
            "stats": {
                "shooting": stats.get("shooting", 0),
                "melee": stats.get("melee", 0),
                "awakening": stats.get("awakening", 0),
                "defense": stats.get("defense", 0),
                "reaction": stats.get("reaction", 0),
            },
            "skills": parsed.get("skills", []),
            "abilities": parsed.get("abilities", []),
        },
    }
    return output


def build_output_supporter(idx, supp_info, parsed, image_map):
    """Build supporter JSON."""
    name = supp_info["name"]
    image = image_map.get(name, "")

    output = {
        "id": idx,
        "name": name,
        "image": image,
        "rarity": supp_info["rarity"],
        "type": "",
        "obtain": "",
        "series": parsed.get("series", []),
        "tags": parsed.get("tags", []),
        "abilities": parsed.get("abilities", []),
    }
    return output


def main():
    # Determine script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "public", "units.json")
    progress_path = os.path.join(script_dir, "wikiwiki_progress.json")

    # Load existing image map
    existing_json = os.path.join(script_dir, "public", "units.json")
    image_map = load_image_map(existing_json)

    # Load progress for resume support
    progress = {"units_done": [], "pilots_done": [], "supporters_done": [], "all_data": []}
    if os.path.exists(progress_path):
        with open(progress_path, "r", encoding="utf-8") as f:
            progress = json.load(f)
        print(f"[INFO] Resuming from progress: {len(progress['units_done'])} units, {len(progress['pilots_done'])} pilots done")

    all_data = progress.get("all_data", [])
    next_id = max((d["id"] for d in all_data), default=0) + 1

    # ---- Phase 1: Units ----
    print("\n" + "=" * 60)
    print("PHASE 1: Scraping Units")
    print("=" * 60)
    unit_list = scrape_unit_list()
    time.sleep(DELAY)

    units_done = set(progress.get("units_done", []))
    for i, unit_info in enumerate(unit_list):
        if unit_info["url"] in units_done:
            continue
        print(f"  [{i+1}/{len(unit_list)}] {unit_info['name']} ({unit_info['rarity']})")
        soup = fetch_page(unit_info["url"])
        if soup:
            parsed = parse_unit_page(soup, unit_info["page_name"])
            if parsed:
                output = build_output_unit(next_id, unit_info, parsed, image_map)
                all_data.append(output)
                next_id += 1
            else:
                print(f"    [WARN] Failed to parse: {unit_info['name']}")
        else:
            print(f"    [ERROR] Failed to fetch: {unit_info['url']}")

        units_done.add(unit_info["url"])
        time.sleep(DELAY)

        # Save progress every 20 units
        if len(units_done) % 20 == 0:
            progress["units_done"] = list(units_done)
            progress["all_data"] = all_data
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False)
            print(f"    [SAVE] Progress saved ({len(units_done)} units)")

    progress["units_done"] = list(units_done)
    progress["all_data"] = all_data

    # ---- Phase 2: Pilots/Characters ----
    print("\n" + "=" * 60)
    print("PHASE 2: Scraping Pilots/Characters")
    print("=" * 60)
    pilot_list = scrape_pilot_list()
    time.sleep(DELAY)

    pilots_done = set(progress.get("pilots_done", []))
    for i, pilot_info in enumerate(pilot_list):
        if pilot_info["url"] in pilots_done:
            continue
        print(f"  [{i+1}/{len(pilot_list)}] {pilot_info['name']} ({pilot_info['rarity']})")
        soup = fetch_page(pilot_info["url"])
        if soup:
            parsed = parse_pilot_page(soup, pilot_info["page_name"])
            if parsed:
                output = build_output_chara(next_id, pilot_info, parsed, image_map)
                all_data.append(output)
                next_id += 1
            else:
                print(f"    [WARN] Failed to parse: {pilot_info['name']}")
        else:
            print(f"    [ERROR] Failed to fetch: {pilot_info['url']}")

        pilots_done.add(pilot_info["url"])
        time.sleep(DELAY)

        if len(pilots_done) % 20 == 0:
            progress["pilots_done"] = list(pilots_done)
            progress["all_data"] = all_data
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False)

    progress["pilots_done"] = list(pilots_done)
    progress["all_data"] = all_data

    # ---- Phase 3: Supporters ----
    print("\n" + "=" * 60)
    print("PHASE 3: Scraping Supporters")
    print("=" * 60)
    supporter_list = scrape_supporter_list()
    time.sleep(DELAY)

    supporters_done = set(progress.get("supporters_done", []))
    for i, supp_info in enumerate(supporter_list):
        if supp_info["url"] in supporters_done:
            continue
        print(f"  [{i+1}/{len(supporter_list)}] {supp_info['name']} ({supp_info['rarity']})")
        soup = fetch_page(supp_info["url"])
        if soup:
            parsed = parse_supporter_page(soup, supp_info["page_name"])
            if parsed:
                output = build_output_supporter(next_id, supp_info, parsed, image_map)
                all_data.append(output)
                next_id += 1
        supporters_done.add(supp_info["url"])
        time.sleep(DELAY)

    # ---- Save final output ----
    print(f"\n[INFO] Total items scraped: {len(all_data)}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[DONE] Saved to {output_path}")

    # Cleanup progress file
    if os.path.exists(progress_path):
        os.remove(progress_path)
        print("[INFO] Progress file cleaned up")


if __name__ == "__main__":
    main()
