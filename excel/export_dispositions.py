import csv
import sys

RACE_ID_MAP = {
    "Argonian": "argonian",
    "Breton": "breton",
    "Riverfolk": "t_hr_riverfolk",
    "Dark Elf": "dark elf",
    "High Elf": "high elf",
    "Chimeri-Quey": "t_cnq_chimeriquey",
    "Keptu-Quey": "t_cnq_keptu",
    "Imperial": "imperial",
    "Khajiit": [
        "khajiit",
        "t_els_cathay",
        "t_els_cathay-raht",
        "t_els_dagi-raht",
        "t_els_ohmes",
        "t_els_ohmes-raht",
        "t_els_suthay",
    ],
    "Nord": "nord",
    "Reachmen": "t_sky_reachman",
    "Orc": "orc",
    "Malahk Orc": "t_mw_malahk_orc",
    "Redguard": [
        "redguard",
        "t_yok_duadri"
    ],
    "Wood Elf": "wood elf",
    "Imga": "t_val_imga",
    "Sea Elf": "t_pya_seaelf",
}


def slugify(label: str) -> str:
    return label.strip().lower().replace(" ", "").replace("-", "")


def race_ids(label: str) -> list:
    """Return the list of race ids a spreadsheet label expands to (usually
    length 1, but longer for labels mapped to a list in RACE_ID_MAP)."""
    label = label.strip()
    if label in RACE_ID_MAP:
        mapped = RACE_ID_MAP[label]
        if isinstance(mapped, (list, tuple)):
            return list(mapped)
        return [mapped]
    slug = slugify(label)
    print(
        f"WARNING: no explicit mapping for '{label}', using '{slug}'. "
        f"Add it to RACE_ID_MAP if that's wrong.",
        file=sys.stderr,
    )
    return [slug]


def lua_key(s: str) -> str:
    """Return a Lua table-constructor key: bareword if valid, else ["quoted"]."""
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'["{escaped}"]'


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python export_dispositions.py input.csv output.lua", file=sys.stderr
        )
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    with open(in_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    # First row: header row containing player-race column labels.
    # Column 0 is the "Player ->" label itself, skip it.
    header = rows[0]
    player_labels = header[1:]

    # data[player_race][npc_race] = value
    data = {}

    for row in rows[1:]:
        if not row or not row[0].strip():
            continue
        npc_label = row[0].strip()
        # skip the "NPC v" sub-header row and any trailing notes row
        if npc_label.lower() in ("npc v", "npc↓", "npc down"):
            continue
        if npc_label.startswith("*"):
            continue

        npc_ids = race_ids(npc_label)

        for col_idx, player_label in enumerate(player_labels):
            if not player_label.strip():
                continue
            cell_idx = col_idx + 1
            if cell_idx >= len(row):
                continue
            raw = row[cell_idx].strip()
            if raw == "":
                continue
            try:
                value = int(raw)
            except ValueError:
                try:
                    value = float(raw)
                except ValueError:
                    print(
                        f"WARNING: could not parse '{raw}' at "
                        f"NPC={npc_label!r}, Player={player_label!r}; skipping.",
                        file=sys.stderr,
                    )
                    continue

            player_ids = race_ids(player_label)
            # Expand across every combination of player-side and npc-side
            # subspecies aliases (e.g. all Khajiit subtypes x all Redguard
            # subtypes get the same value).
            for player_id in player_ids:
                for npc_id in npc_ids:
                    data.setdefault(player_id, {})[npc_id] = value

    # --- write Lua ---
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("---@omw-context global|local\n")
        f.write("local dispositions = {\n")
        for player_id in sorted(data.keys()):
            f.write(f"    {lua_key(player_id)} = {{\n")
            for npc_id, value in data[player_id].items():
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                f.write(f"        {lua_key(npc_id)}  = {value},\n")
            f.write("    },\n")
        f.write("}\n\n")
        f.write("return dispositions\n")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
