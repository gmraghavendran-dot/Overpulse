import pandas as pd
import streamlit as st

from queries import get_match_data
from db import engine


# ============================================================
# LOAD MATCH DATA
# ============================================================

def load_match(match_id):
    """
    Load complete ball-by-ball data for the selected match.
    """

    if match_id is None:
        return pd.DataFrame()

    match_id = str(match_id).strip()

    if not match_id:
        return pd.DataFrame()

    try:

        df = get_match_data(match_id)

        if df is None:
            return pd.DataFrame()

        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)

        if df.empty:
            return pd.DataFrame()

        sort_columns = [
            column
            for column in [
                "innings",
                "over_num",
                "ball_num"
            ]
            if column in df.columns
        ]

        if sort_columns:

            df = (
                df
                .sort_values(sort_columns)
                .reset_index(drop=True)
            )

        return df

    except Exception as e:

        st.error(
            f"Unable to load match data: {e}"
        )

        return pd.DataFrame()


# ============================================================
# REPLAY INITIALIZATION
# ============================================================

def initialize_replay(match_id=None):

    """
    Create replay state for the selected match.
    """

    if match_id is None:
        return

    match_id = str(match_id)

    state_key = f"replay_{match_id}"

    if state_key not in st.session_state:

        st.session_state[state_key] = {
            "index": 0,
            "playing": False,
            "match_id": match_id
        }


# ============================================================
# REPLAY STATE
# ============================================================

def get_replay_state(match_id):

    """
    Return replay state for selected match.
    """

    match_id = str(match_id)

    state_key = f"replay_{match_id}"

    if state_key not in st.session_state:

        initialize_replay(match_id)

    return st.session_state[state_key]


# ============================================================
# CURRENT REPLAY DELIVERY
# ============================================================

def get_current_delivery(match_id):

    """
    Return the delivery currently visible in replay.
    """

    df = load_match(match_id)

    if df.empty:
        return None

    state = get_replay_state(match_id)

    index = state["index"]

    index = max(
        0,
        min(index, len(df) - 1)
    )

    return df.iloc[index]


# ============================================================
# VISIBLE DATA
# ============================================================

def get_visible_data(match_id):

    """
    Return only deliveries that have been revealed
    by the replay.
    """

    df = load_match(match_id)

    if df.empty:
        return pd.DataFrame()

    state = get_replay_state(match_id)

    index = state["index"]

    index = max(
        0,
        min(index, len(df) - 1)
    )

    return df.iloc[
        :index + 1
    ].copy()


# ============================================================
# ADVANCE REPLAY
# ============================================================

def advance_replay(match_id):

    """
    Move replay forward by exactly one delivery.
    """

    df = load_match(match_id)

    if df.empty:
        return

    state = get_replay_state(match_id)

    current_index = state["index"]

    if current_index < len(df) - 1:

        new_index = current_index + 1
        state["index"] = new_index

        # Keep the slider widget's session_state key in sync so it
        # doesn't trigger the "user dragged slider" guard condition
        # when render_replay_controls() reads it back.
        slider_key = f"replay_slider_{match_id}"
        st.session_state[slider_key] = new_index

    else:

        state["playing"] = False

        st.session_state[
            "match_finished"
        ] = True

        st.session_state[
            "replay_started"
        ] = False


# ============================================================
# REPLAY PROGRESS
# ============================================================

def get_replay_progress(match_id):

    """
    Return:

    current delivery
    total deliveries
    percentage completed
    """

    df = load_match(match_id)

    if df.empty:
        return 0, 0, 0.0

    state = get_replay_state(match_id)

    current_index = state["index"]

    total = len(df)

    current = min(
        current_index + 1,
        total
    )

    percentage = (
        current / total
    ) * 100

    return (
        current,
        total,
        percentage
    )


# ============================================================
# REPLAY CONTROLS
# ============================================================

