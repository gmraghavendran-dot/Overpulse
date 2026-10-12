import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ==========================================================
# COMMON THEME
# ==========================================================

def style(fig):

    fig.update_layout(

        template="plotly_dark",

        paper_bgcolor="#0B1120",

        plot_bgcolor="#0B1120",

        font=dict(
            family="Segoe UI",
            color="white",
            size=14
        ),

        title_font=dict(
            size=24,
            color="white"
        ),

        margin=dict(
            l=30,
            r=30,
            t=70,
            b=30
        ),

        hovermode="x unified",

        legend_title_font=dict(size=14),

        legend_font=dict(size=12)
    )

    return fig


# ==========================================================
# MANHATTAN CHART
# ==========================================================

def runs_per_over_chart(df):

    if df.empty:

        st.info("No data available.")

        return

    df = df.copy()

    quality = []

    for r in df["total_runs"]:

        if r <= 3:
            quality.append("Low")

        elif r <= 6:
            quality.append("Normal")

        elif r <= 10:
            quality.append("Good")

        elif r <= 15:
            quality.append("Excellent")

        else:
            quality.append("Explosive")

    df["Quality"] = quality

    fig = px.bar(

        df,

        x="over_num",

        y="total_runs",

        color="Quality",

        text="total_runs",

        title="🏏 Manhattan Chart",

        color_discrete_map={

            "Low":"#3B82F6",

            "Normal":"#22C55E",

            "Good":"#FACC15",

            "Excellent":"#FB923C",

            "Explosive":"#EF4444"

        }

    )

    fig.update_traces(

        textposition="outside",

        marker_line_width=1.5,

        marker_line_color="white"

    )

    fig.update_layout(

        xaxis_title="Overs",

        yaxis_title="Runs"

    )

    style(fig)

    st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# WORM GRAPH
# ==========================================================

def cumulative_chart(df):

    if df.empty:

        st.info("No data available.")

        return

    df = df.copy()

    df["ball"] = (

        df["over_num"].astype(str)

        + "."

        + df["ball_num"].astype(str)

    )

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df["ball"],

            y=df["cumulative_runs"],

            mode="lines+markers",

            line=dict(

                color="#00FF9D",

                width=5

            ),

            marker=dict(

                size=8,

                color="#00FF9D"

            ),

            fill="tozeroy",

            fillcolor="rgba(0,255,157,0.15)",

            name="Runs"

        )

    )

    fig.update_layout(

        title="📈 Worm Graph",

        xaxis_title="Ball",

        yaxis_title="Cumulative Runs"

    )

    style(fig)

    st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# TOP BATTERS
# ==========================================================

def batter_chart(df):

    if df.empty:

        st.info("No data available.")

        return

    fig = px.bar(

        df,

        y="batter",

        x="runs",

        orientation="h",

        color="runs",

        text="runs",

        color_continuous_scale="Turbo",

        title="🏏 Top Batters"

    )

    fig.update_layout(

        yaxis=dict(categoryorder="total ascending")

    )

    style(fig)

    st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# TOP BOWLERS
# ==========================================================

def bowler_chart(df):

    if df.empty:

        st.info("No data available.")

        return

    fig = px.bar(

        df,

        y="bowler",

        x="balls",

        orientation="h",

        color="balls",

        text="balls",

        color_continuous_scale="Blues",

        title="🎯 Top Bowlers"

    )

    fig.update_layout(

        yaxis=dict(categoryorder="total ascending")

    )

    style(fig)

    st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# RUN DISTRIBUTION
# ==========================================================

def run_distribution_chart(df):

    if df.empty:

        st.info("No data available.")

        return

    fig = px.pie(

        df,

        names="runs",

        values="count",

        hole=0.60,

        title="🥧 Run Distribution",

        color_discrete_sequence=px.colors.sequential.Agsunset

    )

    fig.update_traces(

        textposition="inside",

        textinfo="percent+label"

    )

    style(fig)

    st.plotly_chart(fig, use_container_width=True)