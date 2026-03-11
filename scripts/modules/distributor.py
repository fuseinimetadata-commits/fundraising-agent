"""
Module 3: Distributor
Auto-posts campaign content to Twitter/X and LinkedIn via Composio
Zero cost -- uses existing connections
"""

import json
import requests
from datetime import datetime
from config import WORKER_ENDPOINT, TWITTER_HANDLE, TELEGRAM_CHAT_ID


def post_launch_content(campaign_id: str, content: dict, state_path: str) -> dict:
    results = {}
    twitter_thread = content["social_posts"]["twitter_threads"][0]["thread"]
    results["twitter"] = post_twitter_thread(twitter_thread, campaign_id)
    linkedin_post = content["social_posts"]["linkedin_posts"][0]
    results["linkedin"] = post_linkedin(linkedin_post["content"], linkedin_post["hashtags"], campaign_id)
    notify_telegram(
        f"Campaign LAUNCHED: {campaign_id}\n"
        f"Twitter: {'OK' if results['twitter']['success'] else 'FAIL'}\n"
        f"LinkedIn: {'OK' if results['linkedin']['success'] else 'FAIL'}"
    )
    return results


def post_update(campaign_id: str, update_index: int, content: dict) -> dict:
    results = {}
    threads = content["social_posts"]["twitter_threads"]
    linkedin_posts = content["social_posts"]["linkedin_posts"]
    if update_index < len(threads):
        results["twitter"] = post_twitter_thread(threads[update_index]["thread"], campaign_id)
    if update_index < len(linkedin_posts):
        results["linkedin"] = post_linkedin(linkedin_posts[update_index]["content"], linkedin_posts[update_index]["hashtags"], campaign_id)
    notify_telegram(f"Campaign update #{update_index + 1} posted: {campaign_id}")
    return results


def post_twitter_thread(tweets: list, campaign_id: str) -> dict:
    payload = {"action": "twitter_post_thread", "campaign_id": campaign_id, "tweets": tweets}
    resp = requests.post(f"{WORKER_ENDPOINT}/composio/twitter", json=payload, timeout=60)
    return {"success": resp.status_code == 200, "response": resp.json() if resp.ok else resp.text}


def post_linkedin(content: str, hashtags: list, campaign_id: str) -> dict:
    content = content.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    full_post = content + "\n\n" + " ".join(hashtags)
    payload = {"action": "linkedin_post", "campaign_id": campaign_id, "content": full_post, "generate_image": True}
    resp = requests.post(f"{WORKER_ENDPOINT}/composio/linkedin", json=payload, timeout=60)
    return {"success": resp.status_code == 200, "response": resp.json() if resp.ok else resp.text}


def notify_telegram(message: str):
    payload = {"action": "telegram_notify", "chat_id": TELEGRAM_CHAT_ID, "message": message}
    try:
        requests.post(f"{WORKER_ENDPOINT}/telegram", json=payload, timeout=15)
    except Exception:
        pass
