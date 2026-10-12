import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    current_timestamp
)

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    BooleanType
)


# ============================================================
# PYTHON CONFIGURATION
# ============================================================

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


# ============================================================
# CONFIGURATION
# ============================================================

KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "cricket-stream"

POSTGRES_URL = (
    "jdbc:postgresql://localhost:5432/data_obs"
)

POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "raga2005"

POSTGRES_DRIVER = "org.postgresql.Driver"

CHECKPOINT = "C:/Dataobs platform/data/checkpoints/cricket_stream"


# ============================================================
# SPARK SESSION
# ============================================================

spark = (
    SparkSession.builder
    .appName("OverPulseFullDatasetPipeline")

    # IMPORTANT:
    # Don't use local[*] for this huge local streaming job.
    .master("local[2]")

    # PostgreSQL JDBC
    .config(
        "spark.jars",
        "jars/postgresql-42.7.12.jar"
    )

    # Kafka connector
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.3"
    )

    # Stability
    .config(
        "spark.sql.shuffle.partitions",
        "2"
    )

    .config(
        "spark.default.parallelism",
        "2"
    )

    .config(
        "spark.network.timeout",
        "120s"
    )

    .config(
        "spark.executor.heartbeatInterval",
        "30s"
    )

    .config(
        "spark.sql.debug.maxToStringFields",
        "200"
    )

    .getOrCreate()
)


spark.sparkContext.setLogLevel("WARN")

spark.conf.set(
    "spark.sql.streaming.metricsEnabled",
    "false"
)


# ============================================================
# STARTUP INFORMATION
# ============================================================

print()
print("=" * 70)
print("🏏 OVERPULSE FULL DATA PIPELINE")
print("=" * 70)

print(
    "Spark Version :", spark.version
)

print(
    "Kafka         :", KAFKA_SERVER
)

print(
    "Topic         :", KAFKA_TOPIC
)

print(
    "Database      :", "data_obs"
)

print(
    "Checkpoint    :", CHECKPOINT
)

print("=" * 70)
print()


# ============================================================
# KAFKA RAW STREAM
# ============================================================

raw_stream = (
    spark.readStream
    .format("kafka")

    .option(
        "kafka.bootstrap.servers",
        KAFKA_SERVER
    )

    .option(
        "subscribe",
        KAFKA_TOPIC
    )

    # IMPORTANT:
    # Read existing events already stored in Kafka.
    .option(
        "startingOffsets",
        "earliest"
    )

    # CRITICAL:
    # Don't allow Spark to swallow millions of events
    # in one micro-batch.
    .option(
        "maxOffsetsPerTrigger",
        "5000"
    )

    .option(
        "failOnDataLoss",
        "false"
    )

    .load()
)


# ============================================================
# COMMON KAFKA JSON
# ============================================================

json_stream = (
    raw_stream
    .selectExpr(
        "CAST(value AS STRING) AS json_value"
    )
)


# ============================================================
# DELIVERY SCHEMA
# ============================================================

delivery_schema = StructType([

    StructField(
        "record_type",
        StringType(),
        True
    ),

    StructField(
        "match_id",
        StringType(),
        True
    ),

    StructField(
        "source_file",
        StringType(),
        True
    ),

    StructField(
        "innings",
        IntegerType(),
        True
    ),

    StructField(
        "batting_team",
        StringType(),
        True
    ),

    StructField(
        "over",
        IntegerType(),
        True
    ),

    StructField(
        "ball",
        IntegerType(),
        True
    ),

    StructField(
        "batter",
        StringType(),
        True
    ),

    StructField(
        "non_striker",
        StringType(),
        True
    ),

    StructField(
        "bowler",
        StringType(),
        True
    ),

    StructField(
        "runs",
        IntegerType(),
        True
    ),

    StructField(
        "runs_off_bat",
        IntegerType(),
        True
    ),

    StructField(
        "extras",
        IntegerType(),
        True
    ),

    StructField(
        "wides",
        IntegerType(),
        True
    ),

    StructField(
        "noballs",
        IntegerType(),
        True
    ),

    StructField(
        "byes",
        IntegerType(),
        True
    ),

    StructField(
        "legbyes",
        IntegerType(),
        True
    ),

    StructField(
        "penalty_runs",
        IntegerType(),
        True
    ),

    StructField(
        "is_boundary",
        BooleanType(),
        True
    ),

    StructField(
        "is_four",
        BooleanType(),
        True
    ),

    StructField(
        "is_six",
        BooleanType(),
        True
    ),

    StructField(
        "is_dot_ball",
        BooleanType(),
        True
    ),

    StructField(
        "is_wicket",
        BooleanType(),
        True
    ),

    StructField(
        "wicket_type",
        StringType(),
        True
    ),

    StructField(
        "player_out",
        StringType(),
        True
    ),

    StructField(
        "fielder",
        StringType(),
        True
    ),

    StructField(
        "data_source",
        StringType(),
        True
    )
])


