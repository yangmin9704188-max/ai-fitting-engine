# Tools

## sync_state.py

Patch `docs/sync/CURRENT_STATE.md` with whitelisted key-value pairs.

### Usage

```bash
# Basic usage - set single value
python tools/sync_state.py --set snapshot.status=candidate

# Multiple patches
python tools/sync_state.py --set snapshot.status=candidate --set last_update.trigger=ci_guard_update

# Custom file path
python tools/sync_state.py --file docs/sync/CURRENT_STATE.md --set pipeline.position=rd

# Dry-run (preview changes without applying)
python tools/sync_state.py --set snapshot.status=hold --dry-run

# YAML value parsing (automatically handles booleans, numbers, lists, dicts)
python tools/sync_state.py --set snapshot.version_keys.snapshot=true
python tools/sync_state.py --set constraints.technical="[item1, item2]"
```

### Notes

- Only whitelisted paths are allowed (see script for full list)
- Values are parsed as YAML (supports bool, int, float, list, dict, string)
- No semantic validation is performed - only path whitelist and type safety checks
