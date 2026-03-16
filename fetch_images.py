#!/usr/bin/env python3
"""
Bulk fetch missing images from GameWith for units, characters, and supporters.
Type-aware matching to prevent duplicate image assignments.
"""

import requests
import re
import json
import time
import os
import unicodedata
from collections import defaultdict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "ja,en;q=0.9",
}

BASE_IMG = "https://img.gamewith.jp/article_tools/ggene-eternal/gacha"

UNIT_LIST_PAGES = [
    "https://gamewith.jp/ggene-eternal/496188",
]

CHARA_LIST_PAGES = [
    ("https://gamewith.jp/ggene-eternal/494682", "UR"),
    ("https://gamewith.jp/ggene-eternal/496139", "SSR"),
    ("https://gamewith.jp/ggene-eternal/496970", "SR"),
    ("https://gamewith.jp/ggene-eternal/496971", "R"),
]

SUPPORTER_LIST_PAGES = [
    "https://gamewith.jp/ggene-eternal/494683",
    "https://gamewith.jp/ggene-eternal/494689",
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_JSON = os.path.join(SCRIPT_DIR, "public", "units.json")
IMG_DIR = os.path.join(SCRIPT_DIR, "public", "unit-images")


def normalize(s):
    """Normalize for matching."""
    s = s.replace("Ⅳ", "4").replace("Ⅲ", "3").replace("Ⅱ", "2").replace("Ⅰ", "1")
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r'III', '3', s)
    s = re.sub(r'II', '2', s)
    s = s.replace("　", "").replace(" ", "").replace("・", "").replace("-", "").replace("―", "")
    s = re.sub(r'\((UR|SSR|SR|R|N|ULT)[/／][^)]*\)', '', s)
    s = re.sub(r'【[^】]*】', '', s)
    s = s.lower()
    return s


def fetch_page(url):
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  Retry {attempt+1} for {url}: {e}")
            time.sleep(2)
    return None


def get_unit_mapping():
    """Parse window.Gunit from unit list page."""
    print("=== Fetching unit data from GameWith ===")
    mapping = {}
    for url in UNIT_LIST_PAGES:
        html = fetch_page(url)
        if not html:
            continue
        match = re.search(r'window\.Gunit=(\[.*?\]);', html, re.DOTALL)
        if not match:
            continue
        data_str = match.group(1)
        for m in re.finditer(r'\{[^{}]*?id:(\d+)[^{}]*?name:"([^"]*)"[^{}]*?second:"([^"]*)"', data_str):
            gw_id = int(m.group(1))
            name = m.group(2)
            second = m.group(3)
            full_name = f"{name}{second}" if second else name
            mapping[full_name] = {
                "id": gw_id,
                "type": "unit",
                "img_url": f"{BASE_IMG}/unit_{gw_id}.png",
            }
        time.sleep(1)
    print(f"  Found {len(mapping)} units")
    return mapping


def get_chara_mapping():
    """Parse character images with rarity and type info.
    Returns dict: {(base_name, rarity, type): {"id": N, ...}}
    """
    print("=== Fetching character data from GameWith ===")
    from bs4 import BeautifulSoup
    mapping = {}
    for url, default_rarity in CHARA_LIST_PAGES:
        print(f"  Fetching: {url} ({default_rarity})")
        html = fetch_page(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all("img"):
            alt = img.get("alt", "")
            src = img.get("src", img.get("data-src", ""))
            if "chara_" not in src:
                continue
            m = re.search(r"chara_(\d+)", src)
            if not m:
                continue
            cid = int(m.group(1))
            # Parse alt: "キャラ名(RARITY/TYPE)"
            alt_match = re.match(r'^(.+?)\s*\((\w+)/(攻撃|支援|耐久)\)$', alt)
            if alt_match:
                name = alt_match.group(1).strip()
                rarity = alt_match.group(2)
                ctype = alt_match.group(3)
            else:
                name = alt.strip()
                rarity = default_rarity
                ctype = ""
            key = (name, rarity, ctype)
            if key not in mapping:
                mapping[key] = {
                    "id": cid,
                    "type": "chara",
                    "img_url": f"{BASE_IMG}/chara_{cid}.png",
                    "original_name": alt,
                }
        time.sleep(1.5)
    print(f"  Found {len(mapping)} characters (type-aware)")
    return mapping


def get_supporter_mapping():
    """Parse supporter images."""
    print("=== Fetching supporter data from GameWith ===")
    mapping = {}
    for url in SUPPORTER_LIST_PAGES:
        print(f"  Fetching: {url}")
        html = fetch_page(url)
        if not html:
            continue
        for m in re.finditer(r'supporter_(\d+)\.png[^>]*?alt=.([^"\']+)', html):
            img_id = int(m.group(1))
            alt_text = m.group(2).strip()
            if alt_text not in mapping:
                mapping[alt_text] = {
                    "id": img_id,
                    "type": "supporter",
                    "img_url": f"{BASE_IMG}/supporter_{img_id}.png",
                    "original_name": alt_text,
                }
        time.sleep(1.5)
    print(f"  Found {len(mapping)} supporters")
    return mapping


def download_image(url, filepath):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 100:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"  Download error: {e}")
    return False


