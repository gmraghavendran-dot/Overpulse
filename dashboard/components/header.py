import streamlit as st
from utils import render_html


def render_header(
    match_title="",
    status="READY",
    score=None,
    wickets=None,
    overs=None,
    match_info=None
):
    """
    Premium OverPulse dashboard header.
    """

    status_upper = str(status).upper()

    score_display = ""
    if score is not None and wickets is not None:
        score_display = f"{score} / {wickets}"
    elif score is not None:
        score_display = f"{score}"

    overs_display = f"Overs: {overs}" if overs is not None else ""

    if match_info and isinstance(match_info, dict):
        team1 = match_info.get("team1", "")
        team2 = match_info.get("team2", "")
        if team1 and team2:
            match_title = f"{team1} vs {team2}"

    match_html = f'<div style="color:white;font-size:18px;font-weight:bold;margin-top:12px;margin-left:44px;">{match_title}</div>' if match_title else ''
    score_html = f'<div style="background:rgba(255,255,255,0.06);padding:10px 18px;border-radius:14px;color:white;font-size:24px;font-weight:800;">{score_display}</div>' if score_display else ''
    overs_html = f'<div style="background:rgba(255,255,255,0.06);padding:10px 18px;border-radius:14px;color:#A5F3FC;font-size:16px;font-weight:bold;">{overs_display}</div>' if overs_display else ''

    render_html(f"""
    <div style="background:linear-gradient(135deg,#0B172A,#162844);padding:24px 30px;border-radius:20px;border:1px solid rgba(0,255,157,0.3);margin-bottom:24px;box-shadow:0 12px 35px rgba(0,0,0,0.4);display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:32px;">🏏</span>
                <div>
                    <h1 style="color:#00FF9D;margin:0;font-size:30px;font-family:'Orbitron',sans-serif;letter-spacing:2px;">OverPulse</h1>
                    <div style="color:#94A3B8;font-size:13px;letter-spacing:0.5px;">Real-Time Cricket Streaming Analytics Platform</div>
                </div>
            </div>
            {match_html}
        </div>

        <div style="display:flex;align-items:center;gap:20px;">
            <div style="display:flex;align-items:center;gap:8px;background:rgba(0,255,157,0.1);border:1px solid #00FF9D;padding:8px 16px;border-radius:25px;color:#00FF9D;font-weight:bold;font-size:13px;">
                <span style="height:10px;width:10px;background-color:#00FF9D;border-radius:50%;display:inline-block;box-shadow:0 0 8px #00FF9D;"></span>
                {status_upper}
            </div>
            {score_html}
            {overs_html}
        </div>
    </div>
    """)
