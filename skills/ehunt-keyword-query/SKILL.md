---
name: ehunt-keyword-query
description: "分析 Etsy 关键词的相关指标，输出可落地的关键词布局策略。"
version: 1.2.1
agent_created: true
metadata:
  title: "关键词查询"
  source: ehunt-agent builtin skill
  api_base_url: https://ehunt.ai
  auth_header: X-EHUNT-AI-KEY
  auth_key_prefix: eh_ai_
  tools:
    - research_keywords
  endpoints:
    research_keywords: "POST /api/agent/data/keywords/research"
---

# Data access

Use the runtime's native EHunt tools when `search_products`, `search_shops`, or `research_keywords` are available. In ehunt-agent, these tools call the website endpoints with the internal `X-EHUNT-INTERNAL-KEY` and `X-EHUNT-USER-ID` credentials supplied by the site; never request, expose, or reuse those internal credentials.

When native EHunt tools are unavailable, call the same etsyhunt-api data endpoints through this Skill's bundled client `scripts/ehunt_api.py` using the user's `EHUNT_AI_KEY`. The client sends `X-EHUNT-AI-KEY` and supports the keywords resources required by this Skill. Resolve both paths relative to this Skill directory, and read `references/API.md` for endpoint and parameter details. Never invent data when the key is missing or the request fails. If `EHUNT_AI_KEY` is missing, explain that `EHUNT_AI_KEY` is the local environment variable and `X-EHUNT-AI-KEY` is the HTTP header added automatically by the client. Direct the user to create an `eh_ai_` key in the EHunt Agent API Key management page, provide the correct temporary configuration command for their operating system, ask them to confirm after setting it, then retry the original query. Do not ask the user to paste the key into chat, do not place it directly in a command argument, and never print or persist it. Only help configure a persistent user-level environment variable after the user explicitly requests and confirms that action.

Examples from this Skill directory:

```bash
python scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
python scripts/ehunt_api.py shops --json '{"country":"US","sort_by":"8","desc":"desc","page_size":10}'
python scripts/ehunt_api.py keywords --json '{"keyword":"wedding gift","long_tail":true,"page_size":10}'
```

Use only the commands needed by the current Skill. Analyze the returned `data.list`; preserve `data.item_count`, `data.credits_charged`, and any allowance fields in the interpretation.

# Instructions

帮用户分析 Etsy 关键词的相关指标。用户要的是「该打哪些词、怎么打」。
参数处理：能识别关键词、种子词或相关主题时，直接调用 research_keywords；不要因为缺少非必要参数而确认。仅当关键词对象和查询意图都完全无法判断时，才调用 ask_clarification。
工作流：
1. 理解查询意图，提取关键词或种子词。
2. 调用 research_keywords 获取用户请求数量的关键词数据；未指定数量时使用工具默认值；禁止调用关键词详情、历史数据或历史趋势能力。
3. 关键词表格最多展示 7 列（不是 7 个关键词），以适配面板宽度。列头优先使用：关键词、竞争度、浏览量、收藏量、销量、评论量、分数；用户明确提到的指标优先，剩余列补充相关指标。不要因为列数限制省略关键词名称或分数。
4. 浏览量、收藏量、销量、评论量均有总量和近一个月量两种口径；总浏览量是使用该关键词的 Top100 热销商品总浏览量，近一个月浏览量是这些 Top100 热销商品最近一个月的总浏览量，其他总量和近一个月量按同样口径理解。不存在“月搜索量”字段，不要创建或展示“月搜索量”。用户没有提到总量或近一个月量时，默认展示近一个月指标；用户明确提到哪种口径就展示哪种口径。
5. 分数必须展示，并说明计算规则：分数 = 使用此关键词的 Top100 热销商品的总浏览量 ÷ 竞争度 ÷ 100。分数越高，代表该关键词搜索量越高或竞争度越低，越推荐使用该关键词。不要把分数称为推荐值，也不要自行改写公式。
6. 最终回复必须按标准 Markdown 格式组织和渲染，不得把 Markdown 语法放入代码块。关键词名称必须使用 `[关键词](URL)` Markdown 链接。链接格式为 https://ehunt.ai/keyword-tool?keyword={关键词各单词以加号拼接}；例如 Jett necklace gift → https://ehunt.ai/keyword-tool?keyword=Jett+necklace+gift。禁止输出 `<a>` 或依赖 `target`、`style` 等 HTML 标签和属性；链接打开方式由宿主客户端决定。
7. 表格之后给出实质性分析，至少覆盖（有数据才写）：
   - 指标对比：结合当前展示的浏览量、竞争度、销量、收藏量或评论量比较关键词。
   - 机会识别：分数较高且竞争度较低的词优先关注。
   - 长尾价值：结合当前指标判断长尾词机会，不推断历史增长或趋势。
8. 给出关键词布局建议：标题主词打哪个、长尾词铺哪些、避免哪些词。
语言与列头：严格跟随用户本轮输入语言输出，表格标题、列头、指标标签、缺失值说明和分析文字必须同语种；英文提问不得出现中文列头，中文提问使用中文列头。
输出格式：先给最多 7 列的关键词表格，再给分数计算规则，再给分点分析和可执行的关键词布局建议。不要只给排名。
如果关键词查询结果同时包含商品或店铺列表，图片使用 `![名称](图片URL)` Markdown 图片语法，商品和店铺名称使用 `[名称](URL)` Markdown 链接；禁止输出 `<img>`、`<a>` 等 HTML 标签。纯关键词表只展示关键词链接，不虚构商品或店铺图片。
