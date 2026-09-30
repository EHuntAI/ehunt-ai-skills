# EHunt Data API

## Authentication paths

The same Etsy data endpoints support two callers. Do not mix their credentials.

### ehunt-agent internal call

The website sends the active user ID and internal service credential to ehunt-agent in request metadata. The engine calls the website data endpoint with:

```http
X-EHUNT-INTERNAL-KEY: <service credential>
X-EHUNT-USER-ID: <site user ID>
```

This credential is private infrastructure configuration. Never place it in this repository, a Skill, a prompt, or a third-party client.

### External Skill or AI tool

A third-party AI tool calls the same website endpoint directly with the user's EHunt AI API Key:

```http
X-EHUNT-AI-KEY: eh_ai_xxxxx
```

Read the key from `EHUNT_AI_KEY`. Never print, persist, commit, or ask the user to paste it into a public prompt.

Both paths resolve an EHunt user and then use the same data service, daily allowance, credit balance, and billing ledger.

## Production endpoints

Base URL: `https://www.ehunt.ai`

| Resource | Method | Endpoint |
|---|---|---|
| Products | POST | `/api/agent/data/products/list` |
| Shops | POST | `/api/agent/data/shops/list` |
| Keywords | POST | `/api/agent/data/keywords/research` |

Product detail and keyword detail endpoints are currently unavailable. Do not call them.

## Shared client

Use the repository client without third-party Python packages:

```bash
python scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
python scripts/ehunt_api.py shops --json '{"country":"US","sort_by":"8","desc":"desc","page_size":10}'
python scripts/ehunt_api.py keywords --json '{"keyword":"wedding gift","long_tail":true,"page_size":10}'
```

Before calling, provide the key through the environment:

```bash
export EHUNT_AI_KEY="eh_ai_xxxxx"
```

Windows PowerShell:

```powershell
$env:EHUNT_AI_KEY = "eh_ai_xxxxx"
python scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
```

A caller may provide request JSON on stdin or with `--json-file`. `EHUNT_API_BASE_URL` can override the production base URL for an authorized test environment.

## Response

Successful requests use this shape:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [],
    "item_count": 0,
    "credits_charged": 0
  }
}
```

The product response also includes `used_today` and `remaining_today` under `data`. Always inspect the top-level `code`; do not assume an HTTP 200 response means the business request succeeded.

## Common request fields

### Products

`search_key`, `shop_id`, `store_id`, `category`, `price`, `sales_weekly`, `sales`, `favorites`, `favorites_weekly`, `reviews`, `reviews_weekly`, `product_type`, `ships_from`, `country`, `listed_time`, `is_bestsell`, `is_pick`, `is_raving`, `sort_by`, `desc`, `page_num`, `page_size`.

Use `min~max` for ranges. Keep `page_size` at or below 50.

### Shops

`search_key`, `search_key_filter_type`, `category`, `country`, `sales`, `sales_weekly`, `products`, `rating`, `favorites`, `favorites_weekly`, `reviews`, `reviews_weekly`, `is_star`, `is_review`, `is_raving`, `listed_time`, `revenue_total`, `revenue_7days`, `sort_by`, `desc`, `page_num`, `page_size`.

Use `desc` or `asc` as the shop `desc` value. Keep `page_size` at or below 50.

### Keywords

`keyword`, `kw`, `long_tail`, `exclude`, `views`, `views_monthly`, `favorites`, `favorites_monthly`, `sales`, `sales_monthly`, `reviews`, `reviews_monthly`, `competition`, `page_num`, `page_size`.

Use comma-separated words for `exclude`. Keep `page_size` at or below 50 for consistent cross-client behavior.
