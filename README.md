<div align="center">

<h1>🏏 OverPulse</h1>
<p><strong>Real-Time Cricket Streaming Analytics Platform</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white"/>
  <img src="https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
</p>

<p><em>End-to-end data engineering pipeline for live ball-by-ball cricket analytics — streaming, processing, storing, and visualising every delivery in real time.</em></p>

</div>

---

## 📌 Overview

**OverPulse** is a production-grade, end-to-end data streaming and analytics platform built specifically for cricket. It simulates a real-time match feed by ingesting **Cricsheet** ball-by-ball JSON datasets through **Apache Kafka**, processes each delivery event using **Apache Spark Structured Streaming**, persists aggregated match data into **PostgreSQL**, and surfaces rich live analytics through a sleek dark-themed **Streamlit** web dashboard.

The platform currently holds **1,243 matches**, **295,732 deliveries**, and **401,738 total runs** — all queryable in real time from the dashboard.

---

## ✨ Features

### 🔴 Live Match Replay Engine
- Select any match from 1,243+ IPL fixtures and replay it ball-by-ball
- Auto-refresh every 2 seconds during replay with a delivery progress bar
- Play / Pause / Reset controls per match session
- Match result revealed only after the full replay completes

### 🎙 Live Commentary Feed
- Delivery-level colour-coded commentary for every ball
- Distinct visual cards for: Dot Ball 🛑 · Single 🟢 · Two Runs 🟡 · Four 💥 · Six 🚀 · Wicket 🔴

### 📊 Match KPI Metrics
- Live score card (runs / wickets)
- Current run rate
- Overs completed (e.g. `14.3`)
- Deliveries processed vs. total deliveries in the match

### 📈 Analytics Charts (Plotly)
- **Manhattan Chart** — runs scored per over (bar chart)
- **Worm Chart** — cumulative runs progression across the innings
- **Top Batters** — runs scored per batter (match or all-time scope)
- **Top Bowlers** — balls bowled per bowler (match or all-time scope)
- **Run Distribution** — frequency of dot balls, 1s, 2s, 4s, 6s
- **Wagon Wheel** — polar shot-zone distribution visualising where runs were scored

### ⚙️ Pipeline Health Monitor
Real-time status panel showing the health of each layer:

| Layer | Status |
|:---|:---|
| Kafka Broker | 🟢 RUNNING |
| Spark Streaming | 🟢 ACTIVE |
| PostgreSQL | 🟢 Connected — delivery count shown live |
| Dashboard | 🟢 Active — events processed counter |

