#!/usr/bin/env python3
"""
GameWith Gジェネエターナル Unit Scraper
Scrapes all unit data from GameWith individual unit pages.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import sys
import os

BASE_URL = "https://gamewith.jp/ggene-eternal/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.9",
}

# All article IDs collected from the list page
ALL_IDS = [
    # Chunk 0
    494618,494623,494629,494621,494620,494651,522839,494668,536914,537496,
    536942,524500,497484,497485,497483,545380,545383,494616,546760,532076,
    496188,494681,496189,496190,496191,494871,494870,494861,494860,494863,
    494862,494865,494864,494867,494866,494869,494868,494873,494872,495657,
    495656,497175,497176,501196,501197,502731,502730,505942,505943,507347,
    507348,512096,512097,513206,513207,516590,516591,518729,518728,521258,
    521257,521256,522772,522771,527322,527321,529042,529043,532058,532059,
    533694,533693,537873,537872,540488,540487,543046,543045,544875,544874,
    546755,546754,496163,494682,496139,496970,496971,495090,495089,495092,
    495091,495088,495087,495086,495085,495084,495083,495082,495081,495080,
    # Chunk 1
    495079,497173,497174,501200,501201,502735,502736,505944,505945,507344,
    507343,512098,512099,513208,513209,516588,516589,518727,518726,521262,
    521261,521263,522775,522774,527324,512212,527319,527323,529044,529045,
    532061,532060,533691,533692,537869,537868,540491,540490,543044,543043,
    544872,544873,543130,546751,546750,496120,494683,494689,496113,495126,
    495125,495124,495123,495122,495121,495120,495119,495118,495117,495116,
    495115,495114,495113,495112,495665,497172,501203,502737,505948,507346,
    512108,513210,516592,518730,521254,522765,527327,529041,532055,533686,
    537870,540481,543041,544870,546748,495063,494989,494925,495177,494885,
    494923,494934,494943,495051,495127,495205,495222,497171,494650,533597,
    # Chunk 2
    546918,546919,546920,546921,546922,546923,546924,546925,546926,546927,
    546928,546773,546774,546775,544991,544967,544992,544993,544332,543104,
    543105,543106,543107,543108,543110,543109,543059,543074,543061,543062,
    543063,540566,540512,540568,540567,538095,538094,538093,538091,538090,
    538092,538089,538088,538087,538086,538085,538084,538082,537887,537894,
    538081,538083,538080,538079,538078,538077,538076,537226,537196,537225,
    533749,533708,532476,532477,532071,532070,532075,532050,532034,532035,
    532036,532037,532038,532039,532049,532040,530879,529117,529146,529116,
    529242,529241,529240,529239,529238,529237,529236,529235,529234,529231,
    529233,529232,524957,524409,522812,522820,522813,522814,522770,522557,
    # Chunk 3
    522379,522378,522377,522375,522374,522376,522373,522372,522036,522037,
    522038,522039,521750,521751,521752,521753,521754,521755,521756,521313,
    521354,521314,521318,520922,518770,518789,518754,518755,518756,518757,
    518758,517469,517471,516599,516594,514429,514446,514428,514451,517844,
    513353,517845,516740,513218,507366,507393,507365,507358,506152,506154,
    506125,506150,506037,506038,506039,506041,506040,506042,503236,502761,
    501211,501223,501210,501199,501198,497179,497180,497178,497181,497475,
    497474,497473,497472,497471,497470,497469,497468,497467,497466,497465,
    497464,497463,497462,497461,497460,497459,497458,497457,497456,497455,
    497454,497453,497452,497451,497450,497449,497448,497447,497446,497445,
    # Chunk 4
    497444,497443,497442,497441,497440,497439,497438,497437,497436,497435,
    497434,497433,497432,497431,496321,496322,496323,496324,496325,496700,
    496326,496327,496685,496328,496329,496330,496331,496332,496333,496334,
    496335,496443,496336,496337,496338,496339,496340,496605,496341,496342,
    496343,496344,496345,496346,496347,496348,496349,496350,496351,496352,
    496353,496354,496355,496356,496357,496358,496603,496359,496699,496360,
    496361,496362,496363,496364,496365,496366,496367,496368,496369,496370,
    496371,496372,496373,496374,496375,496602,496444,496445,496376,496377,
    496067,495362,496064,496051,495345,496050,495672,495673,495674,543060,
    539694,537010,537011,537012,537013,537014,537015,533796,506036,496256,
    # Chunk 5
    496257,496258,496259,496260,496704,496261,496262,496263,496264,496265,
    496266,496703,496267,496268,496269,496270,496447,496271,496272,496273,
    496274,496275,496276,496277,496278,496279,496702,496280,496281,496282,
    496283,496284,496285,496286,496287,496288,496289,496290,496291,496292,
    496293,496294,496295,496296,496297,496298,496448,496299,496300,496301,
    496302,496303,496304,496305,496306,496307,496308,496309,496310,496701,
    496311,496312,496313,496446,496314,496315,496316,496317,496318,496319,
    496320,496052,495671,496192,496193,496194,496195,496196,496197,496198,
    496199,496200,496201,496458,496202,496203,496204,496205,496206,496207,
    496208,496707,496209,496210,496211,496212,496213,496214,496215,496216,
    # Chunk 6
    496217,496218,496219,496220,496221,496222,496223,496224,496225,496226,
    496227,496228,496229,496230,496706,496231,496232,496233,496234,496235,
    496236,496237,496457,496456,496238,496239,496455,496240,496454,496453,
    496241,496452,496705,496242,496451,496243,496244,496450,496245,496449,
    496246,496247,496248,496249,496250,496251,496252,496253,496254,496255,
    496055,496054,496053,495670,496057,496056,495133,
]

# Remove known non-unit page IDs (list pages, guide pages, etc.)
EXCLUDE_IDS = {496188, 494681, 496189, 496190, 496191, 494650}
ALL_IDS = [x for x in ALL_IDS if x not in EXCLUDE_IDS]
# Deduplicate
ALL_IDS = list(dict.fromkeys(ALL_IDS))


def fetch_page(article_id):
    """Fetch a GameWith page and return BeautifulSoup object."""
    url = f"{BASE_URL}{article_id}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser"), url


def parse_basic_info(soup):
    """Extract name, image, rarity, type, obtain method from basic info table."""
    # The first table that is NOT .wd-ggene-weapons and is inside the article
    article = soup.select_one("div.article_body, article, #article-body")
    if not article:
        article = soup

    tables = article.find_all("table")
    info = {}

    for table in tables:
        if "wd-ggene-weapons" in (table.get("class") or []):
            continue
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        # Check if this looks like a basic info table
        first_row_text = rows[0].get_text(strip=True)
        has_rarity = False
        for row in rows:
            cells = row.find_all(["th", "td"])
            for cell in cells:
                if "レア" in cell.get_text():
                    has_rarity = True
                    break

        if not has_rarity:
            continue

        # Parse basic info rows
        for row in rows:
            cells = row.find_all(["th", "td"])
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                # Name and image from first row
                img = cell.find("img")
                if img and not info.get("image"):
                    # GameWith uses lazy-loading: real URL in data-original
                    src = img.get("data-original") or img.get("data-src") or img.get("src", "")
                    if src.startswith("http") and "transparent1px" not in src:
                        info["image"] = src
                # Parse labeled fields
                if "レア" in text and i + 1 < len(cells):
                    rarity_text = cells[i + 1].get_text(strip=True)
                    info["rarity"] = rarity_text
                elif text == "レア":
                    # Rarity might be in the same cell after the label
                    pass
                if "タイプ" in text and "武装" not in text:
                    if i + 1 < len(cells):
                        info["type"] = cells[i + 1].get_text(strip=True)
                if "入手方法" in text and i + 1 < len(cells):
                    info["obtain"] = cells[i + 1].get_text(strip=True)

        # Get name from first row - usually the first text node
        first_row = rows[0]
        first_td = first_row.find("td")
        if first_td:
            # Name is usually text content after the image
            name_parts = []
            for child in first_td.children:
                if isinstance(child, str):
                    t = child.strip()
                    if t:
                        name_parts.append(t)
                elif child.name and child.name != "img":
                    t = child.get_text(strip=True)
                    if t and t != info.get("rarity") and t != info.get("type"):
                        name_parts.append(t)
            if name_parts:
                info["name"] = name_parts[0]

            # Also try getting image from first td
            if not info.get("image"):
                img = first_td.find("img")
                if img:
                    src = img.get("data-original") or img.get("data-src") or img.get("src", "")
                    if src.startswith("http") and "transparent1px" not in src:
                        info["image"] = src

        if info.get("name") or info.get("rarity"):
            break  # Found the basic info table

    return info


def parse_series_tags(soup):
    """Extract series and tags arrays."""
    result = {"series": [], "tags": []}
    # Find h4 containing シリーズ・タグ
    for h4 in soup.find_all(["h3", "h4"]):
        if "シリーズ" in h4.get_text():
            # Next sibling table after this h4 (not descendant)
            table = h4.find_next_sibling("table")
            if not table:
                table = h4.find_next("table")
            if table:
                # GameWith has malformed HTML: <td> outside <tr>
                # Structure: <tr><th>シリーズ</th></tr><td>...</td><tr><th>タグ</th></tr><td>...</td>
                # So we find all TH and TD as direct/indirect children
                all_ths = table.find_all("th")
                all_tds = table.find_all("td")
                for i, th in enumerate(all_ths):
                    label = th.get_text(strip=True)
                    if i < len(all_tds):
                        td = all_tds[i]
                        tag_div = td.find("div", class_="unit_tag")
                        if tag_div:
                            items = [s.get_text(strip=True) for s in tag_div.find_all("span") if s.get_text(strip=True)]
                        else:
                            items = [td.get_text(strip=True)]
                        if "シリーズ" in label:
                            result["series"] = items
                        elif "タグ" in label:
                            result["tags"] = items
            break
    return result


def parse_form_data(container):
    """Parse stats, terrain, abilities, mechanism from a single form container (normal or transformed)."""
    form = {
        "terrain": {},
        "stats": {},
        "abilities": [],
        "mechanism": "",
        "combat_power": 0,
    }
    tables = container.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue

        # Detect table type by header content
        first_row_text = rows[0].get_text(strip=True) if rows else ""

        # Terrain table: has 宇宙, 空中, etc.
        headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        if any(h in headers for h in ["宇宙", "空中", "地上"]):
            vals = [td.get_text(strip=True) for td in rows[-1].find_all("td")]
            terrain_keys = ["宇宙", "空中", "地上", "水上", "水中"]
            for i, key in enumerate(terrain_keys):
                if i < len(vals):
                    form["terrain"][key] = vals[i]
            continue

        # Stats table: contains 戦闘力
        full_text = table.get_text()
        if "戦闘力" in full_text and "HP" in full_text:
            # Extract combat power
            cp_match = re.search(r"戦闘力(\d+)", full_text)
            if cp_match:
                form["combat_power"] = int(cp_match.group(1))

            # Extract stat pairs from all rows
            all_cells = []
            for row in rows:
                for cell in row.find_all(["th", "td"]):
                    text = cell.get_text(strip=True)
                    # Skip the combat power cell (has rowspan)
                    if "戦闘力" in text:
                        continue
                    all_cells.append(text)

            # Pair up: label, value, label, value...
            stat_map = {
                "HP": "hp", "EN": "en", "攻撃力": "attack",
                "防御力": "defense", "移動力": "mobility", "機動力": "agility"
            }
            for i in range(len(all_cells) - 1):
                if all_cells[i] in stat_map:
                    try:
                        form["stats"][stat_map[all_cells[i]]] = int(all_cells[i + 1])
                    except ValueError:
                        form["stats"][stat_map[all_cells[i]]] = all_cells[i + 1]
            continue

        # Abilities or Mechanism table
        if "機構" in first_row_text or any("機構" in (th.get_text(strip=True)) for th in table.find_all("th")):
            # Mechanism
            for td in table.find_all("td"):
                text = td.get_text(strip=True)
                if text and text != "機構":
                    form["mechanism"] = text
                    break
            continue

        # Check if it's an abilities table (has paired name/desc rows)
        if len(rows) >= 2:
            is_ability = False
            for row in rows:
                cells = row.find_all(["th", "td"])
                if len(cells) == 1:
                    text = cells[0].get_text(strip=True)
                    if text and len(text) > 10:  # Description-like
                        is_ability = True
                        break

            if is_ability or "アビリティ" in full_text:
                i = 0
                while i < len(rows):
                    row_text = rows[i].get_text(strip=True)
                    if row_text and i + 1 < len(rows):
                        name = row_text
                        desc = rows[i + 1].get_text(strip=True)
                        if name and desc and len(desc) > len(name):
                            form["abilities"].append({"name": name, "desc": desc})
                            i += 2
                            continue
                    i += 1

    return form


def parse_weapons(container):
    """Parse weapons from a form container."""
    weapons = []
    weapon_tables = container.find_all("table", class_="wd-ggene-weapons")

    for wt in weapon_tables:
        weapon = {}
        rows = wt.find_all("tr")
        if not rows:
            continue

        # First row: weapon name + attribute
        th = rows[0].find("th")
        if th:
            # Attribute from _float-right div
            attr_div = th.find("div", class_="_float-right")
            if attr_div:
                weapon["attribute"] = attr_div.get_text(strip=True)
                attr_div.decompose()  # Remove to get clean name
            weapon["name"] = th.get_text(strip=True)

        # Stats from _stat div
        stat_div = wt.find("div", class_="_stat")
        if stat_div:
            stat_children = stat_div.find_all("div", recursive=False)
            stat_keys = ["range", "power", "en", "hit", "critical", "ammo"]
            for i, key in enumerate(stat_keys):
                if i < len(stat_children):
                    val = stat_children[i].get_text(strip=True)
                    # Remove label prefix if present
                    val = re.sub(r"^(RANGE|POWER|EN|命中|クリティカル|弾数)", "", val).strip()
                    weapon[key] = val

        # Type and effects from _text div
        text_div = wt.find("div", class_="_text")
        if text_div:
            labels = text_div.find_all("div", class_="_label-0")
            for label in labels:
                label_text = label.get_text(strip=True)
                # Get the next sibling div for value
                next_div = label.find_next_sibling("div")
                if next_div:
                    val = next_div.get_text(strip=True)
                    if "タイプ" in label_text:
                        weapon["weapon_type"] = val
                    elif "武装効果" in label_text:
                        weapon["effect"] = val
                    elif "使用制限" in label_text:
                        weapon["restriction"] = val
                    elif "MAP" in label_text or "範囲" in label_text:
                        weapon["map_range"] = val

        if weapon.get("name"):
            weapons.append(weapon)

    return weapons


def parse_unit_page(article_id):
    """Parse a single GameWith unit page and return structured data."""
    soup, url = fetch_page(article_id)

    # Check if this is actually a unit page (has basic info with rarity)
    basic = parse_basic_info(soup)
    if not basic.get("rarity") and not basic.get("name"):
        return None  # Not a unit page

    unit = {
        "id": article_id,
        "gamewith_url": url,
        "name": basic.get("name", ""),
        "image": basic.get("image", ""),
        "rarity": basic.get("rarity", ""),
        "type": basic.get("type", ""),
        "obtain": basic.get("obtain", ""),
    }

    # Series and tags
    st = parse_series_tags(soup)
    unit["series"] = st["series"]
    unit["tags"] = st["tags"]

    # Forms (normal + transformed)
    toggle_wraps = soup.find_all("div", class_="ggene_toggle_content_wrap")

    # First toggle_wrap = stats, second = weapons
    stats_wrap = toggle_wraps[0] if len(toggle_wraps) > 0 else None
    weapons_wrap = toggle_wraps[1] if len(toggle_wraps) > 1 else None

    if stats_wrap:
        form_containers = stats_wrap.find_all("div", class_="js-nav-tabs-content")
        if form_containers:
            # Normal form
            unit["normal"] = parse_form_data(form_containers[0])
            # Transformed form (if exists)
            if len(form_containers) > 1:
                unit["transformed"] = parse_form_data(form_containers[1])
    else:
        # No toggle wrapper - try parsing stats from the page directly
        unit["normal"] = parse_form_data(soup)

    if weapons_wrap:
        weapon_containers = weapons_wrap.find_all("div", class_="js-nav-tabs-content")
        if weapon_containers:
            unit["normal_weapons"] = parse_weapons(weapon_containers[0])
            if len(weapon_containers) > 1:
                unit["transformed_weapons"] = parse_weapons(weapon_containers[1])
    else:
        # Try parsing weapons from page directly
        unit["normal_weapons"] = parse_weapons(soup)

    return unit


def main():
    output_path = os.path.join(os.path.dirname(__file__), "public", "units.json")
    progress_path = os.path.join(os.path.dirname(__file__), "scrape_progress.json")

    # Resume support: load previously scraped data
    units = []
    scraped_ids = set()
    if os.path.exists(progress_path):
        with open(progress_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            units = data.get("units", [])
            scraped_ids = set(data.get("scraped_ids", []))
        print(f"Resuming: {len(scraped_ids)} already scraped")

    remaining = [aid for aid in ALL_IDS if aid not in scraped_ids]
    total = len(ALL_IDS)
    skipped = 0
    errors = []

    print(f"Total IDs: {total}, Remaining: {len(remaining)}")

    for i, article_id in enumerate(remaining):
        idx = len(scraped_ids) + i + 1
        try:
            unit = parse_unit_page(article_id)
            if unit:
                units.append(unit)
                print(f"[{idx}/{total}] ✅ {unit['name']} ({unit['rarity']})")
            else:
                skipped += 1
                print(f"[{idx}/{total}] ⏭  {article_id} (not a unit page)")
            scraped_ids.add(article_id)
        except Exception as e:
            errors.append({"id": article_id, "error": str(e)})
            scraped_ids.add(article_id)
            print(f"[{idx}/{total}] ❌ {article_id}: {e}")

        # Save progress every 20 units
        if idx % 20 == 0:
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump({"units": units, "scraped_ids": list(scraped_ids)}, f, ensure_ascii=False)
            print(f"  ... progress saved ({len(units)} units)")

        # Rate limit: 0.5s between requests
        time.sleep(0.5)

    # Final save
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump({"units": units, "scraped_ids": list(scraped_ids)}, f, ensure_ascii=False)

    # Write final units.json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(units, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"Done! Units: {len(units)}, Skipped: {skipped}, Errors: {len(errors)}")
    if errors:
        print("Errors:")
        for e in errors[:10]:
            print(f"  {e['id']}: {e['error']}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
