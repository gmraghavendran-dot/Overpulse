import pandas as pd
from db import engine

# ==========================================================
# TOTAL RUNS
# ==========================================================

def get_total_runs():

    query = """
    SELECT
        COALESCE(SUM(runs),0) AS total_runs
    FROM ball_by_ball
    """

    return pd.read_sql(query, engine).iloc[0]["total_runs"]


# ==========================================================
# TOTAL BALLS
# ==========================================================

def get_total_balls():

    query = """
    SELECT
        COUNT(*) AS total_balls
    FROM ball_by_ball
    """

    return pd.read_sql(query, engine).iloc[0]["total_balls"]


# ==========================================================
# DATABASE ROW COUNT
# ==========================================================

def get_database_rows():

    query = """
    SELECT
        COUNT(*) AS total_rows
    FROM ball_by_ball
    """

    return pd.read_sql(query, engine).iloc[0]["total_rows"]


# ==========================================================
# CURRENT DELIVERY
# ==========================================================

def get_current_delivery():

    query = """
    SELECT *
    FROM ball_by_ball
    ORDER BY over_num DESC,
             ball_num DESC
    LIMIT 1
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return None

    return df.iloc[0]


# ==========================================================
# LATEST DELIVERIES
# ==========================================================

def get_latest_deliveries(limit=20):

    query = f"""
    SELECT
        match_id,
        over_num,
        ball_num,
        batter,
        bowler,
        runs
    FROM ball_by_ball
    ORDER BY
        over_num DESC,
        ball_num DESC
    LIMIT {limit}
    """

    return pd.read_sql(query, engine)


# ==========================================================
# RUNS PER OVER
# ==========================================================

def get_runs_per_over():

    query = """
    SELECT
        over_num,
        SUM(runs) AS total_runs
    FROM ball_by_ball
    GROUP BY over_num
    ORDER BY over_num
    """

    return pd.read_sql(query, engine)


# ==========================================================
# TOP BATTERS
# ==========================================================

def get_top_batters(limit=10, match_id=None):

    if match_id:
        query = f"""
        SELECT
            batter,
            SUM(runs) AS runs
        FROM ball_by_ball
        WHERE match_id = '{match_id}'
        GROUP BY batter
        ORDER BY runs DESC
        LIMIT {limit}
        """
    else:
        query = f"""
        SELECT
            batter,
            SUM(runs) AS runs
        FROM ball_by_ball
        GROUP BY batter
        ORDER BY runs DESC
        LIMIT {limit}
        """

    return pd.read_sql(query, engine)


# ==========================================================
# TOP BOWLERS
# ==========================================================

def get_top_bowlers(limit=10, match_id=None):

    if match_id:
        query = f"""
        SELECT
            bowler,
            COUNT(*) AS balls
        FROM ball_by_ball
        WHERE match_id = '{match_id}'
        GROUP BY bowler
        ORDER BY balls DESC
        LIMIT {limit}
        """
    else:
        query = f"""
        SELECT
            bowler,
            COUNT(*) AS balls
        FROM ball_by_ball
        GROUP BY bowler
        ORDER BY balls DESC
        LIMIT {limit}
        """

    return pd.read_sql(query, engine)


# ==========================================================
# DATABASE OVERALL STATS
# ==========================================================

def get_database_stats():

    query = """
    SELECT
        (SELECT COUNT(DISTINCT match_id) FROM ball_by_ball) AS total_matches,
        (SELECT COUNT(*) FROM ball_by_ball) AS total_deliveries,
        (SELECT COALESCE(SUM(runs), 0) FROM ball_by_ball) AS total_runs
    """

    try:
        df = pd.read_sql(query, engine)
        if not df.empty:
            return df.iloc[0].to_dict()
    except Exception:
        pass
    return {"total_matches": 0, "total_deliveries": 0, "total_runs": 0}



# ==========================================================
# RUN DISTRIBUTION
# ==========================================================

def get_run_distribution():

    query = """
    SELECT
        runs,
        COUNT(*) AS count
    FROM ball_by_ball
    GROUP BY runs
    ORDER BY runs
    """

    return pd.read_sql(query, engine)


# ==========================================================
# CUMULATIVE RUNS
# ==========================================================

def get_cumulative_runs():

    query = """
    SELECT
        over_num,
        ball_num,
        SUM(runs) OVER(
            ORDER BY over_num, ball_num
        ) AS cumulative_runs
    FROM ball_by_ball
    """

    return pd.read_sql(query, engine)


# ==========================================================
# MATCH SUMMARY
# ==========================================================

def get_match_summary():

    query = """
    SELECT
        COUNT(*) AS deliveries,
        SUM(runs) AS total_runs,
        COUNT(DISTINCT batter) AS batters,
        COUNT(DISTINCT bowler) AS bowlers,
        MAX(over_num) AS overs_completed
    FROM ball_by_ball
    """

    return pd.read_sql(query, engine).iloc[0]


# ==========================================================
# BOUNDARIES
# ==========================================================

def get_boundary_count():

    query = """
    SELECT
        SUM(CASE WHEN runs = 4 THEN 1 ELSE 0 END) AS fours,
        SUM(CASE WHEN runs = 6 THEN 1 ELSE 0 END) AS sixes
    FROM ball_by_ball
    """

    return pd.read_sql(query, engine).iloc[0]


# ==========================================================
# DOT BALLS
# ==========================================================

def get_dot_balls():

    query = """
    SELECT
        COUNT(*) AS dot_balls
    FROM ball_by_ball
    WHERE runs = 0
    """

    return pd.read_sql(query, engine).iloc[0]["dot_balls"]


# ==========================================================
# PIPELINE STATUS
# ==========================================================

def get_pipeline_status():

    return {
        "Kafka": "🟢 Online",
        "Spark": "🟢 Streaming",
        "PostgreSQL": "🟢 Connected",
        "Dashboard": "🟢 Active"
    }
# ==========================================================
# MOMENTUM DATA
# ==========================================================

def get_recent_runs():

    query = """

    SELECT
        over_num,
        ball_num,
        runs

    FROM ball_by_ball

    ORDER BY
        over_num DESC,
        ball_num DESC

    LIMIT 30

    """

    df = pd.read_sql(query, engine)

    return df.sort_values(
        ["over_num","ball_num"]
    )
# ==========================================================
# GET MATCH LIST
# ==========================================================

def get_match_list():

    query = """
    SELECT
        m.match_id,
        m.team1,
        m.team2,
        m.match_date,
        m.winner

    FROM matches m

    ORDER BY
        m.match_date DESC,
        m.match_id
    """

    df = pd.read_sql(
        query,
        engine
    )

    return df.to_dict(
        orient="records"
    )


# ==========================================================
# FILTERED MATCH DATA
# ==========================================================

def get_match_data(match_id):

    query = """
    SELECT
        id,
        match_id,
        innings,
        batting_team,
        over_num,
        ball_num,
        batter,
        non_striker,
        bowler,
        runs,
        runs_off_bat,
        extras,
        wides,
        noballs,
        byes,
        legbyes,
        penalty_runs,
        is_boundary,
        is_four,
        is_six,
        is_dot_ball,
        is_wicket,
        wicket_type,
        player_out,
        fielder,
        processed_at

    FROM ball_by_ball

    WHERE match_id = %(match_id)s

    ORDER BY
        innings,
        over_num,
        ball_num,
        id
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "match_id": str(match_id)
        }
    )


# ==========================================================
# MATCH INFO
# ==========================================================


def get_match_info(match_id):

    query = """
    SELECT
        match_id,
        competition,
        season,
        match_type,
        team1,
        team2,
        winner,
        winner_runs,
        winner_wickets,
        player_of_match

    FROM matches

    WHERE match_id = %(match_id)s

    LIMIT 1
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "match_id": str(match_id)
        }
    )

    if df.empty:
        return None

    return df.iloc[0].to_dict()


# ==========================================================
# MATCH DELIVERIES FOR LIVE REPLAY
# ==========================================================

def get_match_deliveries(match_id, innings=1):

    query = """
    SELECT
        match_id,
        innings,
        over_num,
        ball_num,
        batter,
        non_striker,
        bowler,
        runs,
        runs_off_bat,
        extras,
        is_boundary,
        is_four,
        is_six,
        is_dot_ball,
        is_wicket,
        wicket_type,
        player_out,
        processed_at

    FROM ball_by_ball

    WHERE match_id = %(match_id)s
      AND innings = %(innings)s

    ORDER BY
        over_num ASC,
        ball_num ASC,
        id ASC
    """

    return pd.read_sql(
        query,
        engine,
        params={
            "match_id": match_id,
            "innings": innings
        }
    )