### 🏆 Match Centre Sidebar
- Searchable match list ordered by date (newest first)
- Displays both teams and the match winner per fixture

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        DATA SOURCE                           │
│          Cricsheet Ball-by-Ball JSON Files (data/raw/)       │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    KAFKA PRODUCER                            │
│         producer/cricket_producer.py                         │
│                                                              │
│  Reads each match JSON → emits two event types:             │
│    • MATCH  → match metadata (teams, toss, outcome, etc.)   │
│    • DELIVERY → every ball-by-ball delivery event           │
│                                                              │
│  Topic: cricket-stream  |  Broker: localhost:9092           │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                APACHE KAFKA BROKER                           │
│                 localhost:9092                               │
│          Topic: cricket-stream                               │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│             APACHE SPARK STRUCTURED STREAMING                │
│         spark_jobs/spark_stream_processor.py                 │
│                                                              │
│  • Reads stream from Kafka (maxOffsetsPerTrigger: 5,000)    │
│  • Parses MATCH events → inserts into matches table         │
│  • Parses DELIVERY events → inserts into ball_by_ball table │
│  • JDBC sink to PostgreSQL via postgresql-42.7.12.jar        │
│  • Checkpoints state to disk for fault tolerance            │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE                        │
│                  Database: data_obs                          │
│                                                              │
│  Tables: matches | ball_by_ball | pipeline_logs             │
│          pipeline_metrics                                    │
│  Views:  match_score_summary | batter_statistics            │
│          bowler_statistics                                   │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│              STREAMLIT LIVE DASHBOARD                        │
│                 dashboard/app.py                             │
│                                                              │
│  Queries PostgreSQL in real time via SQLAlchemy engine       │
│  Auto-refreshes every 2s during active replay               │
│  Renders: Scoreboard · Commentary · KPI Cards · Charts       │
│           Player Analytics · Wagon Wheel · Pipeline Monitor  │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Overpulse/
│
├── producer/
│   ├── cricket_producer.py       # Kafka producer — streams all match events
│   └── file_discovery.py         # Scans data/raw/ for JSON match files
│
├── spark_jobs/
│   ├── spark_stream_processor.py # Main PySpark Structured Streaming job
│   └── kafka_stream_processor.py # Alternate lightweight Kafka processor
│
├── dashboard/
│   ├── app.py                    # Streamlit main entrypoint
│   ├── db.py                     # SQLAlchemy engine (PostgreSQL connection)
│   ├── queries.py                # All SQL query functions
│   ├── utils.py                  # HTML rendering helpers
│   ├── assets/
│   │   ├── style.css             # Dark cyberpunk theme styling
│   │   ├── logo.png              # OverPulse logo
│   │   └── stadium.jpg           # Background asset
│   └── components/
│       ├── sidebar.py            # Match Centre sidebar
│       ├── header.py             # Match title & status header
│       ├── live_header.py        # Live delivery header bar
│       ├── cards.py              # KPI metric cards & player cards
│       ├── charts.py             # Manhattan, Worm, Batter, Bowler, Distribution charts
│       ├── commentary.py         # Ball-by-ball commentary generator
│       ├── wagon_wheel.py        # Polar shot-zone Wagon Wheel chart
│       ├── replay.py             # Match replay state machine & controls
│       ├── pipeline.py           # Pipeline health monitor panel
│       ├── analytics.py          # Extended analytics components
│       ├── scoreboard.py         # Full innings scoreboard
│       ├── momentum.py           # Momentum trend component
│       └── command_center.py     # Command centre layout
│
├── database/
│   ├── create_tables.sql         # Full PostgreSQL schema (tables, indexes, views)
│   └── db_connection.py          # Standalone DB connection test utility
│
├── data/
│   └── raw/                      # 1,243 Cricsheet ball-by-ball JSON match files
│
├── jars/
│   └── postgresql-42.7.12.jar    # PostgreSQL JDBC driver for Spark
│
├── checkpoints/                  # Spark streaming checkpoint directory
├── logs/                         # Application log output
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🗄️ Database Schema

### `matches`
Stores high-level metadata for every match.

| Column | Type | Description |
|:---|:---|:---|
| `match_id` | VARCHAR(50) PK | Unique match identifier |
| `competition` | VARCHAR(100) | Tournament name |
| `season` | VARCHAR(20) | Season year |
| `match_type` | VARCHAR(50) | T20, ODI, Test, etc. |
| `team1` / `team2` | VARCHAR(150) | Competing teams |
| `toss_winner` | VARCHAR(150) | Toss-winning team |
| `toss_decision` | VARCHAR(50) | Bat or field |
| `winner` | VARCHAR(150) | Match winner |
| `winner_runs` / `winner_wickets` | INTEGER | Margin of victory |
| `player_of_match` | VARCHAR(255) | Award winner |
| `ingested_at` | TIMESTAMP | Pipeline ingestion time |

### `ball_by_ball`
Granular delivery-level data — one row per ball bowled.

| Column | Type | Description |
|:---|:---|:---|
| `match_id` | VARCHAR(50) FK | Parent match |
| `innings` | INTEGER | 1st or 2nd innings |
| `batting_team` | VARCHAR(150) | Team at bat |
| `over_num` | INTEGER | Over number (0-indexed) |
| `ball_num` | INTEGER | Ball within the over |
| `batter` / `bowler` | VARCHAR(255) | Player names |
| `runs` | INTEGER | Total runs on the delivery |
| `runs_off_bat` | INTEGER | Runs scored off the bat |
| `extras` | INTEGER | Total extras |
| `wides` / `noballs` / `byes` / `legbyes` | INTEGER | Extras breakdown |
| `is_boundary` / `is_four` / `is_six` | BOOLEAN | Boundary flags |
| `is_dot_ball` | BOOLEAN | Dot ball flag |
| `is_wicket` | BOOLEAN | Wicket flag |
| `wicket_type` | VARCHAR(100) | Caught / Bowled / LBW, etc. |
| `player_out` / `fielder` | VARCHAR(255) | Dismissal details |
| `processed_at` | TIMESTAMP | Spark processing timestamp |

