#!/usr/bin/env python3
"""
アルテマ Gジェネエターナル ユニットデータスクレイパー v3
全ユニット（UR/SSR/SR/R/N）のデータを取得し、units.json形式で出力する。
変形機構にも対応。最大LVデータのみ使用。
"""

import json
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter

BASE_URL = "https://altema.jp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36"
}


# ============================================================
# ユニット一覧ページ
# ============================================================
def fetch_unit_list():
    url = f"{BASE_URL}/ggeneeternal/unitlist"
    print(f"Fetching unit list: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table")
    target_table = tables[2]
    rows = target_table.find_all("tr")
    units = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        name_cell = cells[0]
        link = name_cell.find("a")
        name = name_cell.get_text().strip()
        href = link.get("href", "") if link else ""
        rarity = cells[1].get_text().strip()
        unit_type = cells[2].get_text().strip()
        rating = cells[4].get_text().strip().replace("点", "")
        unit_id = ""
        if "/unit/" in href:
            unit_id = href.split("/unit/")[-1].rstrip("/")
        units.append({
            "name": name, "altema_id": unit_id,
            "altema_url": f"{BASE_URL}{href}" if href else "",
            "rarity": rarity, "unit_type": unit_type, "rating": rating,
        })
    return units


# ============================================================
# 情報テーブルパーサー（シリーズ/タグ/入手方法）
# ============================================================
def parse_info_tables(soup):
    """ページ上部の情報テーブルからシリーズ/タグ/入手方法を抽出"""
    series = []
    tags = []
    obtain_method = ""

    tables = soup.find_all("table")

    for table in tables[:5]:  # 最初の5テーブルのみチェック
        rows = table.find_all("tr")
        mode = None
        for row in rows:
            cells = row.find_all(["td", "th"])
            cell_texts = [c.get_text().strip() for c in cells]

            if len(cells) == 1:
                t = cell_texts[0]
                if t == "シリーズ":
                    mode = "series"
                    continue
                elif t == "タグ":
                    mode = "tags"
                    continue
                else:
                    mode = None

            elif len(cells) == 2:
                k, v = cell_texts
                if k == "入手方法":
                    obtain_method = v
                    continue
                if mode == "series":
                    for val in cell_texts:
                        val = val.strip()
                        if val and val != "-":
                            series.append(val)
                elif mode == "tags":
                    for val in cell_texts:
                        val = val.strip()
                        if val and val != "-":
                            tags.append(val)

    return series, tags, obtain_method


# ============================================================
# 武装テーブルパーサー
# ============================================================
def parse_weapons_table(table):
    """1つの武装テーブルから最大LVの全武装をパース"""
    rows = table.find_all("tr")
    if not rows:
        return []

    # LV1と最大LVのrow IDパターンを特定
    lv1_ids = set()
    max_ids = set()
    for r in rows:
        rid = r.get("id", "")
        if rid.startswith("tab_LV1"):
            lv1_ids.add(rid)
        elif rid and rid.startswith("tab_"):
            max_ids.add(rid)

    # 最大LVのIDで絞る（なければ全行）
    target_id = list(max_ids)[0] if max_ids else (list(lv1_ids)[0] if lv1_ids else None)

    if target_id:
        filtered_rows = [r for r in rows if r.get("id", "") == target_id]
    else:
        filtered_rows = rows

    weapons = []
    cur = None

    for row in filtered_rows:
        cells = row.find_all(["th", "td"])
        txts = [c.get_text().strip() for c in cells]

        if len(cells) == 1:
            # 武装名行（colspan=4）
            if cur and cur.get("name"):
                weapons.append(cur)
            cur = _new_weapon()
            name_text = txts[0]
            # 属性抽出: "武装名 <ビーム>"
            m = re.search(r"[<＜](.+?)[>＞]", name_text)
            if m:
                cur["attribute"] = m.group(1)
                sep = "<" if "<" in name_text else "＜"
                cur["name"] = name_text[:name_text.index(sep)].strip()
            else:
                cur["name"] = name_text

        elif len(cells) == 4 and cur:
            k1, v1, k2, v2 = txts
            if k1 == "武装タイプ":
                cur["attack_type"] = v1
                if k2 == "RANGE":
                    _parse_range(cur, v2)
            elif k1 == "POWER":
                cur["power"] = v1.replace(",", "")
                if k2 == "EN":
                    cur["en"] = v2.replace(",", "")
            elif k1 == "命中":
                cur["hit"] = v1
                if k2 == "クリティカル":
                    cur["critical"] = v2

        elif len(cells) == 2 and cur:
            k, v = txts
            if k == "武装効果":
                cur["weapon_effect"] = v
            elif k == "使用制限":
                cur["use_limit"] = v
            elif k == "使用回数":
                cur["use_count"] = v

    if cur and cur.get("name"):
        weapons.append(cur)

    return weapons


