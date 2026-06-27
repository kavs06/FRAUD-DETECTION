# Multi-Agent Investigation API

## Overview

The Multi-Agent Investigation module extends the ML fraud detection pipeline with a structured, rule-based investigation workflow. After the ensemble model assigns a fraud probability to each provider, providers above a configurable threshold are analyzed by four cooperating agents. The module produces JSON investigation reports designed for downstream consumption by GenAI Explainability, RAG chatbots, dashboards, and backend services.

The default execution path (`FraudInvestigationCrew.investigate`) is **deterministic** — it does not require an LLM API key. An optional CrewAI LLM path (`run_crew`) is available for future Gemini integration.

---

## Input

### `provider_df` (required)

Pandas DataFrame with one row per provider. Must include at minimum:

| Column | Description |
|--------|-------------|
| `Provider` | Unique provider identifier |
| `TotalClaims` | Total claim count |
| `UniquePatients` | Distinct beneficiary count |
| `InpatientRatio` | Share of inpatient claims |

Additional ML feature columns (reimbursement, duration, demographics, etc.) improve agent analysis quality.

### `fraud_probabilities` (required)

Pandas DataFrame with:

| Column | Description |
|--------|-------------|
| `Provider` | Provider identifier (must match `provider_df`) |
| `fraud_probability` | Model output probability in `[0, 1]` |

Use `utils.investigation_utils.create_probability_frame()` to build this from notebook outputs:

```python
from utils.investigation_utils import create_probability_frame

provider_probabilities = create_probability_frame(
    final_df.loc[X_test.index],
    y_proba.tolist(),
)
```

### `claims_df` (optional)

Claim-level DataFrame (typically `claims_bene` from the notebook). When supplied, the crew enriches provider features with:

- Duplicate claim ratios
- Top diagnosis/procedure code concentration
- Beneficiary concentration and provider dependency
- Claim growth and temporal spikes

If omitted, the crew attempts to load CSV files from `data/` or the project root.

### `threshold` (optional, default `0.6`)

Only providers with `fraud_probability >= threshold` enter the investigation pipeline.

---

## Workflow

```
Fraud Probability Filter (threshold)
        ↓
Provider Analysis Agent
        ↓
Claim Analysis Agent
        ↓
Beneficiary Analysis Agent
        ↓
Investigation Coordinator
        ↓
JSON Report Export
```

### Entry point

```python
from crews.fraud_investigation_crew import FraudInvestigationCrew

crew = FraudInvestigationCrew(output_dir="outputs", claims_df=claims_bene)
reports = crew.investigate(
    provider_df,
    provider_probabilities,
    threshold=0.6,
    claims_df=claims_bene,
)
```

---

## Output

Reports are written to the configured output directory:

```
outputs/
  PRV51001_report.json       # one file per investigated provider
  investigation_reports.json # combined bundle of all reports
```

### Report schema

Each `{Provider}_report.json` file follows this structure:

```json
{
  "Provider": "PRV51001",
  "fraud_probability": 0.8521,
  "investigation_summary": {
    "provider": {
      "agent": "provider",
      "risk_score": 0.35,
      "evidence": []
    },
    "claim": {
      "agent": "claim",
      "risk_score": 0.32,
      "evidence": []
    },
    "beneficiary": {
      "agent": "beneficiary",
      "risk_score": 0.2,
      "evidence": []
    },
    "coordinator": {
      "Fraud Score": 0.453,
      "Provider Risk": 0.35,
      "Claim Risk": 0.32,
      "Beneficiary Risk": 0.2,
      "Evidence": [],
      "Recommendation": ["Continue baseline monitoring of billing patterns"],
      "Priority": "Low",
      "Confidence": 0.67,
      "risk_score": 0.453,
      "risk_tier": "low",
      "agent": "coordinator",
      "fraud_probability": 0.852,
      "recommended_actions": ["Continue baseline monitoring of billing patterns"]
    }
  },
  "tasks": [
    "provider_analysis",
    "claim_analysis",
    "beneficiary_analysis",
    "coordinator"
  ]
}
```

### Coordinator fields (required)

These fields inside `investigation_summary.coordinator` are always present:

| Field | Type | Description |
|-------|------|-------------|
| `Fraud Score` | float | Combined fraud score `[0, 1]` |
| `Provider Risk` | float | Provider agent risk score |
| `Claim Risk` | float | Claim agent risk score |
| `Beneficiary Risk` | float | Beneficiary agent risk score |
| `Evidence` | list | Aggregated evidence items (empty list if none) |
| `Recommendation` | list | Recommended actions |
| `Priority` | string | `High`, `Medium`, or `Low` |
| `Confidence` | float | Confidence in the assessment `[0, 1]` |

Use `extract_coordinator_summary(report)` to obtain a flat view for downstream APIs:

```python
from utils.investigation_utils import extract_coordinator_summary

summary = extract_coordinator_summary(report)
# Returns Provider, Fraud Score, Provider Risk, Claim Risk,
# Beneficiary Risk, Evidence, Recommendation, Priority, Confidence
```

### Evidence item schema

```json
{
  "metric": "AvgClaimDuration",
  "value": 28.6341,
  "percentile": 0.95,
  "zscore": 1.322,
  "peer_mean": 16.0807,
  "peer_std": 9.4923,
  "signal": "elevated"
}
```

---

## Integration

### GenAI Explainability

Load a single provider report and pass coordinator findings plus evidence to a Gemini prompt:

```python
import json
from pathlib import Path

report = json.loads(Path("outputs/PRV51001_report.json").read_text())
coordinator = report["investigation_summary"]["coordinator"]
# Feed coordinator["Evidence"], coordinator["Fraud Score"], etc. to explainability layer
```

Reference test: `scripts/run_single_provider_test.py`

### RAG Chatbot

Index `investigation_reports.json` or individual `{Provider}_report.json` files. Key retrieval fields:

- `Provider`
- `investigation_summary.coordinator.Evidence`
- `investigation_summary.coordinator.Recommendation`
- `investigation_summary.coordinator.Priority`

### Dashboard

Read `investigation_reports.json` to populate investigation tables:

```python
from utils.investigation_utils import load_investigation_reports

reports = load_investigation_reports("outputs")
rows = [
    {
        "Provider": r["Provider"],
        "Fraud Score": r["investigation_summary"]["coordinator"]["Fraud Score"],
        "Priority": r["investigation_summary"]["coordinator"]["Priority"],
    }
    for r in reports
]
```

### Backend API

Expose an endpoint that:

1. Accepts or retrieves ML fraud probabilities
2. Calls `FraudInvestigationCrew.investigate()`
3. Returns `extract_coordinator_summary(report)` per provider

---

## Validation

```python
from utils.investigation_utils import validate_investigation_report

validate_investigation_report(report)  # raises ValueError if schema is invalid
```

---

## Test scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_investigation_test.py` | Multi-provider smoke test → `outputs_test/` |
| `scripts/run_single_provider_test.py` | Single-provider reference test → `outputs/` |

---

## Error handling

| Condition | Behavior |
|-----------|----------|
| Empty `provider_df` | Raises `ValueError` |
| Missing required columns | Raises `ValueError` with column names |
| No providers above threshold | Logs warning, writes empty `investigation_reports.json`, returns `[]` |
| Missing claim CSV files | Logs warning, continues without claim enrichment |
| Missing beneficiary data | Logs warning, continues with claim data only |
