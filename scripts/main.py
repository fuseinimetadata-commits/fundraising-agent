"""
Fundraising Agent -- Main Entry Point
CLI: python main.py --action <action> --campaign <id> [--brief <file>]

Actions:
  generate    Run full pipeline on a new project brief
  launch      Post launch content to all platforms
  update      Post scheduled update (--index 1|2)
  optimize    Run weekly optimization loop
  report      Print current campaign state
"""

import argparse
import json
import uuid
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from modules.intelligence import analyze_project
from modules.content_factory import generate_all_content
from modules.distributor import post_launch_content, post_update, notify_telegram
from modules.optimizer import run_weekly_optimization, save_campaign_state, load_campaign_state


def cmd_generate(args):
    print("Reading project brief...")
    if args.brief:
        with open(args.brief, "r") as f:
            brief = f.read()
    else:
        print("Enter project brief (end with Ctrl+D):")
        brief = sys.stdin.read()

    campaign_id = args.campaign or f"campaign_{uuid.uuid4().hex[:8]}"
    niche = args.niche or "auto"

    print(f"Analyzing project... (campaign_id: {campaign_id})")
    intelligence = analyze_project(brief, niche)
    print(f"Intelligence done: {intelligence['project_name']} | {intelligence['niche']} | Goal: ${intelligence['funding_goal']['recommended_amount']}")

    print("Generating all campaign content...")
    content = generate_all_content(intelligence)
    print(f"Content generated: {len(content['email_sequence'])} emails, {len(content['social_posts']['twitter_threads'])} Twitter threads, {len(content['social_posts']['linkedin_posts'])} LinkedIn posts")

    state = {
        "campaign_id": campaign_id,
        "project_name": intelligence["project_name"],
        "niche": intelligence["niche"],
        "created_at": datetime.utcnow().isoformat(),
        "status": "draft",
        "goal_amount": intelligence["funding_goal"]["recommended_amount"],
        "platform": intelligence["platform_recommendation"]["primary"],
        "intelligence": intelligence,
        "content": content,
        "kpis": {"views": 0, "clicks": 0, "donations": 0, "amount_raised": 0, "email_open_rate": 0},
        "versions": [],
        "distribution_log": []
    }

    save_campaign_state(campaign_id, state)
    print(f"\nCampaign package complete!")
    print(f"  Campaign ID: {campaign_id}")
    print(f"  Project:     {intelligence['project_name']}")
    print(f"  Platform:    {intelligence['platform_recommendation']['primary']}")
    print(f"  Goal:        ${intelligence['funding_goal']['recommended_amount']}")
    print(f"  Timeline:    {intelligence['funding_goal']['timeline_days']} days")
    print(f"\n  Next: python main.py --action launch --campaign {campaign_id}")

    notify_telegram(f"New campaign generated: {intelligence['project_name']}\nID: {campaign_id}\nGoal: ${intelligence['funding_goal']['recommended_amount']}")
    return campaign_id


def cmd_launch(args):
    campaign_id = args.campaign
    state = load_campaign_state(campaign_id)
    if not state:
        print(f"Campaign {campaign_id} not found")
        return
    print(f"Launching: {state['project_name']}")
    results = post_launch_content(campaign_id, state["content"], "state/campaigns")
    state["status"] = "live"
    state["launched_at"] = datetime.utcnow().isoformat()
    state["distribution_log"].append({"action": "launch", "timestamp": datetime.utcnow().isoformat(), "results": results})
    save_campaign_state(campaign_id, state)
    print(f"Launch complete: Twitter {'OK' if results['twitter']['success'] else 'FAIL'} | LinkedIn {'OK' if results['linkedin']['success'] else 'FAIL'}")


def cmd_update(args):
    campaign_id = args.campaign
    update_index = int(args.index or 1)
    state = load_campaign_state(campaign_id)
    if not state:
        print(f"Campaign {campaign_id} not found")
        return
    print(f"Posting update #{update_index} for: {state['project_name']}")
    results = post_update(campaign_id, update_index, state["content"])
    state["distribution_log"].append({"action": f"update_{update_index}", "timestamp": datetime.utcnow().isoformat(), "results": results})
    save_campaign_state(campaign_id, state)
    print("Update posted")


def cmd_optimize(args):
    campaign_id = args.campaign
    print(f"Running optimization for: {campaign_id}")
    result = run_weekly_optimization(campaign_id)
    print(f"Done: {result.get('analysis', {}).get('overall_health', 'N/A').upper()} | Rewrites: {result.get('rewrites_applied', 0)}")


def cmd_report(args):
    campaign_id = args.campaign
    state = load_campaign_state(campaign_id)
    if not state:
        print(f"Campaign {campaign_id} not found")
        return
    kpis = state.get("kpis", {})
    print(f"\nCampaign Report: {state['project_name']}")
    print(f"  Status:  {state['status']}")
    print(f"  Goal:    ${state['goal_amount']}")
    print(f"  Raised:  ${kpis.get('amount_raised', 0)}")
    print(f"  Donations: {kpis.get('donations', 0)}")
    print(f"  Views:   {kpis.get('views', 0)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fundraising Agent CLI")
    parser.add_argument("--action", choices=["generate", "launch", "update", "optimize", "report"], required=True)
    parser.add_argument("--campaign", help="Campaign ID")
    parser.add_argument("--brief", help="Path to project brief text file")
    parser.add_argument("--niche", help="web3|nonprofit|personal|creative|tech")
    parser.add_argument("--index", help="Update index for --action update")
    args = parser.parse_args()
    {"generate": cmd_generate, "launch": cmd_launch, "update": cmd_update, "optimize": cmd_optimize, "report": cmd_report}[args.action](args)
