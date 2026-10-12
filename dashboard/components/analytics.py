import streamlit as st


def render_match_analytics(
    batting,
    bowling,
    boundaries,
    total_runs,
    total_balls
):

    st.markdown("## 📊 Match Analytics")

    # -----------------------------
    # Calculations
    # -----------------------------

    fours = int(boundaries["fours"] or 0)

    sixes = int(boundaries["sixes"] or 0)

    dots = int(boundaries["dots"] or 0)

    singles = total_runs - (fours * 4) - (sixes * 6)

    overs = total_balls / 6 if total_balls else 0

    run_rate = round(
        total_runs / overs,
        2
    ) if overs else 0

    best_batter = "-"

    best_batter_runs = 0

    if not batting.empty:

        best_batter = batting.iloc[0]["batter"]

        best_batter_runs = batting.iloc[0]["runs"]

    best_bowler = "-"

    best_economy = 0

    if not bowling.empty:

        best_bowler = bowling.iloc[0]["bowler"]

        best_economy = bowling.iloc[0]["economy"]

    # -----------------------------
    # First Row
    # -----------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🔥 Fours",
            fours
        )

    with c2:

        st.metric(
            "🚀 Sixes",
            sixes
        )

    with c3:

        st.metric(
            "⚪ Dot Balls",
            dots
        )

    with c4:

        st.metric(
            "⚡ Run Rate",
            run_rate
        )

    st.markdown("")

    # -----------------------------
    # Second Row
    # -----------------------------

    c5, c6, c7, c8 = st.columns(4)

    with c5:

        st.metric(
            "🥇 Best Batter",
            best_batter,
            f"{best_batter_runs} Runs"
        )

    with c6:

        st.metric(
            "🎯 Best Bowler",
            best_bowler,
            f"Econ {best_economy}"
        )

    with c7:

        st.metric(
            "🏃 Singles",
            singles
        )

    with c8:

        st.metric(
            "🏏 Deliveries",
            total_balls
        )