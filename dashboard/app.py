import os
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils import render_html

from queries import (
    get_total_runs,
    get_total_balls,
    get_latest_deliveries,
    get_runs_per_over,
    get_top_batters,
    get_top_bowlers,
    get_run_distribution,
    get_cumulative_runs,
    get_match_list,
    get_match_info,
    get_current_delivery,
    get_database_stats,
    get_database_rows,
)

from components.sidebar import render_sidebar
from components.header import render_header
from components.live_header import render_live_header
from components import replay

from components.cards import (
    metric_card,
    player_card,
    live_delivery_card,
)

from components.charts import (
    runs_per_over_chart,
    cumulative_chart,
    batter_chart,
    bowler_chart,
    run_distribution_chart,
)

from components.replay import (
    initialize_replay,
    load_match,
    get_visible_data,
    advance_replay,
    get_replay_progress,
    render_replay_controls,
    render_live_replay,
)

from components.commentary import generate_commentary
from components.wagon_wheel import render_wagon_wheel
from components.pipeline import pipeline_monitor


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OverPulse — Real-Time Cricket Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BASE DIRECTORY & CSS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(BASE_DIR, "assets", "style.css")

if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================================================
# GET MATCH LIST & SIDEBAR
# ============================================================

matches = get_match_list()
selected_match = render_sidebar(matches)


# ============================================================
# NO MATCH SELECTED STATE
# ============================================================

if selected_match is None:
    render_html("""
    <div style="text-align:center;padding:80px 20px;background:rgba(15,23,42,0.8);border-radius:24px;border:1px solid rgba(0,255,157,0.2);margin-top:40px;">
        <div style="font-size:64px;margin-bottom:10px;">🏏</div>
        <h1 style="color:#00FF9D;font-family:'Orbitron',sans-serif;font-size:42px;letter-spacing:3px;">OverPulse</h1>
        <p style="color:#CBD5E1;font-size:18px;">Real-Time Cricket Streaming Analytics Platform</p>
        <div style="background:rgba(0,255,157,0.1);display:inline-block;padding:10px 24px;border-radius:20px;color:#00FF9D;font-weight:bold;margin-top:20px;border:1px solid #00FF9D;">
            👈 Select a match from the sidebar Match Center to launch live analytics
        </div>
    </div>
    """)
    st.stop()


# ============================================================
# SELECTED MATCH RESOLUTION
# ============================================================

if isinstance(selected_match, dict):
    selected_match_id = str(selected_match.get("match_id", ""))
else:
    selected_match_id = str(selected_match)

if not selected_match_id:
    st.info("Please select a valid match.")
    st.stop()


# ============================================================
# REPLAY AUTOMATION & DATA RETRIEVAL
# ============================================================

initialize_replay(selected_match_id)

replay_started = st.session_state.get("replay_started", False)
replay_enabled = st.session_state.get("replay_enabled", True)

if replay_started:
    advance_replay(selected_match_id)

visible_data = get_visible_data(selected_match_id)
full_match_data = load_match(selected_match_id)
current_delivery = replay.get_current_delivery(selected_match_id)
match_info = get_match_info(selected_match_id)
current_idx, total_idx, replay_pct = get_replay_progress(selected_match_id)


# ============================================================
# AUTO REFRESH — MUST BE NEAR TOP, BEFORE ALL RENDERS
# Fires every 2 seconds when replay is playing.
# ============================================================

if replay_started:
    st_autorefresh(interval=2000, limit=None, key=f"ar_{selected_match_id}")


# ============================================================
# HEADER & SCOREBOARD
# ============================================================

match_title = ""
if match_info:
    match_title = f"{match_info.get('team1', '')} vs {match_info.get('team2', '')}"
elif isinstance(selected_match, dict):
    match_title = f"{selected_match.get('team1', '')} vs {selected_match.get('team2', '')}"

