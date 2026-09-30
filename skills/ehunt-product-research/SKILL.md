---
name: ehunt-product-research
description: "结合商品与关键词数据，做选品机会发现与方向建议。"
version: 1.2.1
agent_created: true
metadata:
  title: "选品研究"
  source: ehunt-agent builtin skill
  api_base_url: https://www.ehunt.ai
  auth_header: X-EHUNT-AI-KEY
  auth_key_prefix: eh_ai_
  tools:
    - search_products
    - research_keywords
  endpoints:
    search_products: "POST /api/agent/data/products/list"
    research_keywords: "POST /api/agent/data/keywords/research"
---

# Data access

Use the runtime's native EHunt tools when `search_products`, `search_shops`, or `research_keywords` are available. In ehunt-agent, these tools call the website endpoints with the internal `X-EHUNT-INTERNAL-KEY` and `X-EHUNT-USER-ID` credentials supplied by the site; never request, expose, or reuse those internal credentials.

When native EHunt tools are unavailable, call the same etsyhunt-api data endpoints through this Skill's bundled client `scripts/ehunt_api.py` using the user's `EHUNT_AI_KEY`. The client sends `X-EHUNT-AI-KEY` and supports the products and keywords resources required by this Skill. Resolve both paths relative to this Skill directory, and read `references/API.md` for endpoint and parameter details. Never invent data when the key is missing or the request fails. If `EHUNT_AI_KEY` is missing, explain that `EHUNT_AI_KEY` is the local environment variable and `X-EHUNT-AI-KEY` is the HTTP header added automatically by the client. Direct the user to create an `eh_ai_` key in the EHunt Agent API Key management page, provide the correct temporary configuration command for their operating system, ask them to confirm after setting it, then retry the original query. Do not ask the user to paste the key into chat, do not place it directly in a command argument, and never print or persist it. Only help configure a persistent user-level environment variable after the user explicitly requests and confirms that action.

Examples from this Skill directory:

```bash
python scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
python scripts/ehunt_api.py shops --json '{"country":"US","sort_by":"8","desc":"desc","page_size":10}'
python scripts/ehunt_api.py keywords --json '{"keyword":"wedding gift","long_tail":true,"page_size":10}'
```

Use only the commands needed by the current Skill. Analyze the returned `data.list`; preserve `data.item_count`, `data.credits_charged`, and any allowance fields in the interpretation.

# Instructions

结合 Etsy 商品数据和关键词数据，做选品机会发现和方向建议。用户要的是「做什么品、为什么、怎么切入」。
工作流：
1. 理解用户选品方向（品类、价格带、目标市场等）。区间统一使用 min~max；“近N天/近一年”分别映射为 listed_time=N/365。
2. 调用 search_products 和 research_keywords 获取用户请求数量的数据；未指定数量时使用各工具默认值。优先分别查询需求和供给，若某条件没有对应字段，使用相邻可解释字段补偿并明确说明。
3. 交叉分析，判据如下（有数据才下结论）：
   - 机会关键词 = 浏览量高 + 竞争度低，且对应商品头部评论数不高（说明壁垒低）。
   - 需求真实性 = 关键词有浏览量，且对应商品确有销量，两者必须互相印证。
   - 切入可行性 = 头部商品里存在上架时间短但销量已起的新品（说明新品能突围）。
   - 利润空间 = 主流价格带扣除成本后是否留有余量，避开纯低价红海。
4. 输出选品方向建议：机会关键词 + 对应商品表现 + 推荐切入角度 + 建议定价区间。
语言与列头：严格跟随用户本轮输入语言输出，表格标题、列头、指标标签、缺失值说明和分析文字必须同语种；英文提问不得出现中文列头，中文提问使用中文列头。
输出格式：先给机会关键词表格（关键词/浏览量/竞争度/推荐值；未指定总/月时默认使用近一个月浏览量），再给对应商品表现表格，最后给 3-5 条选品方向建议（每条含判断依据和可执行动作）。
要给出明确的方向取舍，不要罗列所有可能性。
商品表现列表的第一列固定为商品图片，第二列为商品名称；店铺名称、价格、上架时间等每项信息分别独立成列，禁止把图片、商品名称、店铺名称或其他不同信息合并到同一列。只有同一指标的总量和周量可以合并为一列，例如销量、收藏、评论分别写成“总值 / 周值”。商品标题和店铺名称必须使用 HTML 超链接并设置 target="_blank" rel="noopener noreferrer"，分别链接到 https://ehunt.ai/product-detail/{商品ID} 和 https://ehunt.ai/store-detail/{店铺名称}，必须另开页面。优先使用工具返回的图片、ID和名称，缺少字段时如实说明，不得编造图片或链接。市场分析使用分节标题、短段落和项目符号，表格只保留核心指标，风险和建议分开列出。
