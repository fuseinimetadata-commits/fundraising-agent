"""
Demo launch script -- End-to-end proof of concept.
Run inside COMPOSIO_REMOTE_WORKBENCH (uses run_composio_tool + invoke_llm helpers).

Demonstrates: LLM content generation -> Twitter thread -> LinkedIn post -> GitHub state
Campaign: RWA SME Tokenization Protocol (Gitcoin Grants, $50k goal)

Verified live run 2026-03-11:
  Twitter: 5/5 tweets | https://twitter.com/ERC3643Assessor/status/2031741649944998288
  LinkedIn: urn:li:share:7437507395620184064
  GitHub: state/campaigns/demo_rwa_850162.json
"""

import json, time, re, uuid

LINKEDIN_AUTHOR_URN = "urn:li:person:FU7-9X_m7y"

brief = """
We are building a decentralized protocol for tokenizing real-world assets (RWA)
on Ethereum using the ERC-3643 compliant security token standard. Our platform
allows SMEs in emerging markets across Africa and Southeast Asia to access global
capital by issuing regulated, transferable security tokens. We need $50,000 to
complete our smart contract audit, deploy our testnet, and onboard our first 10
issuers. This addresses the $5 trillion SME funding gap in developing economies.
Fundraising on Gitcoin Grants. Builder: Fuseini Mohammed (@ERC3643Assessor).
"""

# Generate tweets
twitter_result, _ = invoke_llm(f"Create 5-tweet Web3 fundraising thread. Max 230 chars each. JSON array only. Project: {brief.strip()[:400]}")
try:
    match = re.search(r'\[[\s\S]*?\]', twitter_result)
    tweets = json.loads(match.group()) if match else None
except:
    tweets = None

if not tweets or len(tweets) < 5:
    tweets = [
        "SMEs in Africa & SE Asia hold real assets but can't reach global capital. We're building the rails -- on Ethereum. Here's what we're doing and why it matters.",
        "The $5 trillion SME funding gap: 70% of jobs in developing economies come from small businesses locked out of global capital markets. Not due to lack of value -- due to lack of rails.",
        "Our ERC-3643 compliant protocol on Ethereum lets emerging market SMEs issue regulated, transferable security tokens. Global investors can now back them compliantly.",
        "$50,000 = smart contract audit + testnet + 10 SME issuers onboarded. That unlocks hundreds of jobs and direct access to global capital for real businesses.",
        "Live on @gitcoin Grants. If borderless capital for emerging markets matters to you, back us today. #RWA #ERC3643 #DeFi #GitcoinGrants"
    ]

# Generate LinkedIn post
li_result, _ = invoke_llm(f"Write 200-250 word LinkedIn post announcing this campaign. Speak as Fuseini Mohammed. Straight apostrophes only. End with #RWA #ERC3643 #Web3. Return post text only. Project: {brief.strip()[:400]}")
linkedin_post = li_result.strip() if li_result and len(li_result) > 100 else "We are building rails for SMEs in emerging markets to access global capital via ERC-3643 security tokens on Ethereum. $50k Gitcoin Grants campaign now live. #RWA #ERC3643 #Web3"
linkedin_post = linkedin_post.replace('\u2018',"'").replace('\u2019',"'").replace('\u201c','"').replace('\u201d','"')
linkedin_post = re.sub(r'\(([^)]+)\)', r'\1', linkedin_post)

# Post Twitter thread
tweet_ids, prev_id = [], None
for i, text in enumerate(tweets):
    if len(text) > 270: text = text[:267] + "..."
    payload = {"text": text}
    if prev_id: payload["reply_in_reply_to_tweet_id"] = prev_id
    r, err = run_composio_tool("TWITTER_CREATION_OF_A_POST", payload)
    if not err:
        tid = str(r.get("data",{}).get("data",{}).get("id","") or r.get("data",{}).get("id",""))
        if tid: tweet_ids.append(tid); prev_id = tid
    time.sleep(2)

# Post LinkedIn
li_r, li_err = run_composio_tool("LINKEDIN_CREATE_LINKED_IN_POST", {"author": LINKEDIN_AUTHOR_URN, "commentary": linkedin_post[:2900], "visibility": "PUBLIC", "lifecycleState": "PUBLISHED"})
share_urn = None if li_err else (li_r.get("data",{}).get("x_restli_id") or li_r.get("data",{}).get("id"))

# Save state
campaign_id = f"rwa_{uuid.uuid4().hex[:6]}"
state = {"campaign_id": campaign_id, "status": "live", "goal_amount": 50000, "platform": "gitcoin", "kpis": {"views":0,"clicks":0,"donations":0,"amount_raised":0}, "distribution_log": [{"action":"launch","twitter":{"tweet_ids":tweet_ids},"linkedin":{"share_urn":share_urn}}], "content": {"twitter_threads": tweets, "linkedin_post": linkedin_post}}
run_composio_tool("GITHUB_CREATE_OR_UPDATE_FILE_CONTENTS", {"owner":"fuseinimetadata-commits","repo":"fundraising-agent","path":f"state/campaigns/{campaign_id}.json","content":json.dumps(state,indent=2),"message":f"feat: launch {campaign_id}","branch":"main"})

print(f"Twitter: {len(tweet_ids)}/5 | {'https://twitter.com/ERC3643Assessor/status/'+tweet_ids[0] if tweet_ids else 'none'}")
print(f"LinkedIn: {share_urn}")
print(f"Campaign: {campaign_id}")
