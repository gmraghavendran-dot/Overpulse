import streamlit as st


def clean_html(html_str):
    if not html_str:
        return ""
    lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    return "\n".join(lines)


def render_html(html_str):
    st.markdown(clean_html(html_str), unsafe_allow_html=True)


def metric_card(title, value):
    st.metric(
        label=title,
        value=value
    )