total_runs = int(visible_data["runs"].sum()) if not visible_data.empty and "runs" in visible_data.columns else 0
total_balls = len(visible_data) if not visible_data.empty else 0
wickets = int(visible_data["is_wicket"].fillna(False).sum()) if not visible_data.empty and "is_wicket" in visible_data.columns else 0

completed_overs = total_balls // 6
balls_in_over = total_balls % 6
overs_display = f"{completed_overs}.{balls_in_over}"

render_header(
    match_title=match_title,
    status="LIVE REPLAY" if replay_started else ("FINISHED" if st.session_state.get("match_finished") else "READY"),
    score=total_runs,
    wickets=wickets,
    overs=overs_display,
    match_info=match_info
)

render_live_header(
    match_info=match_info,
    current_delivery=current_delivery,
    visible_data=visible_data
)


# ============================================================
# REPLAY CONTROLS & PROGRESS
# ============================================================

render_replay_controls(selected_match_id)

render_html(f"""
<div style="margin-top:2px;margin-bottom:16px;">
    <div style="display:flex;justify-content:space-between;color:#94A3B8;font-size:13px;margin-bottom:6px;font-weight:600;">
        <span>DELIVERY {current_idx} / {total_idx}</span>
        <span>{replay_pct:.1f}% REPLAY COMPLETED</span>
    </div>
    <div style="background:rgba(255,255,255,0.08);border-radius:6px;height:8px;overflow:hidden;">
        <div style="height:100%;width:{min(100.0, max(0.0, replay_pct))}%;background:linear-gradient(90deg,#00FF9D,#3B82F6);border-radius:6px;transition:width 0.4s ease;"></div>
    </div>
</div>
""")


# ============================================================
# LIVE COMMENTARY
# ============================================================

st.markdown("### 🎙 Live Commentary")
if current_delivery is not None:
    generate_commentary(current_delivery)


# ============================================================
# MATCH KPI METRICS
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("## 📊 Live Match State")

c1, c2, c3, c4 = st.columns(4)

overs_num = total_balls / 6.0
run_rate = round(total_runs / overs_num, 2) if overs_num > 0 else 0.0

with c1:
    metric_card("SCORE", f"{total_runs} / {wickets}", "🏏", "#00FF9D")
with c2:
    metric_card("RUN RATE", run_rate, "⚡", "#3B82F6")
with c3:
    metric_card("OVERS", overs_display, "⏱", "#FACC15")
with c4:
    metric_card("DELIVERIES", f"{total_balls} / {len(full_match_data)}", "🎯", "#EC4899")


# ============================================================
# CURRENT PLAYER CARDS
# ============================================================

if current_delivery is not None:
    if isinstance(current_delivery, dict):
        current_batter = current_delivery.get("batter", "-")
        current_bowler = current_delivery.get("bowler", "-")
        last_runs = current_delivery.get("runs", 0)
    else:
        current_batter = getattr(current_delivery, "batter", "-")
        current_bowler = getattr(current_delivery, "bowler", "-")
        last_runs = getattr(current_delivery, "runs", 0)
else:
    current_batter = "-"
    current_bowler = "-"
    last_runs = 0

st.markdown("<br>", unsafe_allow_html=True)
p1, p2, p3 = st.columns(3)

with p1:
    player_card("CURRENT BATTER", current_batter, "🏏")
with p2:
    player_card("CURRENT BOWLER", current_bowler, "🎯")
with p3:
    metric_card("LAST DELIVERY", f"{last_runs} RUN(S)", "🔥", "#F59E0B")


# ============================================================
# MATCH ANALYTICS (Manhattan & Worm)
# ============================================================

render_html("<hr style='border-color:rgba(255,255,255,0.1);margin:30px 0;'>")
st.markdown("## 📈 Match Analytics")

if not visible_data.empty:
    runs_per_over = (
        visible_data.groupby("over_num", as_index=False)["runs"]
        .sum()
        .rename(columns={"runs": "total_runs"})
        .sort_values("over_num")
    )
    cumulative = visible_data.copy()
    cumulative["cumulative_runs"] = cumulative["runs"].fillna(0).cumsum()
