import streamlit as st
from utils import render_html


# ==========================================================
# PREMIUM METRIC CARD
# ==========================================================

def metric_card(title, value, icon, color="#22C55E"):

    render_html(f"""
    <div style="background:linear-gradient(135deg,#12263A,#1B3556);padding:22px;border-radius:18px;border-left:6px solid {color};box-shadow:0px 8px 18px rgba(0,0,0,.30);min-height:130px;">
        <div style="color:#A5F3FC;font-size:15px;font-weight:600;letter-spacing:0.5px;">
            {icon} {title}
        </div>
        <div style="color:white;font-size:36px;font-weight:800;margin-top:14px;">
            {value}
        </div>
    </div>
    """)


# ==========================================================
# PLAYER CARD
# ==========================================================

def player_card(title, player, icon):

    render_html(f"""
    <div style="background:#162B45;padding:20px;border-radius:18px;text-align:center;border:2px solid #2ECC71;min-height:130px;">
        <div style="color:#A5F3FC;font-size:15px;font-weight:bold;">
            {icon} {title}
        </div>
        <div style="margin-top:16px;color:white;font-size:24px;font-weight:700;">
            {player}
        </div>
    </div>
    """)


# ==========================================================
# LIVE DELIVERY CARD
# ==========================================================

def live_delivery_card(latest):

    if latest is None:
        st.warning("No Live Data")
        return

    over_val = latest.get("over_num", 0)
    ball_val = latest.get("ball_num", 0)
    batter_val = latest.get("batter", "-")
    bowler_val = latest.get("bowler", "-")
    runs_val = latest.get("runs", 0)

    render_html(f"""
    <div style="background:#12263A;padding:25px;border-radius:18px;border:2px solid #FACC15;box-shadow:0px 8px 20px rgba(0,0,0,.30);">
        <h3 style="color:#FACC15;margin-top:0;display:flex;align-items:center;gap:10px;">
            🔥 Latest Delivery — Over {over_val}.{ball_val}
        </h3>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-top:15px;">
            <div style="background:rgba(255,255,255,0.05);padding:12px 18px;border-radius:12px;">
                <span style="color:#94A3B8;font-size:13px;">BATTER</span><br>
                <strong style="color:white;font-size:18px;">🏏 {batter_val}</strong>
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:12px 18px;border-radius:12px;">
                <span style="color:#94A3B8;font-size:13px;">BOWLER</span><br>
                <strong style="color:white;font-size:18px;">🎯 {bowler_val}</strong>
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:12px 18px;border-radius:12px;">
                <span style="color:#94A3B8;font-size:13px;">RUNS SCORED</span><br>
                <strong style="color:#FACC15;font-size:22px;">⚡ {runs_val} RUNS</strong>
            </div>
        </div>
    </div>
    """)