def render_replay_controls(match_id):

    """
    Premium replay controls for the selected match.
    """

    df = load_match(match_id)

    if df.empty:

        st.info(
            "No ball-by-ball data available for this match."
        )

        return

    initialize_replay(match_id)

    state = get_replay_state(match_id)

    st.markdown(
        "### 🎬 Match Replay"
    )

    col1, col2, col3, col4 = st.columns(
        [1, 1, 1, 6]
    )

    # --------------------------------------------------------
    # PREVIOUS
    # --------------------------------------------------------

    with col1:

        if st.button(
            "⏮",
            key=f"replay_prev_{match_id}",
            use_container_width=True
        ):

            state["index"] = max(
                0,
                state["index"] - 1
            )

            state["playing"] = False

            st.session_state[
                "match_finished"
            ] = False

            st.rerun()

    # --------------------------------------------------------
    # PLAY / PAUSE
    # --------------------------------------------------------

    with col2:

        button_text = (
            "⏸"
            if state["playing"]
            else "▶"
        )

        if st.button(
            button_text,
            key=f"replay_play_{match_id}",
            use_container_width=True
        ):

            state["playing"] = (
                not state["playing"]
            )

            st.session_state[
                "replay_started"
            ] = state["playing"]

            if state["playing"]:

                st.session_state[
                    "match_finished"
                ] = False

            st.rerun()

    # --------------------------------------------------------
    # NEXT
    # --------------------------------------------------------

    with col3:

        if st.button(
            "⏭",
            key=f"replay_next_{match_id}",
            use_container_width=True
        ):

            if state["index"] < len(df) - 1:

                state["index"] += 1

                st.session_state[
                    "match_finished"
                ] = False

            else:

                state["playing"] = False

                st.session_state[
                    "match_finished"
                ] = True

            st.rerun()

    # --------------------------------------------------------
    # SLIDER
    # --------------------------------------------------------

    with col4:

        # CRITICAL: Sync the slider's own session_state key to the
        # current replay index BEFORE Streamlit renders the widget.
        # Without this, Streamlit reads the stale slider key value
        # (e.g. 5) while state["index"] is already 6 (advanced by
        # advance_replay). The comparison then fires, resetting index
        # back to 5 and silently stopping the auto-replay every tick.
        slider_key = f"replay_slider_{match_id}"
        st.session_state[slider_key] = state["index"]

        selected_index = st.slider(
            "Delivery",
            min_value=0,
            max_value=len(df) - 1,
            value=state["index"],
            key=slider_key
        )

        # selected_index will now always equal state["index"] during
        # auto-play (because we synced above). It will only differ
        # when the user physically drags the slider — in which case
        # Streamlit updates the key BEFORE this code runs.
        if selected_index != state["index"]:
            state["index"] = selected_index
            state["playing"] = False
            st.session_state["replay_started"] = False
            st.session_state["match_finished"] = False

    # --------------------------------------------------------
    # CURRENT DELIVERY INFORMATION
    # --------------------------------------------------------

    current = df.iloc[
        state["index"]
    ]

    innings = current.get(
        "innings",
        "-"
    )

    over_num = current.get(
        "over_num",
        "-"
    )

    ball_num = current.get(
        "ball_num",
        "-"
    )

    runs = current.get(
        "runs",
        0
    )

    st.caption(
        f"Innings {innings}  •  "
        f"Over {over_num}.{ball_num}  •  "
        f"{runs} run(s)"
    )


# ============================================================
# LIVE REPLAY
# ============================================================

def render_live_replay(match_id):

    """
    Display the delivery currently being replayed.
    """

    delivery = get_current_delivery(
        match_id
    )

    if delivery is None:
        return

    st.markdown(
        "### 🔴 Live Delivery"
    )

    batter = delivery.get(
        "batter",
        "-"
    )

    bowler = delivery.get(
        "bowler",
        "-"
    )

    runs = delivery.get(
        "runs",
        0
    )

    over_num = delivery.get(
        "over_num",
        "-"
    )

    ball_num = delivery.get(
        "ball_num",
        "-"
    )

    # --------------------------------------------------------
    # DELIVERY DISPLAY
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "BALL",
            f"{over_num}.{ball_num}"
        )

    with c2:

        st.metric(
            "BATTER",
            batter
        )

    with c3:

        if runs == 1:

            delivery_text = "1 RUN"

        else:

            delivery_text = (
                f"{runs} RUNS"
            )

        st.metric(
            "DELIVERY",
            delivery_text
        )

    st.caption(
        f"{batter} facing {bowler}"
    )


# ============================================================
# RESET REPLAY
# ============================================================

def reset_replay(match_id):

    """
    Reset selected match replay to first delivery.
    """

    match_id = str(match_id)

    state_key = f"replay_{match_id}"

    if state_key in st.session_state:

        st.session_state[
            state_key
        ]["index"] = 0

        st.session_state[
            state_key
        ]["playing"] = False

    st.session_state[
        "replay_started"
    ] = False

    st.session_state[
        "match_finished"
    ] = False