else:
    runs_per_over = None
    cumulative = None

m_left, m_right = st.columns(2)

with m_left:
    runs_per_over_chart(runs_per_over)
with m_right:
    cumulative_chart(cumulative)


# ============================================================
# PLAYER ANALYTICS (Match vs Entire Database Toggle)
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("## 🏏 Player Analytics")

scope_col1, scope_col2 = st.columns([2, 3])
with scope_col1:
    player_scope = st.radio(
        "Analytics Data Scope:",
        ["Selected Match", "Entire Database (All 1,243+ Matches)"],
        horizontal=True,
        key="player_scope_toggle"
    )

if player_scope == "Entire Database (All 1,243+ Matches)":
    top_batters = get_top_batters(limit=10, match_id=None)
    top_bowlers = get_top_bowlers(limit=10, match_id=None)
else:
    top_batters = get_top_batters(limit=10, match_id=selected_match_id)
    top_bowlers = get_top_bowlers(limit=10, match_id=selected_match_id)

pl_left, pl_right = st.columns(2)

with pl_left:
    batter_chart(top_batters)
with pl_right:
    bowler_chart(top_bowlers)


# ============================================================
# WAGON WHEEL & RUN DISTRIBUTION
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
ww_left, ww_right = st.columns(2)

with ww_left:
    render_wagon_wheel(visible_data)

with ww_right:
    if not visible_data.empty and "runs" in visible_data.columns:
        run_dist = visible_data.groupby("runs").size().reset_index(name="count").sort_values("runs")
    else:
        run_dist = None
    run_distribution_chart(run_dist)


# ============================================================
# LIVE MATCH FEED
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("## 📋 Live Match Feed")

if not visible_data.empty:
    feed_cols = [c for c in ["innings", "over_num", "ball_num", "batter", "bowler", "runs", "is_boundary", "is_wicket"] if c in visible_data.columns]
    feed_df = visible_data[feed_cols].sort_values(["innings", "over_num", "ball_num"], ascending=False).head(20)
    st.dataframe(feed_df, use_container_width=True, hide_index=True, height=350)
else:
    st.info("No deliveries recorded yet.")


# ============================================================
# MATCH RESULT ANNOUNCEMENT
# ============================================================

# Show result ONLY after the replay has fully played through
# (not based on DB winner field, which would show it immediately)
if st.session_state.get("match_finished") and current_idx >= total_idx and total_idx > 0:
    match_winner = ""
    if match_info and match_info.get("winner"):
        match_winner = match_info.get("winner")
    elif isinstance(selected_match, dict) and selected_match.get("winner"):
        match_winner = selected_match.get("winner")

    st.markdown("<br>", unsafe_allow_html=True)
    winner_display = match_winner if match_winner else "Match Completed"
    render_html(f"""
    <div style="background:linear-gradient(135deg,#064E3B,#047857);padding:24px;border-radius:20px;text-align:center;border:2px solid #34D399;box-shadow:0 10px 30px rgba(52,211,153,0.3);">
        <div style="font-size:36px;">🏆</div>
        <h2 style="color:#A7F3D0;margin:6px 0;font-size:28px;">MATCH RESULT</h2>
        <div style="color:white;font-size:22px;font-weight:bold;">{winner_display}</div>
    </div>
    """)


# ============================================================
# PIPELINE HEALTH MONITOR
# ============================================================

render_html("<hr style='border-color:rgba(255,255,255,0.1);margin:30px 0;'>")
db_stats = get_database_stats()
pipeline_monitor(
    database_rows=db_stats.get("total_deliveries", 0),
    total_events=current_idx
)


# ============================================================
# FOOTER
# ============================================================

render_html("""
<div style="text-align:center;padding:30px 0;color:#64748B;font-size:13px;border-top:1px solid rgba(255,255,255,0.08);margin-top:40px;">
    <strong style="color:#00FF9D;">OverPulse</strong> &nbsp;•&nbsp; Real-Time Cricket Streaming Analytics Platform
</div>
""")