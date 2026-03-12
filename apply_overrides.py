#!/usr/bin/env python3
"""
apply_overrides.py
overrides.json の手動補正データを public/units.json に適用するスクリプト。

使い方:
  python3 apply_overrides.py

overrides.json のフォーマット:
{
  "units": [
    {
      "name": "ユニット名",
      "overrides": {
        "stats": { "hp": "999999", ... },           # ステータス上書き
        "weapons": [                                  # 武装の部分上書き
          {
            "match": { "name": "武装名", "is_map": true },  # マッチ条件
            "set": { "use_count": 1 }                        # 上書き値
          }
        ],
        "abilities": [ ... ],                         # アビリティ全置換
        "mechanisms": [ ... ],                        # 機構全置換
        "terrain": { "space": "◯", ... }              # 地形全置換
      }
    }
  ]
}
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_PATH = os.path.join(SCRIPT_DIR, "public", "units.json")
OVERRIDES_PATH = os.path.join(SCRIPT_DIR, "overrides.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → 保存完了: {path}")


def weapon_matches(weapon, match_cond):
    """武装がマッチ条件に合致するか判定"""
    for key, val in match_cond.items():
        if weapon.get(key) != val:
            return False
    return True


def apply_unit_overrides(unit, overrides):
    """1ユニットに対してオーバーライドを適用"""
    changes = 0

    # stats 上書き
    if "stats" in overrides:
        for k, v in overrides["stats"].items():
            old = unit.get("stats", {}).get(k)
            if old != v:
                unit.setdefault("stats", {})[k] = v
                print(f"    stats.{k}: {old} → {v}")
                changes += 1

    # combat_power 上書き
    if "combat_power" in overrides:
        old = unit.get("combat_power")
        unit["combat_power"] = overrides["combat_power"]
        if old != overrides["combat_power"]:
            print(f"    combat_power: {old} → {overrides['combat_power']}")
            changes += 1

    # terrain 上書き
    if "terrain" in overrides:
        unit["terrain"] = overrides["terrain"]
        print(f"    terrain: 全置換")
        changes += 1

    # weapons 部分上書き
    if "weapons" in overrides:
        for wo in overrides["weapons"]:
            match_cond = wo["match"]
            set_vals = wo["set"]
            matched = False
            for weapon in unit.get("weapons", []):
                if weapon_matches(weapon, match_cond):
                    matched = True
                    for k, v in set_vals.items():
                        old = weapon.get(k)
                        weapon[k] = v
                        if old != v:
                            print(f"    武装[{weapon['name']}].{k}: {old} → {v}")
                            changes += 1
            if not matched:
                print(f"    ⚠ 武装マッチなし: {match_cond}")

    # abilities 全置換
    if "abilities" in overrides:
        unit["abilities"] = overrides["abilities"]
        print(f"    abilities: 全置換 ({len(overrides['abilities'])}件)")
        changes += 1

    # mechanisms 全置換
    if "mechanisms" in overrides:
        unit["mechanisms"] = overrides["mechanisms"]
        print(f"    mechanisms: 全置換 ({len(overrides['mechanisms'])}件)")
        changes += 1

    return changes


def main():
    if not os.path.exists(OVERRIDES_PATH):
        print("overrides.json が見つかりません。スキップします。")
        sys.exit(0)

    units = load_json(UNITS_PATH)
    overrides_data = load_json(OVERRIDES_PATH)

    unit_map = {u["name"]: u for u in units}
    total_changes = 0

    for ov in overrides_data.get("units", []):
        name = ov["name"]
        print(f"\n[{name}]")
        if name not in unit_map:
            print(f"  ⚠ ユニットが見つかりません: {name}")
            continue

        changes = apply_unit_overrides(unit_map[name], ov.get("overrides", {}))
        total_changes += changes
        if changes == 0:
            print("  変更なし（既に適用済み）")

    if total_changes > 0:
        save_json(UNITS_PATH, units)
        print(f"\n合計 {total_changes} 件の変更を適用しました。")
    else:
        print("\n変更はありませんでした。")


if __name__ == "__main__":
    main()
