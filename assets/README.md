# Demo assets

Public portfolio screenshots generated from the running application are stored here.

Current screenshot set:

1. `reportly-landing.png` — initial upload and sample-data entry page.
2. `reportly-dashboard.png` — KPIs, sales trend, product share, and daily summary.
3. `reportly-products.png` — product sales ranking.
4. `reportly-orders.png` — cleaned order details and Excel export.

Only use the synthetic files in `sample_data` when recording public demos.

Regenerate the images while the app is running locally:

```powershell
node scripts/capture_portfolio.mjs "http://localhost:8501/" "assets/reportly-landing.png" 1440 1000 9224
node scripts/capture_portfolio.mjs "http://localhost:8501/?demo=true" "assets/reportly-dashboard.png" 1440 1800 9225
node scripts/capture_portfolio.mjs "http://localhost:8501/?demo=true" "assets/reportly-products.png" 1440 1200 9226 "商品分析"
node scripts/capture_portfolio.mjs "http://localhost:8501/?demo=true" "assets/reportly-orders.png" 1440 1150 9227 "订单明细"
```
