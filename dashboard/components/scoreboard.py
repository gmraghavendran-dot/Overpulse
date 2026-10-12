import streamlit as st


def render_scoreboard(

        total_runs,
        total_balls,
        run_rate,
        fours,
        sixes,
        dot_balls

):

    overs = f"{total_balls//6}.{total_balls%6}"

    st.markdown("""

<div class="scoreboard">

<h1>🏏 LIVE SCOREBOARD</h1>

</div>

""", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.metric(

            "SCORE",

            total_runs

        )

    with c2:

        st.metric(

            "OVERS",

            overs

        )

    with c3:

        st.metric(

            "RUN RATE",

            run_rate

        )

    with c4:

        st.metric(

            "FOURS",

            fours

        )

    with c5:

        st.metric(

            "SIXES",

            sixes
        )

    st.progress(

        min(dot_balls/100,1.0),

        text=f"Dot Balls : {dot_balls}"

    )