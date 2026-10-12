import streamlit as st
import pandas as pd
import json
from utils import render_html


# ============================================================
# OVERPULSE — LIVE MATCH HEADER
# ============================================================

def render_live_header(
    match_info,
    current_delivery,
    visible_data
):

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    if match_info is None and current_delivery is None:
        return

    if isinstance(match_info, pd.Series):
        match_info = match_info.to_dict()
    elif match_info is None:
        match_info = {}

    if isinstance(current_delivery, pd.Series):
        current_delivery = current_delivery.to_dict()
    elif current_delivery is None:
        current_delivery = {}

    # --------------------------------------------------------
    # MATCH INFORMATION
    # --------------------------------------------------------

    team1 = match_info.get("team1") or "Team 1"
    team2 = match_info.get("team2") or "Team 2"
    match_type = match_info.get("match_type") or ""

    # Parse competition — the DB stores it as JSON e.g.
    # {"name":"Indian Premier League","match_number":5}
    # We extract it into a clean readable label.
    raw_competition = match_info.get("competition") or ""
    competition = ""
    try:
        comp_data = json.loads(raw_competition)
        comp_name = comp_data.get("name") or comp_data.get("competition") or ""
        comp_num  = comp_data.get("match_number") or comp_data.get("number") or ""
        comp_stage = comp_data.get("stage") or ""
        if comp_name:
            competition = comp_name
            if comp_num:
                competition += f" • Match {comp_num}"
            if comp_stage:
                competition += f" • {comp_stage}"
        else:
            competition = raw_competition
    except (json.JSONDecodeError, TypeError):
        # Not JSON — use as-is but strip curly braces if present
        competition = str(raw_competition).strip()
        if competition.startswith("{"):
            competition = "Cricket Analytics"

    if not competition:
        competition = "Cricket Analytics"

    # --------------------------------------------------------
    # CURRENT DELIVERY
    # --------------------------------------------------------

    innings = int(current_delivery.get("innings", 1) or 1)
    over_num = int(current_delivery.get("over_num", 0) or 0)
    ball_num = int(current_delivery.get("ball_num", 0) or 0)
    batting_team = current_delivery.get("batting_team") or team1

    # --------------------------------------------------------
    # SCORE CALCULATION
    # --------------------------------------------------------

    if visible_data is not None and not visible_data.empty:
        innings_data = visible_data[visible_data["innings"] == innings] if "innings" in visible_data.columns else visible_data
        total_runs = int(innings_data["runs"].sum()) if "runs" in innings_data.columns else 0
        wickets = int(innings_data["is_wicket"].fillna(False).sum()) if "is_wicket" in innings_data.columns else 0
    else:
        total_runs = int(current_delivery.get("runs", 0) or 0)
        wickets = int(bool(current_delivery.get("is_wicket", False)))

    # --------------------------------------------------------
    # CURRENT BATTER / BOWLER
    # --------------------------------------------------------

    batter = current_delivery.get("batter") or "-"
    bowler = current_delivery.get("bowler") or "-"
    delivery_runs = int(current_delivery.get("runs", 0) or 0)
    is_four = bool(current_delivery.get("is_four", False))
    is_six = bool(current_delivery.get("is_six", False))
    is_wicket = bool(current_delivery.get("is_wicket", False))

    delivery_label = f"{over_num}.{ball_num}"

    if is_wicket:
        delivery_text = "WICKET"
    elif is_six:
        delivery_text = "SIX!"
    elif is_four:
        delivery_text = "FOUR!"
    elif delivery_runs == 0:
        delivery_text = "DOT BALL"
    elif delivery_runs == 1:
        delivery_text = "1 RUN"
    else:
        delivery_text = f"{delivery_runs} RUNS"

    # ========================================================
    # HEADER
    # ========================================================

    render_html(f"""
    <section class="op-live-header" style="background:linear-gradient(135deg,#0F172A,#1E293B);padding:24px;border-radius:20px;border:1px solid rgba(0,255,157,0.25);margin-bottom:20px;box-shadow:0 10px 30px rgba(0,0,0,0.4);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:12px;">
            <div>
                <span style="color:#00FF9D;font-size:12px;font-weight:700;letter-spacing:1px;">
                    {competition} {"• " + match_type if match_type else ""}
                </span>
                <h2 style="color:white;margin:4px 0 0 0;font-size:24px;">
                    {team1} <span style="color:#00FF9D;">vs</span> {team2}
                </h2>
            </div>
            <div style="display:flex;align-items:center;gap:8px;background:rgba(34,197,94,0.15);border:1px solid #22C55E;padding:6px 14px;border-radius:20px;color:#4ADE80;font-weight:bold;font-size:13px;">
                <span style="height:10px;width:10px;background-color:#22C55E;border-radius:50%;display:inline-block;box-shadow:0 0 8px #22C55E;"></span>
                LIVE
            </div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;text-align:center;">
            <div style="background:rgba(255,255,255,0.04);padding:15px;border-radius:14px;">
                <div style="color:#94A3B8;font-size:12px;font-weight:600;">BATTING TEAM</div>
                <div style="color:white;font-size:18px;font-weight:bold;margin-top:4px;">{batting_team}</div>
                <div style="color:#00FF9D;font-size:32px;font-weight:800;margin-top:6px;">{total_runs} <span style="font-size:20px;color:#94A3B8;">/ {wickets}</span></div>
            </div>

            <div style="background:rgba(255,255,255,0.04);padding:15px;border-radius:14px;">
                <div style="color:#94A3B8;font-size:12px;font-weight:600;">CURRENT OVER</div>
                <div style="color:white;font-size:28px;font-weight:bold;margin-top:8px;">{delivery_label}</div>
                <div style="color:#64748B;font-size:12px;margin-top:4px;">Innings {innings}</div>
            </div>

            <div style="background:rgba(255,255,255,0.04);padding:15px;border-radius:14px;">
                <div style="color:#94A3B8;font-size:12px;font-weight:600;">LAST DELIVERY</div>
                <div style="color:#FACC15;font-size:24px;font-weight:bold;margin-top:8px;">{delivery_text}</div>
            </div>

            <div style="background:rgba(255,255,255,0.04);padding:15px;border-radius:14px;text-align:left;">
                <div style="color:#94A3B8;font-size:12px;font-weight:600;">BATTER & BOWLER</div>
                <div style="color:white;font-size:14px;margin-top:6px;">🏏 <strong>{batter}</strong></div>
                <div style="color:white;font-size:14px;margin-top:4px;">🎯 <strong>{bowler}</strong></div>
            </div>
            </div>
        </div>
    </section>
    """)
