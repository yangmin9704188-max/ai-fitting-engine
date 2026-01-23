# Curated v0 Warnings Schema

Warning format specification for curated_v0 dataset generation.

## Warning Entry Format

Each warning is a JSON object with the following structure:

```json
{
  "source": "7th|8th_direct|8th_3d|system|unknown",
  "file": "file_path_or_name",
  "column": "standard_key_or_all",
  "reason": "reason_code",
  "row_index": null_or_integer,
  "original_value": null_or_value,
  "sentinel_value": "optional_sentinel_value_for_SENTINEL_MISSING",
  "details": "human_readable_description"
}
```

## Fields

- **source**: Source identifier (file source or "system" for pipeline-level warnings)
- **file**: File path or name where the issue occurred
- **column**: Standard key column name, or "all" for file-level issues
- **reason**: Reason code (see below)
- **row_index**: Row index (0-based) if applicable, null otherwise
- **original_value**: Original value that caused the warning, null if not applicable
- **sentinel_value**: (Optional) Sentinel value that was replaced (e.g., "9999" or "" for SENTINEL_MISSING)
- **details**: Human-readable description of the warning

## Reason Codes

- `column_not_present`: Column is not present in the source (mapped as `present: false`)
- `column_not_found`: Column name exists in mapping but not found in DataFrame
- `file_not_found`: Source file does not exist
- `file_load_failed`: Failed to load source file
- `unit_undetermined`: Could not determine source unit for column
- `unit_conversion_failed`: Unit conversion failed (invalid unit or conversion error)
- `unit_conversion_applied`: Unit conversion was applied (provenance record)
- `value_missing`: Missing values (NaN) in column (excludes cases already recorded as SENTINEL_MISSING)
- `SENTINEL_MISSING`: Sentinel value (9999 for 8th_direct, empty string for 7th/8th_3d) replaced with NaN
- `numeric_parsing_failed`: Numeric parsing failed after preprocessing (e.g., comma removal in 7th)
- `OUTLIER_RULES_NOT_FOUND`: No explicit outlier removal rules found in codebase
- `age_filter_applied`: Age filter (20-59) was applied
- `no_data_processed`: No data was successfully processed from any source

## Output Format

Warnings are saved as JSONL (JSON Lines) format:
- One JSON object per line
- UTF-8 encoding
- Each line is a valid JSON object

## Example

```json
{"source": "7th", "file": "data/raw/sizekorea_raw/7th_data.csv", "column": "HUMAN_ID", "reason": "column_not_present", "row_index": null, "original_value": null, "details": "Column 'null' not mapped in 7th"}
{"source": "7th", "file": "data/raw/sizekorea_raw/7th_data.csv", "column": "HEIGHT_M", "reason": "unit_conversion_applied", "row_index": null, "original_value": null, "details": "PROVENANCE: mm_to_m, quantization=0.001m"}
{"source": "system", "file": "build_curated_v0.py", "column": "all", "reason": "OUTLIER_RULES_NOT_FOUND", "row_index": null, "original_value": null, "details": "No explicit outlier removal rules found in codebase. Outlier removal step skipped."}
```
