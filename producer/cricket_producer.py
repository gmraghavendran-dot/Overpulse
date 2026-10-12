import json
import os
import time
from pathlib import Path

from kafka import KafkaProducer


# ============================================================
# OVERPULSE - FULL IPL DATASET PRODUCER
# ============================================================
#
# Reads ALL match JSON files from:
#
#     data/raw/
#
# Sends two types of events to Kafka:
#
#     MATCH
#         ↓
#     Match metadata
#
#     DELIVERY
#         ↓
#     Every ball-by-ball event
#
# Kafka topic:
#
#     cricket-stream
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

KAFKA_SERVER = "localhost:9092"

KAFKA_TOPIC = "cricket-stream"

RAW_DATA_DIR = Path("data/raw")


# ============================================================
# KAFKA PRODUCER
# ============================================================

producer = KafkaProducer(

    bootstrap_servers=KAFKA_SERVER,

    value_serializer=lambda value:
        json.dumps(
            value,
            ensure_ascii=False
        ).encode("utf-8"),

    # Reliability
    acks="all",

    # Allow Kafka to batch messages efficiently
    batch_size=32768,

    linger_ms=10,

    # Retry temporary failures
    retries=5
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_int(value, default=0):

    try:

        if value is None:
            return default

        return int(value)

    except (ValueError, TypeError):

        return default


def get_first_value(value):

    """
    Cricsheet sometimes stores values inside lists.
    This helper safely extracts the first value.
    """

    if isinstance(value, list):

        if len(value) > 0:

            return value[0]

        return None

    return value


def get_match_date(info):

    dates = info.get("dates", [])

    if isinstance(dates, list) and dates:

        return str(dates[0])

    return None


def get_team_names(info):

    teams = info.get("teams", [])

    if isinstance(teams, list):

        team1 = teams[0] if len(teams) > 0 else None

        team2 = teams[1] if len(teams) > 1 else None

        return team1, team2

    return None, None


def get_player_of_match(info):

    awards = info.get("player_of_match", [])

    if isinstance(awards, list) and awards:

        return ", ".join(
            str(player)
            for player in awards
        )

    return None


# ============================================================
# SEND MATCH EVENT
# ============================================================

def send_match_event(
    match_id,
    info,
    source_file
):

    team1, team2 = get_team_names(info)

    outcome = info.get(
        "outcome",
        {}
    )

    winner = outcome.get(
        "winner"
    )

    winner_runs = None

    winner_wickets = None

    if isinstance(
        outcome.get("by"),
        dict
    ):

        by = outcome["by"]

        winner_runs = safe_int(
            by.get("runs"),
            None
        )

        winner_wickets = safe_int(
            by.get("wickets"),
            None
        )

    toss = info.get(
        "toss",
        {}
    )

    event = {

        # ----------------------------------------------------
        # EVENT IDENTIFICATION
        # ----------------------------------------------------

        "record_type": "MATCH",

        "match_id": match_id,

        "source_file": source_file,

        # ----------------------------------------------------
        # MATCH INFORMATION
        # ----------------------------------------------------

        "competition": get_first_value(
            info.get("event", {})
            if isinstance(
                info.get("event"),
                dict
            )
            else None
        ),

        "season": str(
            info.get(
                "season",
                ""
            )
        ),

        "match_type": info.get(
            "match_type"
        ),

        "gender": info.get(
            "gender"
        ),

        "match_date": get_match_date(
            info
        ),

        "venue": info.get(
            "venue"
        ),

        "city": info.get(
            "city"
        ),

        "team1": team1,

        "team2": team2,

        # ----------------------------------------------------
        # TOSS
        # ----------------------------------------------------

        "toss_winner": toss.get(
            "winner"
        ),

        "toss_decision": toss.get(
            "decision"
        ),

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        "winner": winner,

        "winner_runs": winner_runs,

        "winner_wickets": winner_wickets,

        "player_of_match":
            get_player_of_match(info),

        # ----------------------------------------------------
        # GENERAL
        # ----------------------------------------------------

        "overs": safe_int(
            info.get("overs"),
            None
        ),

        "total_innings": None,

        "data_source": "Cricsheet IPL Dataset"
    }

    producer.send(
        KAFKA_TOPIC,
        value=event
    )


# ============================================================
# SEND DELIVERY EVENT
# ============================================================

def send_delivery_event(

    match_id,

    innings_number,

    batting_team,

    over_number,

    ball_number,

    delivery,

    source_file

):

    # --------------------------------------------------------
    # RUN INFORMATION
    # --------------------------------------------------------

    runs_data = delivery.get(
        "runs",
        {}
    )

    total_runs = safe_int(
        runs_data.get("total")
    )

    runs_off_bat = safe_int(
        runs_data.get("batter")
    )

    extras = safe_int(
        runs_data.get("extras")
    )

    # --------------------------------------------------------
    # EXTRA INFORMATION
    # --------------------------------------------------------

    extras_data = delivery.get(
        "extras",
        {}
    )

    wides = safe_int(
        extras_data.get("wides")
    )

    noballs = safe_int(
        extras_data.get("noballs")
    )

    byes = safe_int(
        extras_data.get("byes")
    )

    legbyes = safe_int(
        extras_data.get("legbyes")
    )

    penalty_runs = safe_int(
        extras_data.get("penalty")
    )

    # --------------------------------------------------------
    # WICKET INFORMATION
    # --------------------------------------------------------

    wickets = delivery.get(
        "wickets",
        []
    )

    is_wicket = (
        isinstance(wickets, list)
        and len(wickets) > 0
    )

    wicket_type = None

    player_out = None

    fielder = None

    if is_wicket:

        wicket = wickets[0]

        wicket_type = wicket.get(
            "kind"
        )

        player_out = wicket.get(
            "player_out"
        )

        fielders = wicket.get(
            "fielders",
            []
        )

        if isinstance(
            fielders,
            list
        ) and fielders:

            fielder_names = []

            for f in fielders:

                if isinstance(
                    f,
                    dict
                ):

                    name = f.get(
                        "name"
                    )

                    if name:

                        fielder_names.append(
                            name
                        )

            if fielder_names:

                fielder = ", ".join(
                    fielder_names
                )

    # --------------------------------------------------------
    # BOUNDARIES
    # --------------------------------------------------------

    is_four = (
        runs_off_bat == 4
    )

    is_six = (
        runs_off_bat == 6
    )

    is_boundary = (
        is_four
        or is_six
    )

    # --------------------------------------------------------
    # DOT BALL
    # --------------------------------------------------------

    is_dot_ball = (
        total_runs == 0
    )

    # --------------------------------------------------------
    # CREATE EVENT
    # --------------------------------------------------------

    event = {

        # ----------------------------------------------------
        # EVENT IDENTIFICATION
        # ----------------------------------------------------

        "record_type": "DELIVERY",

        "match_id": match_id,

        "source_file": source_file,

        # ----------------------------------------------------
        # INNINGS
        # ----------------------------------------------------

        "innings": innings_number,

        "batting_team": batting_team,

        # ----------------------------------------------------
        # BALL
        # ----------------------------------------------------

        "over": over_number,

        "ball": ball_number,

        # ----------------------------------------------------
        # PLAYERS
        # ----------------------------------------------------

        "batter": delivery.get(
            "batter"
        ),

        "non_striker": delivery.get(
            "non_striker"
        ),

        "bowler": delivery.get(
            "bowler"
        ),

        # ----------------------------------------------------
        # RUNS
        # ----------------------------------------------------

        "runs": total_runs,

        "runs_off_bat": runs_off_bat,

        "extras": extras,

        # ----------------------------------------------------
        # EXTRAS
        # ----------------------------------------------------

        "wides": wides,

        "noballs": noballs,

        "byes": byes,

        "legbyes": legbyes,

        "penalty_runs": penalty_runs,

        # ----------------------------------------------------
        # CLASSIFICATION
        # ----------------------------------------------------

        "is_boundary": is_boundary,

        "is_four": is_four,

        "is_six": is_six,

        "is_dot_ball": is_dot_ball,

        # ----------------------------------------------------
        # WICKET
        # ----------------------------------------------------

        "is_wicket": is_wicket,

        "wicket_type": wicket_type,

        "player_out": player_out,

        "fielder": fielder,

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        "data_source": "Cricsheet IPL Dataset"
    }

    producer.send(
        KAFKA_TOPIC,
        value=event
    )


# ============================================================
# PROCESS ONE MATCH
# ============================================================

def process_match(
    file_path
):

    match_id = (
        file_path.stem
    )

    source_file = (
        file_path.name
    )

    # --------------------------------------------------------
    # READ JSON
    # --------------------------------------------------------

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            match = json.load(
                file
            )

    except Exception as error:

        print()
        print(
            f"❌ Failed to read "
            f"{source_file}"
        )

        print(error)

        return 0, 0

    info = match.get(
        "meta",
        {}
    )

    info.update(
        match.get(
            "info",
            {}
        )
    )

    # --------------------------------------------------------
    # SEND MATCH EVENT
    # --------------------------------------------------------

    send_match_event(

        match_id,

        info,

        source_file
    )

    match_count = 1

    delivery_count = 0

    # --------------------------------------------------------
    # PROCESS INNINGS
    # --------------------------------------------------------

    innings_list = match.get(
        "innings",
        []
    )

    for innings_index, innings in enumerate(
        innings_list,
        start=1
    ):

        batting_team = innings.get(
            "team"
        )

        overs = innings.get(
            "overs",
            []
        )

        for over_data in overs:

            over_number = safe_int(
                over_data.get(
                    "over"
                )
            )

            deliveries = over_data.get(
                "deliveries",
                []
            )

            for ball_number, delivery in enumerate(
                deliveries,
                start=1
            ):

                send_delivery_event(

                    match_id,

                    innings_index,

                    batting_team,

                    over_number,

                    ball_number,

                    delivery,

                    source_file
                )

                delivery_count += 1

    return (
        match_count,
        delivery_count
    )


# ============================================================
# FIND ALL MATCH FILES
# ============================================================

def get_match_files():

    if not RAW_DATA_DIR.exists():

        print()
        print(
            "❌ RAW DATA DIRECTORY NOT FOUND:"
        )

        print(
            RAW_DATA_DIR.resolve()
        )

        return []

    files = sorted(

        [

            file

            for file in RAW_DATA_DIR.glob(
                "*.json"
            )

            if file.name.lower()
            != "README.json"

        ]

    )

    return files


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print()
    print("=" * 70)
    print("🏏 OVERPULSE FULL DATASET PRODUCER")
    print("=" * 70)

    print(
        f"Kafka       : {KAFKA_SERVER}"
    )

    print(
        f"Topic       : {KAFKA_TOPIC}"
    )

    print(
        f"Dataset     : {RAW_DATA_DIR.resolve()}"
    )

    print("=" * 70)
    print()

    # --------------------------------------------------------
    # FIND FILES
    # --------------------------------------------------------

    match_files = get_match_files()

    total_files = len(
        match_files
    )

    if total_files == 0:

        print(
            "❌ No JSON match files found."
        )

        return

    print(
        f"📁 Match files found : "
        f"{total_files}"
    )

    print()

    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    matches_processed = 0

    deliveries_sent = 0

    failed_files = 0

    start_time = time.time()

    # --------------------------------------------------------
    # PROCESS FILES
    # --------------------------------------------------------

    for index, file_path in enumerate(
        match_files,
        start=1
    ):

        try:

            matches, deliveries = (
                process_match(
                    file_path
                )
            )

            matches_processed += matches

            deliveries_sent += deliveries

        except Exception as error:

            failed_files += 1

            print()
            print(
                f"❌ Failed: "
                f"{file_path.name}"
            )

            print(error)

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        if (
            index % 10 == 0
            or index == total_files
        ):

            elapsed = (
                time.time()
                - start_time
            )

            rate = (

                index / elapsed

                if elapsed > 0

                else 0
            )

            print(
                f"📊 "
                f"Matches: "
                f"{index}/{total_files} | "
                f"Deliveries: "
                f"{deliveries_sent:,} | "
                f"Files/sec: "
                f"{rate:.2f}"
            )

    # --------------------------------------------------------
    # WAIT FOR KAFKA
    # --------------------------------------------------------

    print()
    print(
        "⏳ Flushing Kafka messages..."
    )

    producer.flush()

    # --------------------------------------------------------
    # FINAL STATISTICS
    # --------------------------------------------------------

    elapsed = (
        time.time()
        - start_time
    )

    print()
    print("=" * 70)
    print("🏏 DATASET INGESTION COMPLETED")
    print("=" * 70)

    print(
        f"Files discovered    : "
        f"{total_files:,}"
    )

    print(
        f"Matches processed   : "
        f"{matches_processed:,}"
    )

    print(
        f"Deliveries sent     : "
        f"{deliveries_sent:,}"
    )

    print(
        f"Failed files        : "
        f"{failed_files:,}"
    )

    print(
        f"Processing time     : "
        f"{elapsed:.2f} seconds"
    )

    if elapsed > 0:

        print(
            f"Processing rate     : "
            f"{total_files / elapsed:.2f} files/sec"
        )

    print("=" * 70)
    print()
    print(
        "🔥 Full IPL dataset streamed to Kafka!"
    )
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print(
            "🛑 Producer stopped by user."
        )

    finally:

        producer.flush()

        producer.close()

        print(
            "Kafka producer closed."
        )