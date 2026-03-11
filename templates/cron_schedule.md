# Fundraising Agent -- Cron Schedule

All crons use SureThing infrastructure. Per-campaign crons created on launch.

## Cron 1: Day 10 Update (per campaign, delay trigger)
Run: python scripts/main.py --action update --campaign CAMPAIGN_ID --index 1

## Cron 2: Day 25 Final Push (per campaign, delay trigger)
Run: python scripts/main.py --action update --campaign CAMPAIGN_ID --index 2

## Cron 3: Weekly Optimization (global, every Monday 9am UTC)
Expression: 0 9 * * 1
For each active campaign: python scripts/main.py --action optimize --campaign CAMPAIGN_ID

## Cron 4: Weekly KPI Sync (global, every Monday 8am UTC)
Expression: 0 8 * * 1
Fetch Twitter + LinkedIn metrics via Composio, update state/campaigns/CAMPAIGN_ID.json on GitHub.

## Notes
- Crons 3 and 4 are global
- Crons 1 and 2 are per-campaign delay tasks
- All crons notify Telegram chat_id 1018539294 on completion
