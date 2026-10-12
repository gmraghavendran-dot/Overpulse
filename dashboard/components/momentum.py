import streamlit as st
import plotly.graph_objects as go


def momentum_meter(df):

    if df.empty:
        return

    score = df["runs"].sum()

    if score <= 10:
        value = 20

    elif score <= 20:
        value = 40

    elif score <= 30:
        value = 60

    elif score <= 40:
        value = 80

    else:
        value = 100

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=value,

        title={
            "text":"🔥 Match Momentum"
        },

        gauge={

            "axis":{
                "range":[0,100]
            },

            "bar":{
                "color":"red"
            },

            "steps":[

                {
                    "range":[0,25],
                    "color":"#34D399"
                },

                {
                    "range":[25,50],
                    "color":"#FBBF24"
                },

                {
                    "range":[50,75],
                    "color":"#FB923C"
                },

                {
                    "range":[75,100],
                    "color":"#EF4444"
                }

            ]

        }

    ))

    fig.update_layout(
        height=350,
        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )