import streamlit as st
from utils import render_html


def pipeline_monitor(database_rows=0, total_events=0):

    st.markdown("## ⚙ Pipeline Health")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_html("""
        <div style="background:#0F172A;padding:16px;border-radius:14px;border:1px solid #22C55E;box-shadow:0 4px 15px rgba(34,197,94,0.15);">
            <div style="color:#4ADE80;font-weight:bold;font-size:14px;display:flex;align-items:center;gap:6px;">
                <span>🟢</span> Kafka Broker
            </div>
            <div style="color:white;font-size:12px;margin-top:8px;">Status: <strong style="color:#22C55E;">RUNNING</strong></div>
        </div>
        """)

    with col2:
        render_html("""
        <div style="background:#0F172A;padding:16px;border-radius:14px;border:1px solid #22C55E;box-shadow:0 4px 15px rgba(34,197,94,0.15);">
            <div style="color:#4ADE80;font-weight:bold;font-size:14px;display:flex;align-items:center;gap:6px;">
                <span>🟢</span> Spark Streaming
            </div>
            <div style="color:white;font-size:12px;margin-top:8px;">Status: <strong style="color:#22C55E;">ACTIVE</strong></div>
        </div>
        """)

    with col3:
        render_html(f"""
        <div style="background:#0F172A;padding:16px;border-radius:14px;border:1px solid #22C55E;box-shadow:0 4px 15px rgba(34,197,94,0.15);">
            <div style="color:#4ADE80;font-weight:bold;font-size:14px;display:flex;align-items:center;gap:6px;">
                <span>🟢</span> PostgreSQL
            </div>
            <div style="color:white;font-size:12px;margin-top:8px;">Deliveries: <strong style="color:#00FF9D;">{database_rows:,}</strong></div>
        </div>
        """)

    with col4:
        render_html(f"""
        <div style="background:#0F172A;padding:16px;border-radius:14px;border:1px solid #22C55E;box-shadow:0 4px 15px rgba(34,197,94,0.15);">
            <div style="color:#4ADE80;font-weight:bold;font-size:14px;display:flex;align-items:center;gap:6px;">
                <span>🟢</span> Dashboard
            </div>
            <div style="color:white;font-size:12px;margin-top:8px;">Events Processed: <strong style="color:#FACC15;">{total_events:,}</strong></div>
        </div>
        """)