def _new_weapon():
    return {
        "name": "", "attribute": "", "attack_type": "",
        "range_min": "", "range_max": "",
        "power": "", "en": "", "hit": "", "critical": "",
        "is_map": False, "is_ex": False,
        "weapon_effect": "", "use_limit": "", "use_count": None,
    }


def _parse_range(weapon, range_str):
    """RANGE値をパース。"MAP" / "1/2" / "2/5" / "1" etc."""
    r = range_str.strip()
    if not r or r == "-":
        weapon["range_min"] = ""
        weapon["range_max"] = ""
        return
    if r == "MAP":
        weapon["is_map"] = True
        weapon["range_min"] = "MAP"
        weapon["range_max"] = "MAP"
        return
    # MAP付きの場合: "MAP1/3" etc.
    if r.startswith("MAP"):
        weapon["is_map"] = True
        r = r[3:]
    if "/" in r:
        parts = r.split("/")
        weapon["range_min"] = parts[0]
        weapon["range_max"] = parts[1]
    else:
        weapon["range_min"] = r
        weapon["range_max"] = r


# ============================================================
# ステータステーブルパーサー
# ============================================================
def parse_stats_table(table):
    """最大LVのステータスと戦闘力を抽出"""
    rows = table.find_all("tr")
    stat_map = {
        "HP": "hp", "攻撃力": "attack", "EN": "en",
        "防御力": "defense", "移動力": "mobility", "機動力": "agility"
    }
    stats_max = {}
    cp_max = ""

    for row in rows:
        rid = row.get("id", "")
        if rid == "tab_LV1":
            continue  # LV1データはスキップ（"tab_LV100"を誤スキップしないよう完全一致）
        cells = row.find_all(["th", "td"])
        txts = [c.get_text().strip() for c in cells]

        if len(cells) == 1:
            m = re.search(r"戦闘力([\d,]+)", txts[0])
            if m:
                cp_max = m.group(1).replace(",", "")
        elif len(cells) == 4:
            k1, v1, k2, v2 = txts
            if k1 in stat_map:
                stats_max[stat_map[k1]] = v1.replace(",", "")
            if k2 in stat_map:
                stats_max[stat_map[k2]] = v2.replace(",", "")

    return stats_max, cp_max


# ============================================================
# 地形適性 & 機構パーサー
# ============================================================
def parse_terrain_and_mechanisms(soup):
    """地形適性テーブルから地形と機構を抽出"""
    terrain = {"space": "-", "air": "-", "ground": "-", "surface": "-", "water": "-"}
    terrain_map = {"宇宙": "space", "空中": "air", "地上": "ground", "水上": "surface", "水中": "water"}
    mechanisms = []

    for tab in soup.find_all("div", class_="tab-change-area"):
        table = tab.find("table")
        if not table:
            continue
        first_text = table.find("tr").get_text().strip() if table.find("tr") else ""
        if "地形適性" not in first_text:
            continue

        rows = table.find_all("tr")
        mode = None
        for row in rows:
            cells = row.find_all(["td", "th"])
            txts = [c.get_text().strip() for c in cells]

            if len(cells) == 1:
                t = txts[0]
                if "地形適性" in t:
                    mode = "terrain_header"
                elif "機構" in t:
                    mode = "mechanism"
                continue

            # 地形キー行 (5セル: 宇宙,空中,地上,水上,水中)
            if len(cells) == 5 and mode == "terrain_header":
                if txts[0] in terrain_map:
                    mode = "terrain_header"  # これはキー行
                else:
                    # 値行
                    keys = ["宇宙", "空中", "地上", "水上", "水中"]
                    for k, v in zip(keys, txts):
                        v = v.replace("●", "◯").replace("▲", "△")
                        terrain[terrain_map[k]] = v
                    mode = None

            # 機構行 (2セル)
            if len(cells) == 2 and mode == "mechanism":
                rid = row.get("id", "")
                # tab_base のみ（変形前）
                if rid and "tab_" in rid and "base" not in rid:
                    continue
                name, effect = txts
                if name and name not in ["機構", "名称"]:
                    mechanisms.append({"name": name, "effect": effect})

        return terrain, mechanisms

    return terrain, mechanisms


