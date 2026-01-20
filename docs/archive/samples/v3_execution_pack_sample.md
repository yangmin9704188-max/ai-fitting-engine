# Human Summary
This is a sample v3 Execution Pack for testing the auto-executor.
It creates a marker file in docs/samples/ to verify file creation,
command execution, and commit generation. This is a safe test that
only modifies files within the docs/samples/ directory.

# Cursor Execution Prompt

## Prerequisites
None required for this test.

## Scope Lock
Only allow editing files in `docs/samples/`.
Forbidden: any change outside `docs/samples/` directory.

## Step 1: Create marker file
**File**: `docs/samples/v3_sample_marker.txt`
**Action**: Create new file with test marker content
**Command**: 
```bash
py -c "from datetime import datetime; open('docs/samples/v3_sample_marker.txt', 'w').write('v3 executor test marker - created at ' + datetime.now().isoformat())"
```

**Expected Output**:
- File: `docs/samples/v3_sample_marker.txt` must exist
- File size: > 0 bytes

**Verification**:
```bash
py -c "import os; assert os.path.exists('docs/samples/v3_sample_marker.txt'), 'Marker file not created'; assert os.path.getsize('docs/samples/v3_sample_marker.txt') > 0, 'Marker file is empty'"
```

## Step 2: Verify marker file content
**File**: None (verification only)
**Action**: Verify marker file contains expected content
**Command**: 
```bash
py -c "content = open('docs/samples/v3_sample_marker.txt', 'r').read(); assert 'v3 executor test marker' in content, 'Marker content mismatch'"
```

**Expected Output**:
- Command exit code: 0
- Command output: No error message

**Verification**:
```bash
py -c "print('Step 2 verification passed')"
```

## Final Verification
```bash
py -c "import os; assert os.path.exists('docs/samples/v3_sample_marker.txt'), 'Final verification failed: marker file missing'"
```

# Stop Triggers
```json
{
  "FREEZE_REQUIRED": {
    "condition": "If any file outside docs/samples/ is modified",
    "human_message": "Scope lock violation detected. Only docs/samples/ files should be modified.",
    "severity": "ERROR",
    "requires_approval": true
  },
  "UNEXPECTED_ERROR": {
    "condition": "If marker file creation fails or verification commands fail",
    "human_message": "Test execution failed. Check command output for details.",
    "severity": "ERROR",
    "requires_approval": false
  }
}
```
