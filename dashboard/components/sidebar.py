import streamlit as st
import pandas as pd
from utils import render_html
from components.replay import reset_replay


def render_sidebar(matches):
    """
    OverPulse match selector and replay controls.
    """

    with st.sidebar:

        # =====================================================
        # BRAND
        # =====================================================

        render_html("""
        <div class="sidebar-brand">
            <div class="sidebar-logo">🏏</div>
            <div class="sidebar-brand-text">
                <div class="sidebar-title">OverPulse</div>
                <div class="sidebar-subtitle">Cricket Analytics</div>
            </div>
        </div>
        """)

        render_html('<div class="sidebar-divider"></div>')

        # =====================================================
        # MATCH CENTER
        # =====================================================

        render_html('<div class="sidebar-section-title">MATCH CENTER</div>')

        if matches is None:
            st.warning("No matches available.")
            return None

        if isinstance(matches, pd.DataFrame):
            if matches.empty:
                st.warning("No matches available.")
                return None
            matches = matches.to_dict(orient="records")

        try:
            matches = list(matches)
        except Exception:
            st.warning("Unable to load match list.")
            return None

        if len(matches) == 0:
            st.warning("No matches available.")
            return None

        normalized_matches = []

        for match in matches:
            if isinstance(match, dict):
                match_id = str(match.get("match_id", match.get("id", "")))
                team1 = match.get("team1", match.get("home_team", "Unknown Team"))
                team2 = match.get("team2", match.get("away_team", "Unknown Team"))
                match_date = match.get("match_date", match.get("date", ""))
                winner = match.get("winner", "")
            else:
                match_id = str(match)
                team1 = "Match"
                team2 = match_id
                match_date = ""
                winner = ""

            if not match_id.strip():
                continue

            normalized_matches.append({
                "match_id": match_id,
                "team1": str(team1),
                "team2": str(team2),
                "match_date": str(match_date) if match_date else "",
                "winner": str(winner) if winner else ""
            })

        if len(normalized_matches) == 0:
            st.warning("No valid matches found.")
            return None

        match_options = {}
        for match in normalized_matches:
            match_id = match["match_id"]
            team1 = match["team1"]
            team2 = match["team2"]
            label = f"{team1}  vs  {team2}"
            if match["match_date"]:
                label += f"  •  {match['match_date']}"
            label += f"  [{match_id}]"
            match_options[label] = match

        labels = list(match_options.keys())

        previous_match_id = st.session_state.get("selected_match_id")
        default_index = 0

        if previous_match_id is not None:
            previous_match_id = str(previous_match_id)
            for index, match in enumerate(normalized_matches):
                if match["match_id"] == previous_match_id:
                    default_index = index
                    break

        selected_label = st.selectbox(
            "Select Match",
            labels,
            index=default_index,
            key="match_selector"
        )

        selected_match = match_options[selected_label]
        selected_match_id = str(selected_match["match_id"])

        match_changed = (
            previous_match_id is not None
            and str(previous_match_id) != selected_match_id
        )

        if match_changed:
            reset_replay(selected_match_id)

        st.session_state["selected_match_id"] = selected_match_id
        st.session_state["selected_match"] = selected_match

        # Only reveal the winner after the replay has fully completed
        match_finished = st.session_state.get("match_finished", False)
        show_winner = match_finished and bool(selected_match.get("winner"))
        winner_html = (
            f'<div class="selected-match-result" style="color:#22C55E;font-weight:bold;margin-top:8px;">🏆 Winner: {selected_match["winner"]}</div>'
            if show_winner else ""
        )

        render_html(f"""
        <div class="selected-match-card" style="background:#0F172A;padding:16px;border-radius:14px;border:1px solid rgba(0,255,157,0.3);margin-bottom:15px;">
            <div class="selected-match-label" style="color:#00FF9D;font-size:11px;font-weight:700;letter-spacing:1px;">
                SELECTED MATCH
            </div>
            <div class="selected-match-teams" style="color:white;font-size:16px;font-weight:700;margin-top:6px;">
                {selected_match["team1"]} <span style="color:#00FF9D;font-size:12px;">vs</span> {selected_match["team2"]}
            </div>
            <div class="selected-match-id" style="color:#94A3B8;font-size:12px;margin-top:4px;">
                Match ID: {selected_match_id}
            </div>
            {winner_html}
        </div>
        """)


        render_html('<div class="sidebar-section-title">REPLAY</div>')

        replay_enabled = st.toggle(
            "2-second playback",
            value=True,
            key="replay_enabled"
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("▶ Play", use_container_width=True, key="start_replay"):
                st.session_state["replay_started"] = True

        with c2:
            if st.button("⏸ Pause", use_container_width=True, key="pause_replay"):
                st.session_state["replay_started"] = False

        if st.button("↺ Restart Match", use_container_width=True, key="restart_match"):
            reset_replay(selected_match_id)
            st.session_state["replay_started"] = True
            st.rerun()

        render_html('<div class="sidebar-divider"></div>')
        render_html('<div class="sidebar-section-title">SYSTEM</div>')

        render_html("""
        <div style="display:flex;flex-direction:column;gap:8px;font-size:13px;color:#CBD5E1;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span>● Dashboard</span> <span style="color:#22C55E;">ACTIVE</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span>● Live Analytics</span> <span style="color:#22C55E;">ONLINE</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span>● Match History</span> <span style="color:#00FF9D;">1,243 MATCHES</span>
            </div>
        </div>
        """)

        render_html("""
        <div class="sidebar-footer" style="margin-top:20px;padding-top:15px;border-top:1px solid rgba(255,255,255,0.1);color:#64748B;font-size:11px;text-align:center;">
            <div style="color:#00FF9D;font-weight:bold;">OVERPULSE</div>
            <span>Real-Time Cricket Intelligence</span>
        </div>
        """)

    return selected_match
