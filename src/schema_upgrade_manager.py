# schema_upgrade_manager.py

def upgrade_v1_to_v2(ws):
    """
    Upgrade metadata structure from schema v1 to v2.
    Example: add new meta fields, rename keys, normalize formats.
    """
    # Example logic (adapt for your actual worksheet/data structure):
    for row in ws.iter_rows(min_row=2, max_col=1):
        key = row[0].value
        if key == "Schema_Version":
            row[0].offset(column=1).value = "v2"
        # Add new keys if missing
    ws.append(["Data_Hash", "Not calculated", "Added in v2"])
    return ws

# Add future schema upgrades here as needed
UPGRADERS = {
    ("v1", "v2"): upgrade_v1_to_v2,
}

def apply_schema_upgrade(ws, current_version, target_version):
    upgrader = UPGRADERS.get((current_version, target_version))
    if upgrader:
        ws = upgrader(ws)
        return ws, f"Schema upgraded: {current_version} ➜ {target_version}"
    else:
        return ws, f"No upgrade path from {current_version} to {target_version}"
