"""
Module 2: Content Factory
Generates ALL campaign content from intelligence package
Output: campaign copy, 7-email sequence, social posts, thank-yous, updates, impact report
Uses Cloudflare Workers AI -- zero cost
"""

import json
import requests
from config import WORKER_ENDPOINT, LLM_MODEL


def generate_all_content(intelligence: dict) -> dict:
    campaign_copy = generate_campaign_copy(intelligence)
    email_sequence = generate_email_sequence(intelligence)
    social_posts = generate_social_posts(intelligence)
    engagement_templates = generate_engagement_templates(intelligence)
    return {
        "campaign_copy": campaign_copy,
        "email_sequence": email_sequence,
        "social_posts": social_posts,
        "engagement_templates": engagement_templates
    }


def generate_campaign_copy(intel: dict) -> dict:
    prompt = f"""You are a world-class copywriter specializing in fundraising campaigns.

PROJECT INTELLIGENCE:
{json.dumps(intel, indent=2)}

Generate campaign page copy. Return ONLY valid JSON:
{{
  "headline": "powerful campaign headline (max 12 words)",
  "subheadline": "expanding headline, creates urgency (max 20 words)",
  "story": {{
    "opening": "hook paragraph (2-3 sentences)",
    "problem": "problem paragraph",
    "solution": "what this project does",
    "impact": "specific tangible impact if funded",
    "social_proof": "credibility signals",
    "call_to_action": "compelling CTA sentence"
  }},
  "donation_tier_copy": [
    {{"tier": "Supporter", "amount": 25, "label": "catchy label", "description": "what donor gets + impact"}},
    {{"tier": "Champion", "amount": 100, "label": "catchy label", "description": "what donor gets + impact"}},
    {{"tier": "Patron", "amount": 500, "label": "catchy label", "description": "what donor gets + impact"}}
  ],
  "meta_description": "SEO description (155 chars max)",
  "elevator_pitch": "30-second verbal pitch (3 sentences)"
}}"""
    return json.loads(_call_llm(prompt))


def generate_email_sequence(intel: dict) -> list:
    prompt = f"""You are an email marketing expert specializing in fundraising campaigns.

PROJECT INTELLIGENCE:
{json.dumps(intel, indent=2)}

Generate a 7-email fundraising sequence. Return ONLY valid JSON array.
Email sequence arc: Launch (Day 0) -> Social proof (Day 3) -> Impact story (Day 7) -> Mid-push (Day 12) -> Donor spotlight (Day 18) -> Urgency (Day 25) -> Last chance (Day 29).
Each email: email_number, send_timing, subject, preview_text, purpose, body (300-400 words), cta_text, cta_url_placeholder."""
    return json.loads(_call_llm(prompt))


def generate_social_posts(intel: dict) -> dict:
    prompt = f"""You are a social media strategist for fundraising campaigns.

PROJECT INTELLIGENCE:
{json.dumps(intel, indent=2)}

Generate social content. Return ONLY valid JSON:
{{
  "twitter_threads": [
    {{"post_number": 1, "timing": "Launch day", "thread": ["tweet1", "tweet2", "tweet3", "tweet4", "tweet5"]}},
    {{"post_number": 2, "timing": "Day 10 milestone", "thread": ["tweet1", "tweet2", "tweet3"]}},
    {{"post_number": 3, "timing": "Day 25 final push", "thread": ["tweet1", "tweet2", "tweet3", "tweet4"]}}
  ],
  "linkedin_posts": [
    {{"post_number": 1, "timing": "Launch day", "content": "200-300 word professional post", "hashtags": ["#tag1", "#tag2", "#tag3"]}},
    {{"post_number": 2, "timing": "Day 14 midpoint", "content": "...", "hashtags": [...]}},
    {{"post_number": 3, "timing": "Day 28 final push", "content": "...", "hashtags": [...]}}
  ],
  "short_captions": [
    {{"platform": "Instagram/TikTok", "timing": "Week 1", "caption": "punchy caption + 5 hashtags"}},
    {{"platform": "Instagram/TikTok", "timing": "Week 2", "caption": "..."}},
    {{"platform": "Instagram/TikTok", "timing": "Week 3", "caption": "..."}},
    {{"platform": "Instagram/TikTok", "timing": "Week 4", "caption": "..."}},
    {{"platform": "Instagram/TikTok", "timing": "Final push", "caption": "..."}}
  ]
}}"""
    return json.loads(_call_llm(prompt))


def generate_engagement_templates(intel: dict) -> dict:
    prompt = f"""You are a donor relations specialist.

PROJECT INTELLIGENCE:
{json.dumps(intel, indent=2)}

Generate donor engagement templates. Return ONLY valid JSON:
{{
  "thank_you_messages": [
    {{"tier": "Supporter ($25)", "message": "warm 3-4 sentence thank-you"}},
    {{"tier": "Champion ($100)", "message": "community-focused 4-5 sentence thank-you"}},
    {{"tier": "Patron ($500)", "message": "VIP 5-6 sentence thank-you"}}
  ],
  "progress_updates": [
    {{"milestone": "25% funded", "message": "100-150 word update"}},
    {{"milestone": "50% funded", "message": "100-150 word update"}},
    {{"milestone": "75% funded", "message": "100-150 word update"}},
    {{"milestone": "100% funded", "message": "150-200 word success announcement"}}
  ],
  "impact_report_template": {{
    "title": "Impact Report title",
    "sections": [
      {{"section": "What We Accomplished", "prompt": "Fill in milestones"}},
      {{"section": "How Your Money Was Used", "prompt": "Fill in budget breakdown"}},
      {{"section": "Lives/Projects Impacted", "prompt": "Fill in specific metrics"}},
      {{"section": "What Comes Next", "prompt": "Fill in roadmap"}},
      {{"section": "Thank You", "prompt": "Personal note to donors"}}
    ]
  }},
  "comment_response_templates": [
    {{"scenario": "General encouragement", "response": "1-2 sentence reply"}},
    {{"scenario": "Question about fund usage", "response": "transparent answer"}},
    {{"scenario": "Skepticism", "response": "confidence-building reply"}},
    {{"scenario": "Someone shares campaign", "response": "grateful amplification"}}
  ]
}}"""
    return json.loads(_call_llm(prompt))


def _call_llm(prompt: str) -> str:
    payload = {
        "skill": "fundraising_content",
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a fundraising content expert. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
    }
    resp = requests.post(f"{WORKER_ENDPOINT}/llm", json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", data.get("response", ""))