# ============================================================
# アビリティ/スキルパーサー
# ============================================================
def parse_abilities(soup):
    """articleDiv内のスタンドアロンテーブルからアビリティを抽出。
    1セル行が交互: 名前行, 効果行, 名前行, 効果行..."""
    abilities = []

    # tab-change-area外のテーブルを探す
    for table in soup.find_all("table"):
        # tab-change-area内は除外
        if table.find_parent("div", class_="tab-change-area"):
            continue
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue
        # 全行が1セルのテーブルかチェック
        all_single = all(len(r.find_all(["td", "th"])) == 1 for r in rows)
        if not all_single:
            continue
        # 偶数行（名前/効果ペア）かチェック
        if len(rows) % 2 != 0:
            continue
        # 先頭がスキップ対象でないか
        first = rows[0].get_text().strip()
        if any(k in first for k in ["関連記事", "おすすめキャラ", "記事を書いた"]):
            continue

        for i in range(0, len(rows), 2):
            name = rows[i].get_text().strip()
            effect = rows[i+1].get_text().strip() if i+1 < len(rows) else ""
            # CSSクラスからアビリティ名判定（背景色付き行）
            if name and effect:
                abilities.append({"name": name, "effect": effect})

    return abilities


# ============================================================
# ユニットアイコン取得
# ============================================================
def find_unit_icon(soup):
    og = soup.find("meta", property="og:image")
    if og:
        url = og.get("content", "")
        if url and "1x1" not in url:
            return url
    return ""


# ============================================================
# メイン詳細ページパーサー
# ============================================================
def parse_unit_detail(html, unit_info):
    soup = BeautifulSoup(html, "html.parser")

    # 情報テーブル
    series, tags, obtain_method = parse_info_tables(soup)

    result = {
        "name": unit_info["name"],
        "rarity": unit_info["rarity"],
        "unit_type": unit_info["unit_type"],
        "altema_id": unit_info["altema_id"],
        "source_url": unit_info["altema_url"],
        "rating": unit_info["rating"],
        "icon_url": find_unit_icon(soup),
        "series": series,
        "tags": tags,
        "obtain_method": obtain_method,
    }

    # 地形適性 & 機構
    terrain, mechanisms = parse_terrain_and_mechanisms(soup)

    # アビリティ
    abilities = parse_abilities(soup)
    result["abilities"] = abilities
    result["skills"] = []  # アルテマではスキル/アビリティの区別なし
    result["mechanisms"] = mechanisms

    # 変形判定
    transform_areas = soup.find_all("div", class_="transform-area")
    has_transform = any("transform" in ta.get("class", []) for ta in transform_areas)

    # tab-change-areaを収集
    tab_areas = soup.find_all("div", class_="tab-change-area")

    if has_transform:
        result["has_transform"] = True
        forms = parse_transform_unit(soup, transform_areas, tab_areas, terrain)
        result["forms"] = forms
    else:
        result["has_transform"] = False
        form = parse_normal_unit(tab_areas, terrain)
        result["forms"] = [form]

    return result


def _is_weapon_table(table):
    """武装テーブルかどうか判定"""
    first_text = table.get_text()[:200] if table else ""
    return any(kw in first_text for kw in ["<ビーム>", "<物理>", "<特殊>", "武装タイプ", "POWER"])


