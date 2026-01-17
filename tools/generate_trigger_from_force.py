#!/usr/bin/env python3
"""Generate triggers.json from force_trigger input for testing."""
import json
import os
import sys

force_trigger = os.environ.get('FORCE_TRIGGER', '')

standard_triggers = [
    "FREEZE_REQUIRED",
    "AUDIT_FAILED",
    "SPEC_CHANGE",
    "UNEXPECTED_ERROR",
    "INSUFFICIENT_EVIDENCE",
    "RISK_HIGH"
]

triggers = {key: False for key in standard_triggers}
if force_trigger in standard_triggers:
    triggers[force_trigger] = True

output = json.dumps(triggers, indent=2, sort_keys=True)
print(output)

with open('triggers.json', 'w') as f:
    json.dump(triggers, f, indent=2, sort_keys=True)
