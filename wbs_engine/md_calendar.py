from __future__ import annotations

import re
from datetime import date, datetime

from wbs_engine.config import load_json
from wbs_engine.models import CellPatch, Confidence, MdDeadline, WbsRow


def rgb_tuple(color: dict | None) -> tuple[float, float, float] | None:
    if not color:
        return None
    r = color.get("red", 0)
    g = color.get("green", 0)
    b = color.get("blue", 0)
    return (float(r), float(g), float(b))


def match_color_key(rgb: tuple[float, float, float], semantics: dict) -> str | None:
    for key, spec in semantics.items():
        target = spec.get("rgb", [])
        tol = float(spec.get("tolerance", 0.05))
        if len(target) != 3:
            continue
        if all(abs(rgb[i] - float(target[i])) <= tol for i in range(3)):
            return key
    return None


def _parse_day_header(values: list[list[str]], col_idx: int) -> date | None:
    if len(values) < 2:
        return None
    day_row = values[1] if len(values) > 1 else []
    if col_idx >= len(day_row):
        return None
    day_txt = str(day_row[col_idx]).strip()
    if not day_txt.isdigit():
        return None
    month_hint = ""
    for row_idx in (0, 1):
        row = values[row_idx] if row_idx < len(values) else []
        for c in range(col_idx, -1, -1):
            if c < len(row):
                cell = str(row[c]).strip()
                if "年" in cell:
                    m = re.search(r"(\d{4})年(\d{1,2})月", cell)
                    if m:
                        month_hint = f"{m.group(1)}-{int(m.group(2)):02d}"
                        break
        if month_hint:
            break
    if not month_hint:
        return None
    y, m = month_hint.split("-")
    try:
        return date(int(y), int(m), int(day_txt))
    except ValueError:
        return None


def parse_md_grid(
    grid_rows: list[list[dict]],
    values: list[list[str]],
    semantics: dict | None = None,
) -> list[MdDeadline]:
    semantics = semantics or load_json("color_semantics.json")
    deadlines: list[MdDeadline] = []

    for r_idx, grid_row in enumerate(grid_rows):
        if r_idx < 4:
            continue
        val_row = values[r_idx] if r_idx < len(values) else []
        year = str(val_row[0]).strip() if val_row else ""
        season = str(val_row[1]).strip() if len(val_row) > 1 else ""
        brand = str(val_row[2]).strip() if len(val_row) > 2 else ""
        buyer = str(val_row[3]).strip() if len(val_row) > 3 else ""
        stage = str(val_row[4]).strip() if len(val_row) > 4 else ""
        if not brand:
            continue

        for c_idx, cell in enumerate(grid_row):
            fmt = cell.get("effectiveFormat", {}) or cell.get("userEnteredFormat", {})
            bg = fmt.get("backgroundColor") or fmt.get("backgroundColorStyle", {}).get("rgbColor")
            rgb = rgb_tuple(bg)
            if not rgb or rgb == (1.0, 1.0, 1.0):
                continue
            color_key = match_color_key(rgb, semantics)
            if not color_key or color_key not in semantics:
                continue
            role = semantics[color_key].get("role")
            if role != "md_deadline":
                continue
            d = _parse_day_header(values, c_idx)
            if not d:
                continue
            deadlines.append(
                MdDeadline(
                    year=year or str(d.year),
                    season=season,
                    brand=brand,
                    buyer=buyer,
                    stage=stage,
                    date=d.strftime("%Y/%m/%d"),
                    md_row=r_idx + 1,
                    md_col=c_idx + 1,
                    color_key=color_key,
                    rgb=rgb,
                )
            )
    return deadlines


def normalize_brand(name: str, aliases: dict | None = None) -> str:
    aliases = aliases or load_json("brand_aliases.json")
    n = name.strip()
    if n in aliases:
        return aliases[n]
    lower_map = {k.lower(): v for k, v in aliases.items()}
    return lower_map.get(n.lower(), n)


def wbs_key_for_md(brand: str, season: str) -> str:
    b = normalize_brand(brand)
    if season:
        return f"{b}：{season}"
    return b


def md_to_wbs_patches(deadlines: list[MdDeadline], wbs_rows: list[WbsRow]) -> list[CellPatch]:
    patches: list[CellPatch] = []
    by_key: dict[str, WbsRow] = {}
    for row in wbs_rows:
        if row.is_md_brand_row and row.action not in {"", "MDを期日入れる"}:
            by_key[row.project] = row

    for dl in deadlines:
        key = wbs_key_for_md(dl.brand, dl.season)
        target = by_key.get(key)
        if not target:
            for row in wbs_rows:
                if row.is_md_brand_row and normalize_brand(row.project.split("：")[0]) == normalize_brand(dl.brand):
                    if dl.season and dl.season in row.project:
                        target = row
                        break
        if not target:
            continue
        if target.due == dl.date:
            continue
        patches.append(
            CellPatch(
                sheet_row=target.sheet_row,
                column="due",
                old_value=target.due,
                new_value=dl.date,
                reason=(
                    f"BSOMD row{dl.md_row} col{dl.md_col} {dl.color_key} "
                    f"rgb={dl.rgb} buyer={dl.buyer or 'unknown'}"
                ),
                confidence=Confidence.HIGH,
                source=f"BSOMDスケジュール {dl.year} {dl.season} {dl.brand}",
            )
        )
        memo_reason = (
            f"Calendar: BSOMD row{dl.md_row}={dl.date} "
            f"（塗り {dl.color_key} WBS-cloud {datetime.now().strftime('%Y/%m/%d')}）"
        )
        patches.append(
            CellPatch(
                sheet_row=target.sheet_row,
                column="memo",
                old_value=target.memo,
                new_value=memo_reason if not target.memo else f"{target.memo} | {memo_reason}",
                reason="MDカレンダー同期メモ",
                confidence=Confidence.HIGH,
            )
        )
    return patches
