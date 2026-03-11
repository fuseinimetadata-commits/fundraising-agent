"""
Module 4: Optimizer
Weekly cron -- pulls KPIs, LLM analysis, rewrites underperformers, reports to Telegram
Uses GitHub state files + Cloudflare Workers AI -- zero cost
"""

import json
import requests
from datetime import datetime
from config import WORKER_ENDPOINT, LLM_MODEL, TELEGRAM_CHAT_ID, GITHUB_OWNER, GITHUB_REPO


def run_weekly_optimization(campaign_id: str) -> dict:
    state = load_campaign_state(campaign_id)
    if not state:
        return {"error": f"Campaign {campaign_id} not found"}
    kpis = state.get("kpis", {})
    content = state.get("content", {})
    analysis = analyze_performance(campaign_id, kpis, content)
    rewrites = {}
    if analysis.get("rewrite_needed"):
        for item in analysis.get("rewrite_targets", []):
            rewrites[item["type"]] = rewrite_content(item, state["intelligence"])
    if rewrites:
        state = apply_rewrites(state, rewrites)
        save_campaign_state(campaign_id, state)
    report = build_report(campaign_id, kpis, analysis, rewrites)
    send_report_to_telegram(report)
    return {"campaign_id": campaign_id, "analysis": analysis, "rewrites_applied": len(rewrites)}


def analyze_performance(campaign_id: str, kpis: dict, content: dict) -> dict:
    prompt = f"""Fundraising performance analysis for campaign {campaign_id}.

KPIs: {json.dumps(kpis)}

Analyze and return ONLY valid JSON:
{{"overall_health": "strong|moderate|weak", "key_insight": "1-sentence diagnosis", "rewrite_needed": true, "rewrite_targets": [{{"type": "email_subject|twitter_hook|linkedin_opening|cta", "item_index": 0, "current_text": "...", "problem": "why underperforming", "priority": "high|medium|low"}}], "recommended_actions": ["action1", "action2"], "projected_outcome": "expected result"}}"""
    return json.loads(_call_llm(prompt))


def rewrite_content(item: dict, intelligence: dict) -> str:
    prompt = f"""Rewrite this underperforming fundraising content.
TYPE: {item['type']}
CURRENT: {item['current_text']}
PROBLEM: {item['problem']}
PROJECT: {intelligence.get('core_problem', '')}
EMOTIONAL HOOK: {intelligence.get('emotional_hook', '')}

Return ONLY the rewritten text."""
    return _call_llm(prompt).strip()


def build_report(campaign_id: str, kpis: dict, analysis: dict, rewrites: dict) -> str:
    return (
        f"Weekly Fundraising Report -- {campaign_id}\n"
        f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}\n\n"
        f"KPIs: Views={kpis.get('views',0)} Clicks={kpis.get('clicks',0)} "
        f"Donations={kpis.get('donations',0)} Raised=${kpis.get('amount_raised',0)}\n\n"
        f"Analysis: {analysis.get('key_insight','N/A')}\n"
        f"Health: {analysis.get('overall_health','N/A').upper()}\n"
        f"Rewrites applied: {len(rewrites)}\n\n"
        + "\n".join(f"- {a}" for a in analysis.get("recommended_actions", []))
    )


def send_report_to_telegram(report: str):
    try:
        requests.post(f"{WORKER_ENDPOINT}/telegram", json={"action": "telegram_notify", "chat_id": TELEGRAM_CHAT_ID, "message": report}, timeout=15)
    except Exception:
        pass


def load_campaign_state(campaign_id: str) -> dict:
    resp = requests.post(f"{WORKER_ENDPOINT}/composio/github", json={"action": "github_read_file", "owner": GITHUB_OWNER, "repo": GITHUB_REPO, "path": f"state/campaigns/{campaign_id}.json"}, timeout=30)
    if resp.ok:
        return resp.json().get("content", {})
    return {}


def save_campaign_state(campaign_id: str, state: dict):
    requests.post(f"{WORKER_ENDPOINT}/composio/github", json={"action": "github_write_file", "owner": GITHUB_OWNER, "repo": GITHUB_REPO, "path": f"state/campaigns/{campaign_id}.json", "content": json.dumps(state, indent=2), "message": f"chore: update campaign state {campaign_id}"}, timeout=30)


def apply_rewrites(state: dict, rewrites: dict) -> dict:
    if "versions" not in state:
        state["versions"] = []
    state["versions"].append({"timestamp": datetime.utcnow().isoformat(), "snapshot": json.dumps(state.get("content", {}))[:500] + "..."})
    for content_type, new_text in rewrites.items():
        if content_type == "email_subject" and state["content"].get("email_sequence"):
            state["content"]["email_sequence"][0]["subject"] = new_text
        elif content_type == "twitter_hook" and state["content"]["social_posts"]["twitter_threads"]:
            state["content"]["social_posts"]["twitter_threads"][0]["thread"][0] = new_text
        elif content_type == "linkedin_opening" and state["content"]["social_posts"]["linkedin_posts"]:
            state["content"]["social_posts"]["linkedin_posts"][0]["content"] = new_text
    return state


def _call_llm(prompt: str) -> str:
    resp = requests.post(f"{WORKER_ENDPOINT}/llm", json={"skill": "fundraising_optimizer", "model": LLM_MODEL, "messages": [{"role": "system", "content": "Return only valid JSON or plain text as instructed."}, {"role": "user", "content": prompt}]}, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", data.get("response", ""))
