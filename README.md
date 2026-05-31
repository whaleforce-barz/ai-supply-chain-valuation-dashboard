# AI Supply Chain Valuation Dashboard

Static dashboard for US and Taiwan AI data center supply-chain valuation screens.
The two markets are shown on separate pages, but the browser UI and normalized
data schema are shared.

## Contents

- `index.html`: landing page
- `us.html`: US AI supply-chain valuation page
- `tw.html`: Taiwan AI supply-chain valuation page
- `method.html`: valuation and validation method audit
- `app.js`: client-side filtering, sorting, validation panels, mean-reversion panels, and detail modal
- `styles.css`: dashboard styling
- `data/*.csv`: normalized valuation, historical validation, and six-month mean-reversion data
- `data/method_audit.json`: shared method and data-status audit
- `scripts/build_ai_supply_chain_unified_dataset.py`: rebuilds dashboard data from local research outputs

## Deployment

GitHub Actions deploys the repository root to GitHub Pages on every push to `main`.

The public Pages URL is shown in each successful workflow run.