# ============================================================
# MATCH SCHEMA
# ============================================================

match_schema = StructType([

    StructField(
        "record_type",
        StringType(),
        True
    ),

    StructField(
        "match_id",
        StringType(),
        True
    ),

    StructField(
        "source_file",
        StringType(),
        True
    ),

    StructField(
        "competition",
        StringType(),
        True
    ),

    StructField(
        "season",
        StringType(),
        True
    ),

    StructField(
        "match_type",
        StringType(),
        True
    ),

    StructField(
        "gender",
        StringType(),
        True
    ),

    StructField(
        "match_date",
        StringType(),
        True
    ),

    StructField(
        "venue",
        StringType(),
        True
    ),

    StructField(
        "city",
        StringType(),
        True
    ),

    StructField(
        "team1",
        StringType(),
        True
    ),

    StructField(
        "team2",
        StringType(),
        True
    ),

    StructField(
        "toss_winner",
        StringType(),
        True
    ),

    StructField(
        "toss_decision",
        StringType(),
        True
    ),

    StructField(
        "winner",
        StringType(),
        True
    ),

    StructField(
        "winner_runs",
        IntegerType(),
        True
    ),

    StructField(
        "winner_wickets",
        IntegerType(),
        True
    ),

    StructField(
        "player_of_match",
        StringType(),
        True
    ),

    StructField(
        "overs",
        IntegerType(),
        True
    ),

    StructField(
        "total_innings",
        IntegerType(),
        True
    ),

    StructField(
        "data_source",
        StringType(),
        True
    )
])


# ============================================================
# PARSE DELIVERY EVENTS
# ============================================================

delivery_df = (
    json_stream

    .select(
        from_json(
            col("json_value"),
            delivery_schema
        ).alias("data")
    )

    .select("data.*")

    # ONLY DELIVERY EVENTS
    .filter(
        col("record_type") == "DELIVERY"
    )

    .withColumnRenamed(
        "over",
        "over_num"
    )

    .withColumnRenamed(
        "ball",
        "ball_num"
    )

    .withColumn(
        "processed_at",
        current_timestamp()
    )
)


# ============================================================
# PARSE MATCH EVENTS
# ============================================================

match_df = (
    json_stream

    .select(
        from_json(
            col("json_value"),
            match_schema
        ).alias("data")
    )

    .select("data.*")

    # ONLY MATCH EVENTS
    .filter(
        col("record_type") == "MATCH"
    )

    .withColumn(
        "processed_at",
        current_timestamp()
    )
)


# ============================================================
# POSTGRES CONFIGURATION
# ============================================================

postgres_properties = {

    "user":
        POSTGRES_USER,

    "password":
        POSTGRES_PASSWORD,

    "driver":
        POSTGRES_DRIVER
}


# ============================================================
# WRITE DELIVERIES
# ============================================================

def write_deliveries(batch_df, batch_id):

    print()
    print("-" * 70)
    print(f"🏏 DELIVERY BATCH {batch_id}")

    count = batch_df.count()

    print(f"Records : {count:,}")

    if count == 0:
        print("No delivery records.")
        return

    # --------------------------------------------------------
    # Remove duplicates inside the current Spark micro-batch
    # --------------------------------------------------------

    batch_df = (
        batch_df
        .dropDuplicates([
            "match_id",
            "innings",
            "over_num",
            "ball_num"
        ])
    )

    unique_count = batch_df.count()

    print(
        f"Unique records in batch : {unique_count:,}"
    )

    # --------------------------------------------------------
    # Write batch to PostgreSQL staging table
    # --------------------------------------------------------

    staging_table = "ball_by_ball_staging"

    (
        batch_df
        .write
        .mode("overwrite")
        .jdbc(
            url=POSTGRES_URL,
            table=staging_table,
            properties=postgres_properties
        )
    )

    # --------------------------------------------------------
    # Insert into real table with conflict protection
    # --------------------------------------------------------

    import psycopg2

    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        database="data_obs",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

    try:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO ball_by_ball (
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
                processed_at,
                record_type,
                source_file,
                data_source
            )
            SELECT
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
                processed_at,
                record_type,
                source_file,
                data_source
            FROM ball_by_ball_staging

            ON CONFLICT (
                match_id,
                innings,
                over_num,
                ball_num
            )
            DO NOTHING;
        """)

        connection.commit()

        print(
            "✅ Deliveries inserted "
            "without duplicates"
        )

    except Exception as e:

        connection.rollback()

        print(
            "❌ PostgreSQL delivery error:"
        )

        print(e)

        raise

    finally:

        cursor.close()
        connection.close()

    print("-" * 70)


# ============================================================
# WRITE MATCHES
# ============================================================

def write_matches(batch_df, batch_id):

    print()
    print("-" * 70)
    print(f"🏆 MATCH BATCH {batch_id}")

    count = batch_df.count()

    print(f"Records : {count:,}")

    if count == 0:
        print("No match records.")
        return

    # --------------------------------------------------------
    # Remove duplicate MATCH events inside Spark batch
    # --------------------------------------------------------

    batch_df = (
        batch_df
        .dropDuplicates([
            "match_id"
        ])
    )

    unique_count = batch_df.count()

    print(
        f"Unique matches in batch : "
        f"{unique_count:,}"
    )

    # --------------------------------------------------------
    # Prepare PostgreSQL-compatible data
    # --------------------------------------------------------

    matches_to_write = (
        batch_df
        .select(
            "match_id",
            "competition",
            "season",
            "match_type",
            "gender",
            "match_date",
            "venue",
            "city",
            "team1",
            "team2",
            "toss_winner",
            "toss_decision",
            "winner",
            "winner_runs",
            "winner_wickets",
            "player_of_match",
            "overs",
            "total_innings",
            "data_source",
            "processed_at"
        )
        .withColumnRenamed(
            "processed_at",
            "ingested_at"
        )
        .withColumn(
            "match_date",
            col("match_date").cast("date")
        )
    )

    # --------------------------------------------------------
    # Staging table
    # --------------------------------------------------------

    staging_table = "matches_staging"

    (
        matches_to_write
        .write
        .mode("overwrite")
        .jdbc(
            url=POSTGRES_URL,
            table=staging_table,
            properties=postgres_properties
        )
    )

    # --------------------------------------------------------
    # Insert only new matches
    # --------------------------------------------------------

    import psycopg2

    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        database="data_obs",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

    try:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO matches (
                match_id,
                competition,
                season,
                match_type,
                gender,
                match_date,
                venue,
                city,
                team1,
                team2,
                toss_winner,
                toss_decision,
                winner,
                winner_runs,
                winner_wickets,
                player_of_match,
                overs,
                total_innings,
                data_source,
                ingested_at
            )
            SELECT
                match_id,
                competition,
                season,
                match_type,
                gender,
                match_date,
                venue,
                city,
                team1,
                team2,
                toss_winner,
                toss_decision,
                winner,
                winner_runs,
                winner_wickets,
                player_of_match,
                overs,
                total_innings,
                data_source,
                ingested_at
            FROM matches_staging

            ON CONFLICT (match_id)
            DO NOTHING;
        """)

        connection.commit()

        print(
            "✅ Matches inserted "
            "without duplicates"
        )

    except Exception as e:

        connection.rollback()

        print(
            "❌ PostgreSQL match error:"
        )

        print(e)

        raise

    finally:

        cursor.close()
        connection.close()

    print("-" * 70)


# ============================================================
# DELIVERY STREAM
# ============================================================

delivery_query = (
    delivery_df

    .writeStream

    .foreachBatch(
        write_deliveries
    )

    .outputMode(
        "append"
    )

    .option(
        "checkpointLocation",
        CHECKPOINT + "/deliveries"
    )

    .trigger(
        processingTime="10 seconds"
    )

    .start()
)


# ============================================================
# MATCH STREAM
# ============================================================

match_query = (
    match_df

    .writeStream

    .foreachBatch(
        write_matches
    )

    .outputMode(
        "append"
    )

    .option(
        "checkpointLocation",
        CHECKPOINT + "/matches"
    )

    .trigger(
        processingTime="10 seconds"
    )

    .start()
)


# ============================================================
# STREAMING STATUS
# ============================================================

print()
print("=" * 70)
print("🟢 SPARK STREAMING IS RUNNING")
print("=" * 70)

print()
print(
    "MATCH    → PostgreSQL matches"
)

print(
    "DELIVERY → PostgreSQL ball_by_ball"
)

print()
print(
    "Kafka batch limit : 5,000 events"
)

print(
    "Trigger interval  : 10 seconds"
)

print(
    "Spark workers     : 2"
)

print()
print(
    "Waiting for Kafka events..."
)

print("=" * 70)


# ============================================================
# WAIT
# ============================================================

try:

    spark.streams.awaitAnyTermination()

except KeyboardInterrupt:

    print()
    print(
        "🛑 Stopping OverPulse streaming..."
    )

    delivery_query.stop()

    match_query.stop()

    spark.stop()

    print(
        "✅ Spark stopped cleanly."
    )