"""
Fundraising Agent -- Config
Zero-cost stack: Cloudflare Workers AI + Composio (Twitter, LinkedIn, GitHub, Apify)
"""

import os

# Cloudflare Workers AI (existing worker endpoint)
WORKER_ENDPOINT = os.environ.get("WORKER_ENDPOINT", "https://clawgig-webhook.fuseini-metadata.workers.dev")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "")

# Telegram notifications
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_BOT = os.environ.get("TELEGRAM_BOT", "")

# GitHub state storage (via Composio)
GITHUB_OWNER = "fuseinimetadata-commits"
GITHUB_REPO = "fundraising-agent"
GITHUB_BRANCH = "main"
STATE_PATH = "state/campaigns"

# Social platforms (via Composio -- already connected)
TWITTER_HANDLE = "@ERC3643Assessor"
LINKEDIN_PROFILE = "Fuseini Mohammed"

# LLM model (via Workers AI)
LLM_MODEL = "llama-3.3-70b"

# Campaign defaults
DEFAULT_EMAIL_SEQUENCE_LENGTH = 7
DEFAULT_SOCIAL_POSTS_TWITTER = 3
DEFAULT_SOCIAL_POSTS_LINKEDIN = 3
DEFAULT_SOCIAL_POSTS_CAPTIONS = 5

# Donation tier defaults
TIER_NAMES = ["Supporter", "Champion", "Patron"]
TIER_AMOUNTS_GENERIC = [25, 100, 500]
TIER_AMOUNTS_WEB3 = [50, 250, 1000]  # Web3 donors skew higher