def _is_stats_table(table):
    """ステータステーブルかどうか判定"""
    text = table.get_text()[:200] if table else ""
    return "戦闘力" in text and ("HP" in text or "攻撃力" in text)


def parse_normal_unit(tab_areas, terrain):
    """変形なしユニット"""
    form = {
        "form_name": "通常",
        "terrain": terrain,
        "stats": {},
        "combat_power": "",
        "weapons": [],
    }

    for tab in tab_areas:
        table = tab.find("table")
        if not table:
            continue
        first_text = table.find("tr").get_text().strip() if table.find("tr") else ""
        if "地形適性" in first_text:
            continue

        if _is_stats_table(table):
            stats, cp = parse_stats_table(table)
            form["stats"] = stats
            form["combat_power"] = cp
        elif _is_weapon_table(table):
            weapons = parse_weapons_table(table)
            form["weapons"] = weapons

    # EX武装判定の強化: 名前にEXを含むか最終武装かで判定
    for w in form["weapons"]:
        raw = w["name"]
        w["is_ex"] = raw.endswith("EX") or bool(re.search(r"EX$", raw.split("(")[0].split("（")[0] if raw else ""))
        # is_map: rangeから判定済み
        # 名前に(MAP)が含まれる場合も
        if re.search(r"\(MAP\)|（MAP）", raw):
            w["is_map"] = True
            w["name"] = re.sub(r"\s*[\(（]MAP[\)）]", "", raw)

    return form


def parse_transform_unit(soup, transform_areas, tab_areas, terrain):
    """変形ユニット: 変形前/変形後のデータを分割取得"""
    all_weapon_tables = []
    all_stat_tables = []

    for tab in tab_areas:
        table = tab.find("table")
        if not table:
            continue
        first_text = table.find("tr").get_text().strip() if table.find("tr") else ""
        if "地形適性" in first_text:
            continue
        if _is_stats_table(table):
            all_stat_tables.append(table)
        elif _is_weapon_table(table):
            all_weapon_tables.append(table)

    forms = []
    # 変形前
    form_base = {"form_name": "変形前", "terrain": terrain, "stats": {}, "combat_power": "", "weapons": []}
    if all_weapon_tables:
        form_base["weapons"] = parse_weapons_table(all_weapon_tables[0])
    if all_stat_tables:
        s, cp = parse_stats_table(all_stat_tables[0])
        form_base["stats"] = s
        form_base["combat_power"] = cp
    forms.append(form_base)

    # 変形後
    form_tf = {"form_name": "変形後", "terrain": terrain, "stats": {}, "combat_power": "", "weapons": []}
    if len(all_weapon_tables) >= 2:
        form_tf["weapons"] = parse_weapons_table(all_weapon_tables[1])
    if len(all_stat_tables) >= 2:
        s, cp = parse_stats_table(all_stat_tables[1])
        form_tf["stats"] = s
        form_tf["combat_power"] = cp
    forms.append(form_tf)

    # EX/MAP判定
    for form in forms:
        for w in form["weapons"]:
            raw = w["name"]
            w["is_ex"] = raw.endswith("EX") or bool(re.search(r"EX$", raw.split("(")[0] if raw else ""))
            if re.search(r"\(MAP\)|（MAP）", raw):
                w["is_map"] = True
                w["name"] = re.sub(r"\s*[\(（]MAP[\)）]", "", raw)

    return forms


