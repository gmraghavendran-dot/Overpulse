import streamlit as st
from datetime import datetime


def render_command_center(score):

    current_time = datetime.now().strftime("%H:%M:%S")

    st.markdown(
        f"""
        <div style="
        background:linear-gradient(135deg,#071A2B,#123456);
        border-radius:22px;
        padding:30px;
        border:2px solid #22C55E;
        box-shadow:0px 10px 30px rgba(0,0,0,.35);
        ">

        <h1 style="
        color:white;
        text-align:center;
        margin-bottom:10px;
        ">

        🏏 OVERPULSE COMMAND CENTER

        </h1>

        <p style="
        text-align:center;
        color:#9BD8FF;
        font-size:18px;
        ">

        Real-Time Cricket Data Engineering Dashboard

        </p>

        <hr>

        <div style="
        display:flex;
        justify-content:space-around;
        text-align:center;
        ">

            <div>

                <h3 style="color:#22C55E;">
                🟢 LIVE
                </h3>

                <p style="color:white;">
                Streaming
                </p>

            </div>

            <div>

                <h3 style="color:#FFD166;">
                🏏 {score['runs']}/{score['balls']}
                </h3>

                <p style="color:white;">
                Live Score
                </p>

            </div>

            <div>

                <h3 style="color:#7EE787;">
                {score['overs']}
                </h3>

                <p style="color:white;">
                Overs
                </p>

            </div>

            <div>

                <h3 style="color:#66D9EF;">
                {score['run_rate']}
                </h3>

                <p style="color:white;">
                Run Rate
                </p>

            </div>

            <div>

                <h3 style="color:#F87171;">
                {current_time}
                </h3>

                <p style="color:white;">
                Last Refresh
                </p>

            </div>

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )