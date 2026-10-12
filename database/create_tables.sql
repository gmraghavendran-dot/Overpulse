-- ============================================================
-- OVERPULSE DATABASE SCHEMA
-- Real-Time Cricket Data Engineering Platform
-- ============================================================

-- ============================================================
-- 1. MATCH METADATA
-- ============================================================

CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR(50) PRIMARY KEY,

    competition VARCHAR(100),
    season VARCHAR(20),
    match_type VARCHAR(50),
    gender VARCHAR(20),

    match_date DATE,

    venue VARCHAR(255),
    city VARCHAR(100),

    team1 VARCHAR(150),
    team2 VARCHAR(150),

    toss_winner VARCHAR(150),
    toss_decision VARCHAR(50),

    winner VARCHAR(150),
    winner_runs INTEGER,
    winner_wickets INTEGER,

    player_of_match VARCHAR(255),

    overs INTEGER,

    total_innings INTEGER,

    data_source VARCHAR(100) DEFAULT 'Cricsheet',

    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. BALL-BY-BALL DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS ball_by_ball (

    id BIGSERIAL PRIMARY KEY,

    match_id VARCHAR(50) NOT NULL,

    innings INTEGER,

    batting_team VARCHAR(150),

    over_num INTEGER,

    ball_num INTEGER,

    batter VARCHAR(255),

    non_striker VARCHAR(255),

    bowler VARCHAR(255),

    -- Runs
    runs INTEGER DEFAULT 0,

    runs_off_bat INTEGER DEFAULT 0,

    extras INTEGER DEFAULT 0,

    -- Extras
    wides INTEGER DEFAULT 0,

    noballs INTEGER DEFAULT 0,

    byes INTEGER DEFAULT 0,

    legbyes INTEGER DEFAULT 0,

    penalty_runs INTEGER DEFAULT 0,

    -- Delivery classification
    is_boundary BOOLEAN DEFAULT FALSE,

    is_four BOOLEAN DEFAULT FALSE,

    is_six BOOLEAN DEFAULT FALSE,

    is_dot_ball BOOLEAN DEFAULT FALSE,

    -- Wicket information
    is_wicket BOOLEAN DEFAULT FALSE,

    wicket_type VARCHAR(100),

    player_out VARCHAR(255),

    fielder VARCHAR(255),

    -- Processing metadata
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_match
        FOREIGN KEY (match_id)
        REFERENCES matches(match_id)
        ON DELETE CASCADE
);


-- ============================================================
-- 3. PIPELINE LOGS
-- ============================================================

CREATE TABLE IF NOT EXISTS pipeline_logs (

    id BIGSERIAL PRIMARY KEY,

    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    component VARCHAR(50) NOT NULL,

    event_type VARCHAR(100),

    match_id VARCHAR(50),

    file_name VARCHAR(255),

    records INTEGER DEFAULT 0,

    status VARCHAR(30),

    processing_time_ms BIGINT,

    message TEXT
);


-- ============================================================
-- 4. PIPELINE METRICS
-- ============================================================

CREATE TABLE IF NOT EXISTS pipeline_metrics (

    id BIGSERIAL PRIMARY KEY,

    metric_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    component VARCHAR(50) NOT NULL,

    metric_name VARCHAR(100) NOT NULL,

    metric_value DOUBLE PRECISION,

    metric_unit VARCHAR(50),

    metadata JSONB
);


-- ============================================================
-- 5. INDEXES
-- ============================================================

-- Match lookup
CREATE INDEX IF NOT EXISTS idx_ball_match
ON ball_by_ball(match_id);


-- Match + innings
CREATE INDEX IF NOT EXISTS idx_ball_match_innings
ON ball_by_ball(match_id, innings);


-- Over analysis
CREATE INDEX IF NOT EXISTS idx_ball_over
ON ball_by_ball(match_id, innings, over_num);


-- Batter analytics
CREATE INDEX IF NOT EXISTS idx_batter
ON ball_by_ball(batter);


-- Bowler analytics
CREATE INDEX IF NOT EXISTS idx_bowler
ON ball_by_ball(bowler);


-- Wicket analytics
CREATE INDEX IF NOT EXISTS idx_wickets
ON ball_by_ball(is_wicket);


-- Pipeline monitoring
CREATE INDEX IF NOT EXISTS idx_pipeline_logs_timestamp
ON pipeline_logs(log_timestamp);


CREATE INDEX IF NOT EXISTS idx_pipeline_metrics_timestamp
ON pipeline_metrics(metric_timestamp);


-- ============================================================
-- 6. USEFUL VIEWS
-- ============================================================

-- Total runs by match
CREATE OR REPLACE VIEW match_score_summary AS
SELECT
    match_id,
    innings,
    batting_team,
    SUM(runs) AS total_runs,
    COUNT(*) AS balls,
    SUM(CASE WHEN is_four THEN 1 ELSE 0 END) AS fours,
    SUM(CASE WHEN is_six THEN 1 ELSE 0 END) AS sixes,
    SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END) AS wickets
FROM ball_by_ball
GROUP BY
    match_id,
    innings,
    batting_team;


-- Batter statistics
CREATE OR REPLACE VIEW batter_statistics AS
SELECT
    match_id,
    batter,
    SUM(runs_off_bat) AS runs,
    COUNT(*) AS balls_faced,
    SUM(
        CASE
            WHEN runs_off_bat = 4 THEN 1
            ELSE 0
        END
    ) AS fours,
    SUM(
        CASE
            WHEN runs_off_bat = 6 THEN 1
            ELSE 0
        END
    ) AS sixes
FROM ball_by_ball
GROUP BY
    match_id,
    batter;


-- Bowler statistics
CREATE OR REPLACE VIEW bowler_statistics AS
SELECT
    match_id,
    bowler,
    COUNT(*) AS balls_bowled,
    SUM(runs) AS runs_conceded,
    SUM(
        CASE
            WHEN is_wicket THEN 1
            ELSE 0
        END
    ) AS wickets
FROM ball_by_ball
GROUP BY
    match_id,
    bowler;


-- ============================================================
-- COMPLETE
-- ============================================================

SELECT 'OverPulse database schema created successfully!' AS status;