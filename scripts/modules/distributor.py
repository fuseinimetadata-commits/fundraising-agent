"""
Module 3: Distributor -- Native Composio Edition
Posts directly via Composio Twitter + LinkedIn connections.
No Cloudflare Worker proxy needed. Zero cost.

Composio connections:
  Twitter:  ca_OAt9DkyI3qj1 (@ERC3643Assessor)
  LinkedIn: ca_33kHues39vrR (Fuseini Mohammed, urn:li:person:FU7-9X_m7y)

INTERNAL use only (called from main.py or cron tasks).
For standalone execution, use run_composio_tool helper inside COMPOSIO_REMOTE_WORKBENCH.
"""

LINKEDIN_AUTHOR_URN = "urn:li:person:FU7-9X_m7y"
WORKER_ENDPOINT = "https://clawgig-webhook.fuseini-metadata.workers.dev"
TELEGRAM_CHAT_ID = "1018539294"
GITHUB_OWNER = "fuseinimetadata-commits"
GITHUB_REPO = "fundraising-agent"

# NOTE: All Composio API calls in this module use the run_composio_tool() helper
# which is available inside COMPOSIO_REMOTE_WORKBENCH sandbox.
# Direct requests to backend.composio.dev require entity_id + app_name headers
# that are not available in the sandbox -- use run_composio_tool() instead.


def post_launch_content(campaign_id: str, content: dict) -> dict:
    """Post launch-day content to Twitter + LinkedIn. Returns results dict."""
    import time, re
    results = {}

    # Twitter launch thread
    thread = content["social_posts"]["twitter_threads"][0]["thread"]
    results["twitter"] = _post_twitter_thread(thread, campaign_id)

    # LinkedIn launch post
    li = content["social_posts"]["linkedin_posts"][0]
    results["linkedin"] = _post_linkedin(li["content"], li["hashtags"], campaign_id)

    return results


def post_update(campaign_id: str, update_index: int, content: dict) -> dict:
    """Post scheduled update (index 1 = Day 10, index 2 = Day 25)."""
    results = {}
    threads = content["social_posts"]["twitter_threads"]
    li_posts = content["social_posts"]["linkedin_posts"]
    if update_index < len(threads):
        results["twitter"] = _post_twitter_thread(threads[update_index]["thread"], campaign_id)
    if update_index < len(li_posts):
        results["linkedin"] = _post_linkedin(li_posts[update_index]["content"], li_posts[update_index]["hashtags"], campaign_id)
    return results


def _post_twitter_thread(tweets: list, campaign_id: str) -> dict:
    import time
    tweet_ids = []
    prev_id = None
    for i, text in enumerate(tweets):
        if len(text) > 270:
            text = text[:267] + "..."
        payload = {"text": text}
        if prev_id:
            payload["reply_in_reply_to_tweet_id"] = prev_id
        result, error = run_composio_tool("TWITTER_CREATION_OF_A_POST", payload)
        if error:
            prev_id = None
            continue
        tweet_id = str(
            result.get("data", {}).get("data", {}).get("id")
            or result.get("data", {}).get("id", "")
        )
        if tweet_id:
            tweet_ids.append(tweet_id)
            prev_id = tweet_id
        time.sleep(2)
    return {"success": len(tweet_ids) > 0, "tweet_ids": tweet_ids}


def _post_linkedin(content: str, hashtags: list, campaign_id: str) -> dict:
    import re
    content = content.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    content = re.sub(r'\(([^)]+)\)', r'\1', content)
    hashtag_str = " ".join(hashtags[:3])
    full_post = f"{content}\n\n{hashtag_str}".strip()[:2900]
    result, error = run_composio_tool("LINKEDIN_CREATE_LINKED_IN_POST", {
        "author": LINKEDIN_AUTHOR_URN,
        "commentary": full_post,
        "visibility": "PUBLIC",
        "lifecycleState": "PUBLISHED"
    })
    if error:
        return {"success": False, "error": str(error)}
    share_urn = (
        result.get("data", {}).get("x_restli_id")
        or result.get("data", {}).get("id")
    )
    return {"success": True, "share_urn": share_urn}
