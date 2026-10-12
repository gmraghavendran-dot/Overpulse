import streamlit as st
from utils import render_html


def generate_commentary(row):

    if row is None:
        return

    runs = row.get("runs", 0)
    batter = row.get("batter", "-")
    bowler = row.get("bowler", "-")
    over_num = row.get("over_num", 0)
    ball_num = row.get("ball_num", 0)
    is_wicket = bool(row.get("is_wicket", False))
    over = f"{over_num}.{ball_num}"

    if is_wicket:
        emoji = "🔴"
        text = "WICKET!!"
        desc = f"Wicket falls! {row.get('player_out', batter)} is out."
        card_color = "#EF4444"
    elif runs == 0:
        emoji = "🛑"
        text = "Dot Ball"
        desc = "Excellent defensive bowling line."
        card_color = "#3B82F6"
    elif runs == 1:
        emoji = "🟢"
        text = "Single"
        desc = "Quick single taken."
        card_color = "#10B981"
    elif runs == 2:
        emoji = "🟡"
        text = "Two Runs"
        desc = "Comfortable double into the gap."
        card_color = "#F59E0B"
    elif runs == 4:
        emoji = "💥"
        text = "FOUR!"
        desc = "Brilliant boundary through the fielders!"
        card_color = "#8B5CF6"
    elif runs == 6:
        emoji = "🚀"
        text = "SIX!!"
        desc = "Monster hit over the boundary line!"
        card_color = "#EC4899"
    else:
        emoji = "🏏"
        text = f"{runs} Runs"
        desc = "Runs added to the scoreboard."
        card_color = "#00FF9D"

    render_html(f"""
    <div style="background:#111827;padding:18px;border-radius:16px;border-left:6px solid {card_color};box-shadow:0 6px 18px rgba(0,0,0,0.3);margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <h4 style="margin:0;color:white;font-size:18px;">{emoji} {text}</h4>
            <span style="background:rgba(255,255,255,0.1);padding:4px 10px;border-radius:10px;color:#A5F3FC;font-size:12px;font-weight:bold;">Over {over}</span>
        </div>
        <div style="color:#CBD5E1;font-size:14px;margin-top:8px;">
            <strong>{bowler}</strong> to <strong>{batter}</strong> — {runs} run(s)
        </div>
        <div style="color:#94A3B8;font-size:13px;margin-top:6px;font-style:italic;">
            {desc}
        </div>
    </div>
    """)
