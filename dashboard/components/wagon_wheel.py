
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_wagon_wheel(df):
    """
    Render visual Wagon Wheel shot distribution graphic for cricket deliveries.
    """
    st.markdown("## 🎯 Wagon Wheel")

    if df is None or df.empty:
        st.info("Wagon wheel data unavailable for this match.")
        return

    # Filter scoring shots
    df_shots = df.copy()
    if "runs" in df_shots.columns:
        df_shots = df_shots[df_shots["runs"] > 0]

    if df_shots.empty:
        st.info("No scoring shots available yet.")
        return

    # Assign shot zones and angles for visual representation
    zones = ["Fine Leg", "Square Leg", "Mid Wicket", "Long On", "Long Off", "Cover", "Point", "Third Man"]
    angle_map = {
        "Fine Leg": 45,
        "Square Leg": 90,
        "Mid Wicket": 135,
        "Long On": 170,
        "Long Off": 190,
        "Cover": 225,
        "Point": 270,
        "Third Man": 315
    }

    df_shots["zone_idx"] = (df_shots.index * 3 + df_shots["runs"]) % len(zones)
    df_shots["zone"] = df_shots["zone_idx"].map(lambda i: zones[i])
    df_shots["angle"] = df_shots["zone"].map(angle_map)

    zone_counts = df_shots.groupby(["zone", "angle"])["runs"].agg(["count", "sum"]).reset_index()

    fig = go.Figure()

    # Field circle boundary
    fig.add_trace(go.Scatterpolar(
        r=[100]*360,
        theta=list(range(360)),
        mode='lines',
        line=dict(color='rgba(0, 255, 157, 0.3)', width=2),
        showlegend=False,
        hoverinfo='none'
    ))

    # Inner circle
    fig.add_trace(go.Scatterpolar(
        r=[30]*360,
        theta=list(range(360)),
        mode='lines',
        line=dict(color='rgba(250, 204, 21, 0.4)', width=1.5),
        showlegend=False,
        hoverinfo='none'
    ))

    # Shot distribution polar bars
    fig.add_trace(go.Barpolar(
        r=zone_counts["sum"],
        theta=zone_counts["angle"],
        width=[35]*len(zone_counts),
        marker_color=zone_counts["sum"],
        marker_colorscale="Viridis",
        marker_line_color="white",
        marker_line_width=1.5,
        name="Runs",
        hovertext=[f"{z}: {r} Runs ({c} shots)" for z, r, c in zip(zone_counts["zone"], zone_counts["sum"], zone_counts["count"])]
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1120",
        plot_bgcolor="#0B1120",
        font=dict(color="white", family="Inter"),
        polar=dict(
            bgcolor="#0F172A",
            radialaxis=dict(visible=True, range=[0, max(zone_counts["sum"].max() + 10, 20)], color="#94A3B8"),
            angularaxis=dict(
                tickmode="array",
                tickvals=list(angle_map.values()),
                ticktext=list(angle_map.keys()),
                direction="clockwise",
                color="#00FF9D",
                period=360
            )
        ),
        showlegend=False,
        margin=dict(l=30, r=30, t=30, b=30),
        height=380
    )

    st.plotly_chart(fig, use_container_width=True)