### Views
| View | Description |
|:---|:---|
| `match_score_summary` | Runs, balls, fours, sixes, wickets per innings |
| `batter_statistics` | Per-batter runs, balls faced, boundaries per match |
| `bowler_statistics` | Per-bowler balls bowled, runs conceded, wickets per match |

### Indexes
Optimised indexes on `match_id`, `innings`, `over_num`, `batter`, `bowler`, and `is_wicket` for fast analytical queries.

---

## ⚙️ Prerequisites

| Requirement | Version |
|:---|:---|
| Python | 3.12 |
| Apache Kafka | 2.x / 3.x |
| Apache Spark | 4.x (PySpark) |
| PostgreSQL | 13+ |
| Java (JDK) | 11+ (required by Spark) |

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/gmraghavendran-dot/Overpulse.git
cd Overpulse
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL

```sql
-- Create the database
CREATE DATABASE data_obs;

-- Run the schema file
\i database/create_tables.sql
```

### 5. Configure Credentials

Update the credentials in the following files to match your environment:

| File | Setting |
|:---|:---|
| `dashboard/db.py` | `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` |
| `spark_jobs/spark_stream_processor.py` | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_URL` |

### 6. Start Kafka

Make sure your Kafka broker is running locally on `localhost:9092` and the topic `cricket-stream` is created:

```bash
# Create the topic (if not already created)
kafka-topics.sh --create --topic cricket-stream --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

---

## ▶️ Running the Platform

Run each component in a **separate terminal**:

### Step 1 — Start the Streamlit Dashboard
```bash
python -m streamlit run dashboard/app.py
```
> Opens at **http://localhost:8501**

### Step 2 — Start the Spark Stream Processor
```bash
python spark_jobs/spark_stream_processor.py
```
> Spark reads from Kafka and writes to PostgreSQL in micro-batches (every 5,000 offsets).

### Step 3 — Start the Kafka Producer (simulate live feed)
```bash
python producer/cricket_producer.py
```
> Streams all 1,243 match files from `data/raw/` into the `cricket-stream` Kafka topic.

---

## 🖥️ Dashboard Walkthrough

Once running, navigate to [http://localhost:8501](http://localhost:8501):

1. **Match Centre (Sidebar)** — Browse and select any of 1,243+ IPL matches.
2. **Live Header** — Displays current match status, teams, and score.
3. **Replay Controls** — Hit ▶️ Play to start ball-by-ball replay. Delivery progress bar advances in real time.
4. **Commentary** — Each delivery generates a colour-coded commentary card (dot / single / boundary / wicket).
5. **KPI Cards** — Score, Run Rate, Overs, and Deliveries updated live.
6. **Player Cards** — Current batter, bowler, and last delivery runs.
7. **Analytics** — Manhattan bar chart and worm cumulative run curve side by side.
8. **Player Analytics Toggle** — Switch between selected-match stats and all-time database stats (across 1,243+ matches).
9. **Wagon Wheel** — Polar chart showing shot-zone distribution.
10. **Run Distribution** — Frequency histogram of runs scored per delivery.
11. **Live Match Feed** — Scrollable last-20-deliveries table, sorted newest first.
12. **Match Result** — Displayed only after the full replay completes.
13. **Pipeline Monitor** — Real-time health of Kafka, Spark, PostgreSQL, and Dashboard.

---

## 📦 Data Source

Ball-by-ball match data is sourced from **[Cricsheet](https://cricsheet.org/)** — an open, freely available ball-by-ball cricket dataset in JSON format. The `data/raw/` directory contains **1,243 IPL match files** spanning multiple seasons.

---

## 🛠️ Tech Stack

| Layer | Technology |
|:---|:---|
| **Message Broker** | Apache Kafka |
| **Stream Processing** | Apache Spark Structured Streaming (PySpark 4.x) |
| **Database** | PostgreSQL 13+ with SQLAlchemy |
| **JDBC Driver** | `postgresql-42.7.12.jar` |
| **Dashboard** | Streamlit + Plotly + streamlit-autorefresh |
| **Language** | Python 3.12 |
| **Data Format** | JSON (Cricsheet) |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is open source. Data sourced from [Cricsheet](https://cricsheet.org/) under their open data terms.

---

<div align="center">
  <strong>OverPulse</strong> &nbsp;•&nbsp; Built with 🏏 and real-time data engineering
</div>