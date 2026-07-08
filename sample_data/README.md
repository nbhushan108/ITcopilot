# ITcopilot Sample Data

This directory contains sample files for development and testing.

## Files

| File | Description |
|------|-------------|
| `zerodha_tradebook_sample.csv` | Sample Zerodha tradebook export for broker import testing |
| `tax_computation_samples.csv` | Sample tax computation inputs for batch testing |

## Usage

```bash
# Test broker import
python -c "
from pathlib import Path
from broker_imports import get_broker_registry
registry = get_broker_registry()
result = registry.import_statement('zerodha', Path('sample_data/zerodha_tradebook_sample.csv'))
print(f'Imported {len(result.trades)} trades')
"

# Test tax computation via API
curl -X POST http://localhost:8000/api/v1/tax/compute \
  -H "Content-Type: application/json" \
  -d '{
    "pan": "ABCDE1234F",
    "assessment_year": "2025-26",
    "regime": "old",
    "gross_salary": "1500000",
    "other_income": "75000",
    "section_80c": "150000",
    "section_80d": "25000",
    "hra_exemption": "120000"
  }'
```
