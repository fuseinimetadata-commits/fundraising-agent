# Fundraising Agent

**Autonomous AI-driven fundraising campaign agent.**  
Zero-cost stack: Cloudflare Workers AI + Composio (Twitter, LinkedIn, GitHub, Apify)

---

## What It Does

1. **Analyzes** any project brief → audience profiles, narrative angles, funding goal
2. **Generates** complete campaign package: page copy, 7-email sequence, Twitter threads, LinkedIn posts, thank-yous, progress updates, impact report
3. **Distributes** content automatically via Composio to Twitter/X and LinkedIn
4. **Optimizes** weekly via LLM analysis: rewrites underperforming content, reports via Telegram

## Stack (100% Free)
| Layer | Tool |
|-------|------|
| LLM | Cloudflare Workers AI (llama-3.3-70b) |
| Trend scraping | Apify |
| Social posting | Twitter/X + LinkedIn via Composio |
| State storage | GitHub (this repo) |
| Scheduling | SureThing cron |
| Notifications | Telegram |

## Usage

```bash
# Step 1: Fill in your brief
cp templates/campaign_brief.md my_project_brief.md

# Step 2: Generate full campaign package
python scripts/main.py --action generate --brief my_project_brief.md --niche web3

# Step 3: Launch (posts to Twitter + LinkedIn)
python scripts/main.py --action launch --campaign <campaign_id>

# Step 4: Weekly optimization runs automatically via cron
python scripts/main.py --action optimize --campaign <campaign_id>

# Check campaign report
python scripts/main.py --action report --campaign <campaign_id>
```

## Supported Niches
- `web3` — Blockchain, DeFi, RWA, DAOs, Gitcoin grants
- `nonprofit` — NGOs, community projects, social impact
- `personal` — Individual campaigns, medical, education
- `creative` — Art, music, film, writing projects
- `tech` — Open source, developer tools, SaaS MVPs

## Output (Per Campaign)
- Campaign headline + full story copy
- 3 donation tiers with impact statements
- 7-email drip sequence (launch to final push)
- 3 Twitter threads (launch, Day 10, Day 25)
- 3 LinkedIn posts (launch, mid, final)
- 5 short-form captions
- Thank-you messages per tier
- Progress update templates (25%, 50%, 75%, 100%)
- Impact report template
- Comment response templates (4 scenarios)

## Monetization
- Agency: $500-$2k per campaign
- SaaS: $49-$199/mo subscription
- Web3 niche: $1k-$5k per Gitcoin/blockchain campaign