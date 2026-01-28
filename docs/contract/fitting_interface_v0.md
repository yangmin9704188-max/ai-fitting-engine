# Fitting Interface v0

**Purpose**: Artifact-only interface for fitting operations. No implementation imports; all integration via file paths only.

**Schema Version**: `fitting_manifest.v0`

---

## Manifest Structure

### Required Fields

#### `schema_version` (string, const)
- Value: `"fitting_manifest.v0"`

#### `inputs` (object)
- **`units`** (string, enum): `"m"` (meters, required)
- **`body_source`** (object, oneOf exactly one):
  - `geometry_manifest_path` (string)
  - `body_measurements_path` (string)
  - `body_mesh_path` (string)
- **`garment_source`** (object, oneOf exactly one):
  - `garment_template_path` (string)
  - `garment_measurements_path` (string)

#### `outputs` (object)
- **`out_dir`** (string, required): Output directory path

#### `provenance` (object)
- **`schema_version`** (string, const): `"fitting_manifest.v0"`
- **`code_fingerprint`** (string, required): Code version identifier

### Optional Fields

#### `outputs` (continued)
- **`expected_files`** (object): Default names `fitting_summary.json`, `facts_summary.json`
- **`visual_proxy`** (object): `paths` array of strings

#### `provenance` (continued)
- **`input_fingerprints`** (object): Dict of input file fingerprints

---

## Output Files

### `fitting_summary.json`
Facts-only output. NaN allowed. No dropping/clamping to improve metrics. Contains warnings and coverage metrics.

### `facts_summary.json`
Additional facts and diagnostics. Same facts-only principle.

---

## Minimal Example

```json
{
  "schema_version": "fitting_manifest.v0",
  "inputs": {
    "units": "m",
    "body_source": {
      "body_mesh_path": "data/body.obj"
    },
    "garment_source": {
      "garment_template_path": "data/garment.json"
    }
  },
  "outputs": {
    "out_dir": "outputs/run_001"
  },
  "provenance": {
    "schema_version": "fitting_manifest.v0",
    "code_fingerprint": "abc123def"
  }
}
```

---

## Integration Rules

- **No cross-module imports**: Do not import from `modules/body` or `modules/garment` implementation code
- **Path-only communication**: All inputs/outputs via file paths
- **Facts-only**: Report what is, not pass/fail. Use `warnings` and `reasons` fields
- **NaN tolerance**: Do not drop NaN values to inflate coverage metrics
