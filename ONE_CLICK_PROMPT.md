# EHunt AI Skills 一键安装提示词

把下面的提示词复制到支持 Skills 的 AI 助手中发送，即可安装 EHunt 的 6 个电商数据 Skill。

GitHub 仓库地址：`EHuntAI/ehunt-ai-skills`。

## 页面展示用提示词

```text
请帮我安装 EHunt 的全部 6 个 Etsy 电商数据分析 Skill。

请执行：

npx skills add EHuntAI/ehunt-ai-skills --all

安装完成后，请确认以下 6 个 Skill 已经可用：

- ehunt-product-query：商品查询
- ehunt-shop-query：店铺查询
- ehunt-keyword-query：关键词查询
- ehunt-product-research：选品研究与机会发现
- ehunt-competitor-analysis：竞品与店铺分析
- ehunt-keyword-research：关键词研究与 Listing 优化

请在安装完成后逐一检查并告诉我每个 Skill 的名称和用途。然后检查当前运行环境是否已配置 `EHUNT_AI_KEY`（不要显示它的值）：如果未配置，说明 `EHUNT_AI_KEY` 是本地环境变量、`X-EHUNT-AI-KEY` 是客户端自动添加的 HTTP 请求头，并根据我的操作系统给出临时配置方法。不要让我在聊天中粘贴 API Key，也不要未经确认持久化保存它。配置完成后，请调用一个 EHunt Skill 做连通性验证。
```

## 简短按钮文案

```text
帮我安装 EHunt 的全部 Skill，执行命令 `npx skills add EHuntAI/ehunt-ai-skills --all`。安装后检查是否已配置 `EHUNT_AI_KEY`；若未配置，请安全引导我完成配置并验证调用。不要让我在聊天中粘贴 Key。
```

## 终端安装

```bash
npx skills add EHuntAI/ehunt-ai-skills --all
```

只安装一个：

```bash
npx skills add EHuntAI/ehunt-ai-skills --skill ehunt-product-query
```

安装后设置用户自己的 `EHUNT_AI_KEY`（值为 `eh_ai_` 前缀的 API Key），Skill 即可直接调用 EHunt 数据接口。站点与 ehunt-agent 使用的内部 Token 不对外发布，也不能用于第三方安装。