def match_character(item, chara_map):
    """Match a WikiWiki character to a GameWith character using type+rarity.
    Returns match dict or None.
    """
    name = item["name"]
    rarity = item.get("rarity", "")
    wiki_type = item.get("type", "")

    # Extract type from name: アムロ・レイ(CCA)(攻撃) -> type=攻撃, base=アムロ・レイ(CCA)
    type_match = re.search(r'\((攻撃|支援|耐久)\)$', name)
    char_type = type_match.group(1) if type_match else wiki_type
    base_name = re.sub(r'\((攻撃|支援|耐久)\)$', '', name).strip()
    norm_base = normalize(base_name)

    # Priority 1: Exact name + rarity + type match
    for (gw_name, gw_rarity, gw_type), gw_data in chara_map.items():
        if normalize(gw_name) == norm_base and gw_rarity == rarity and gw_type == char_type:
            return gw_data

    # Priority 2: Exact name + rarity (type mismatch or missing)
    for (gw_name, gw_rarity, gw_type), gw_data in chara_map.items():
        if normalize(gw_name) == norm_base and gw_rarity == rarity:
            return gw_data

    # Priority 3: Exact name, any rarity + type match
    for (gw_name, gw_rarity, gw_type), gw_data in chara_map.items():
        if normalize(gw_name) == norm_base and gw_type == char_type:
            return gw_data

    # Priority 4: Containment match with same rarity
    for (gw_name, gw_rarity, gw_type), gw_data in chara_map.items():
        gw_norm = normalize(gw_name)
        if gw_rarity == rarity and len(norm_base) >= 4 and len(gw_norm) >= 4:
            if norm_base in gw_norm or gw_norm in norm_base:
                score = min(len(norm_base), len(gw_norm)) / max(len(norm_base), len(gw_norm))
                if score > 0.7:
                    return gw_data

    return None


def match_unit(item, unit_map):
    """Match a WikiWiki unit to a GameWith unit."""
    name = item["name"]
    our_norm = normalize(name)

    # Exact match
    for gw_name, gw_data in unit_map.items():
        if normalize(gw_name) == our_norm:
            return gw_data

    # Stripped type suffix match
    stripped = re.sub(r'\((攻撃|支援|耐久|機動)\)$', '', name).strip()
    if stripped != name:
        for gw_name, gw_data in unit_map.items():
            if normalize(gw_name) == normalize(stripped):
                return gw_data

    # Containment match
    best_score = 0
    best_match = None
    for gw_name, gw_data in unit_map.items():
        gw_norm = normalize(gw_name)
        if len(our_norm) >= 4 and len(gw_norm) >= 4:
            if our_norm in gw_norm or gw_norm in our_norm:
                score = min(len(our_norm), len(gw_norm)) / max(len(our_norm), len(gw_norm))
                if score > best_score and score > 0.7:
                    best_score = score
                    best_match = gw_data
    return best_match


def match_supporter(item, supporter_map):
    """Match a WikiWiki supporter to a GameWith supporter."""
    name = item["name"]
    our_norm = normalize(name)

    for gw_name, gw_data in supporter_map.items():
        if normalize(gw_name) == our_norm:
            return gw_data
        stripped = re.sub(r'\((UR|SSR|SR|R|N)[/／][^)]*\)', '', gw_name).strip()
        if normalize(stripped) == our_norm:
            return gw_data

    # Containment match
    best_score = 0
    best_match = None
    for gw_name, gw_data in supporter_map.items():
        gw_norm = normalize(gw_name)
        if len(our_norm) >= 4 and len(gw_norm) >= 4:
            if our_norm in gw_norm or gw_norm in our_norm:
                score = min(len(our_norm), len(gw_norm)) / max(len(our_norm), len(gw_norm))
                if score > best_score and score > 0.6:
                    best_score = score
                    best_match = gw_data
    return best_match