# ============================================================
# 出力変換
# ============================================================
def convert_to_output(unit_data):
    """units.json互換フォーマット"""
    main_form = unit_data["forms"][0] if unit_data["forms"] else {}

    output = {
        "name": unit_data["name"],
        "rarity": unit_data["rarity"],
        "unit_type": unit_data["unit_type"],
        "obtain_method": unit_data.get("obtain_method", ""),
        "series": unit_data.get("series", []),
        "tags": unit_data.get("tags", []),
        "stats": main_form.get("stats", {}),
        "combat_power": main_form.get("combat_power", ""),
        "terrain": main_form.get("terrain", {}),
        "weapons": main_form.get("weapons", []),
        "abilities": unit_data.get("abilities", []),
        "skills": unit_data.get("skills", []),
        "mechanisms": unit_data.get("mechanisms", []),
        "source_url": unit_data.get("source_url", ""),
        "icon_url": unit_data.get("icon_url", ""),
        "altema_id": unit_data.get("altema_id", ""),
        "rating": unit_data.get("rating", ""),
        "has_transform": unit_data.get("has_transform", False),
    }

    if unit_data.get("has_transform") and len(unit_data.get("forms", [])) > 1:
        tf = unit_data["forms"][1]
        output["transform_form"] = {
            "form_name": tf.get("form_name", "変形後"),
            "stats": tf.get("stats", {}),
            "combat_power": tf.get("combat_power", ""),
            "terrain": tf.get("terrain", {}),
            "weapons": tf.get("weapons", []),
        }

    return output


# ============================================================
# メイン
# ============================================================
def main():
    print("=== Step 1: Fetching unit list ===")
    unit_list = fetch_unit_list()
    print(f"Found {len(unit_list)} units")
    rarity_count = Counter(u["rarity"] for u in unit_list)
    print(f"Rarity: {dict(rarity_count)}")

    # フィルタ
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_units = []
            seen = set()
            for u in unit_list:
                if u["rarity"] not in seen:
                    test_units.append(u)
                    seen.add(u["rarity"])
            # 変形ユニット追加
            for u in unit_list:
                if u["altema_id"] == "145":
                    if u not in test_units:
                        test_units.append(u)
                    break
            unit_list = test_units
            print(f"Test mode: {len(unit_list)} units")
        elif sys.argv[1] == "--rarity":
            r = sys.argv[2] if len(sys.argv) > 2 else "UR"
            unit_list = [u for u in unit_list if u["rarity"] == r]
            print(f"Filter rarity={r}: {len(unit_list)} units")
        elif sys.argv[1] == "--id":
            uid = sys.argv[2] if len(sys.argv) > 2 else "1"
            unit_list = [u for u in unit_list if u["altema_id"] == uid]
            print(f"Filter id={uid}: {len(unit_list)} units")

    # 詳細取得
    print(f"\n=== Step 2: Fetching {len(unit_list)} unit details ===")
    results = []
    errors = []

    for i, info in enumerate(unit_list):
        url = info["altema_url"]
        if not url:
            errors.append({"name": info["name"], "error": "No URL"})
            continue

        print(f"[{i+1}/{len(unit_list)}] {info['name']} ({info['rarity']})")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()

            if "unitlist" in resp.url or resp.url.rstrip("/") == f"{BASE_URL}/ggeneeternal":
                errors.append({"name": info["name"], "error": "Redirected"})
                print(f"  ⚠ Redirected, skip")
                continue

            data = parse_unit_detail(resp.text, info)
            output = convert_to_output(data)
            results.append(output)

            wc = len(output["weapons"])
            has_s = bool(output["stats"])
            sr = f"series={len(output['series'])}"
            tg = f"tags={len(output['tags'])}"
            ab = f"abilities={len(output['abilities'])}"
            mc = f"mechs={len(output['mechanisms'])}"
            tf = ""
            if output["has_transform"]:
                tf_form = output.get("transform_form", {})
                tf = f" | 変形後: w={len(tf_form.get('weapons',[]))}"
            print(f"  ✓ w={wc} stats={'OK' if has_s else 'MISS'} {sr} {tg} {ab} {mc}{tf}")

        except Exception as e:
            errors.append({"name": info["name"], "error": str(e)})
            print(f"  ✗ {e}")

        time.sleep(0.5)

    # 保存
    print(f"\n=== Step 3: Save ===")
    print(f"Success: {len(results)}, Errors: {len(errors)}")

    out = "/Users/RH/Documents/5.File/5.Dev/GGeneDB/public/units.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved: {out}")

    if errors:
        ep = "/Users/RH/Documents/5.File/5.Dev/GGeneDB/scrape_errors.json"
        with open(ep, "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
        print(f"Errors: {ep}")


if __name__ == "__main__":
    main()
