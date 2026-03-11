"""
Module 1: Campaign Intelligence
Analyzes project brief -> audience profiles, narrative, funding goal, platform recommendation
Uses Cloudflare Workers AI (llama-3.3-70b) -- zero cost
"""

import json
import requests
from config import WORKER_ENDPOINT, LLM_MODEL


def analyze_project(brief: str, niche: str = "auto") -> dict:
    """
    Input:  1-paragraph project brief
    Output: Full intelligence package (audience, narrative, tiers, platform)
    """
    prompt = f"""You are a world-class fundraising strategist. Analyze this project and return a JSON object.

PROJECT BRIEF:
{brief}

Return ONLY valid JSON with this exact structure:
{{
  "project_name": "short name for the project",
  "niche": "web3|nonprofit|personal|creative|tech",
  "core_problem": "the problem this project solves in 1 sentence",
  "emotional_hook": "the most compelling emotional angle for donors (1-2 sentences)",
  "unique_value": "what makes this project different from others",
  "target_audiences": [
    {{"segment": "segment name", "description": "who they are", "motivation": "why they would donate", "platform_behavior": "where they spend time online", "message_tone": "how to talk to them"}},
    {{"segment": "...", "description": "...", "motivation": "...", "platform_behavior": "...", "message_tone": "..."}},
    {{"segment": "...", "description": "...", "motivation": "...", "platform_behavior": "...", "message_tone": "..."}}
  ],
  "funding_goal": {{"recommended_amount": 0, "rationale": "why this amount", "timeline_days": 30}},
  "donation_tiers": [
    {{"name": "Supporter", "amount": 25, "impact": "specific tangible impact"}},
    {{"name": "Champion", "amount": 100, "impact": "specific tangible impact"}},
    {{"name": "Patron", "amount": 500, "impact": "specific tangible impact"}}
  ],
  "platform_recommendation": {{"primary": "gitcoin|gofundme|kickstarter|self-hosted", "rationale": "why", "secondary": "backup"}},
  "campaign_angles": ["angle 1: urgency-based", "angle 2: community-based", "angle 3: impact-based"]
}}"""

    response = _call_llm(prompt)
    return json.loads(response)


def _call_llm(prompt: str) -> str:
    """Route LLM call through existing Cloudflare Worker"""
    payload = {
        "skill": "fundraising_intelligence",
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a fundraising strategist. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
    }
    resp = requests.post(f"{WORKER_ENDPOINT}/llm", json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", data.get("response", ""))


if __name__ == "__main__":
    test_brief = """
    We are building a decentralized protocol for tokenizing real-world assets (RWA)
    on Ethereum using the ERC-3643 standard. Our platform allows SMEs in emerging
    markets to access global capital by issuing compliant security tokens. We need
    $50,000 to complete our smart contract audit, launch our testnet, and onboard
    our first 10 issuers. This directly solves the $5 trillion funding gap for
    SMEs in Africa and Southeast Asia.
    """
    result = analyze_project(test_brief, niche="web3")
    print(json.dumps(result, indent=2))