def check_duplicates(data):
    """Check for duplicate image assignments and report."""
    img_map = defaultdict(list)
    for item in data:
        img = item.get("image", "")
        if img:
            img_map[img].append(f"{item.get('rarity','?')} {item['name']}")

    dupes = {k: v for k, v in img_map.items() if len(v) > 1}
    if dupes:
        print(f"\n⚠️  WARNING: {len(dupes)} duplicate image assignments detected!")
        for img, names in sorted(dupes.items()):
            print(f"  {img}:")
            for n in names:
                print(f"    - {n}")
        print()
        return len(dupes)
    else:
        print("\n✅ No duplicate image assignments found.")
        return 0


def main():
    with open(UNITS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    no_img_count = sum(1 for item in data if not item.get("image"))
    print(f"Items without image: {no_img_count} / {len(data)}\n")

    # Check existing duplicates first
    print("=== Pre-check: existing duplicates ===")
    check_duplicates(data)

    # Fetch all GameWith mappings
    unit_map = get_unit_mapping()
    time.sleep(2)
    chara_map = get_chara_mapping()
    time.sleep(2)
    supporter_map = get_supporter_mapping()

    # Match and download
    os.makedirs(IMG_DIR, exist_ok=True)
    matched = 0
    downloaded = 0
    already_had = 0
    failed_download = 0
    unmatched = []

    # Track which image paths are being assigned to detect new duplicates
    assigned_images = defaultdict(list)
    for item in data:
        if item.get("image"):
            assigned_images[item["image"]].append(item["name"])


    for item in data:
        if item.get("image"):
            already_had += 1
            continue

        category = item.get("category", "")
        name = item["name"]

        # Pick matching function based on category
        if category == "supporter":
            match = match_supporter(item, supporter_map)
        elif category == "unit":
            match = match_unit(item, unit_map)
        else:
            match = match_character(item, chara_map)
            if not match:
                match = match_unit(item, unit_map)

        if not match:
            unmatched.append(name)
            continue

        # Build the expected local image path
        img_type = match["type"]  # "unit", "chara", or "supporter"
        img_id = match["id"]
        filename = f"{img_type}_{img_id}.png"
        img_path = f"/unit-images/{filename}"

        # Duplicate prevention: skip if this image is already assigned
        if img_path in assigned_images:
            existing = assigned_images[img_path]
            print(f"  ⚠️  SKIP duplicate: {name} -> {img_path} (already used by: {', '.join(existing)})")
            continue

        # Assign image
        item["image"] = img_path
        assigned_images[img_path].append(name)
        matched += 1

        # Download if file doesn't exist locally
        local_path = os.path.join(IMG_DIR, filename)
        if os.path.exists(local_path):
            print(f"  ✓ {name} -> {img_path} (already downloaded)")
        else:
            print(f"  ↓ {name} -> {img_path} (downloading...)")
            if download_image(match["img_url"], local_path):
                downloaded += 1
            else:
                print(f"    ✗ Failed to download {match['img_url']}")
                item["image"] = ""
                assigned_images[img_path].remove(name)
                if not assigned_images[img_path]:
                    del assigned_images[img_path]
                failed_download += 1

    # Post-assignment duplicate check
    print("\n=== Post-check: duplicate assignments ===")
    dupe_count = check_duplicates(data)

    # Save
    with open(UNITS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved to {UNITS_JSON}")

    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"  Total items:        {len(data)}")
    print(f"  Already had image:  {already_had}")
    print(f"  Newly matched:      {matched}")
    print(f"  Downloaded:         {downloaded}")
    print(f"  Failed downloads:   {failed_download}")
    print(f"  Unmatched:          {len(unmatched)}")
    print(f"  Duplicate images:   {dupe_count}")

    if unmatched:
        print(f"\nUnmatched items ({len(unmatched)}):")
        for n in unmatched:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
