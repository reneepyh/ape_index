import argparse
import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, regexp_extract, regexp_replace, when, lag
from pyspark.sql.window import Window

parser = argparse.ArgumentParser()
parser.add_argument("--user")
parser.add_argument("--password")
parser.add_argument("--redshifturl")
parser.add_argument("--tempdir")
parser.add_argument("--s3rawdata")
args = parser.parse_args()

spark = SparkSession.builder.appName("ape-index").getOrCreate()
spark.sparkContext.setLogLevel("DEBUG")

REDSHIFT_URL = args.redshifturl
TEMP_S3_PATH = args.tempdir
USER = args.user
PASSWORD = args.password
s3_rawdata_folder = args.s3rawdata

def log_stage(stage):
    print(f"🔄 Executing stage: {stage}")

def load_csv_from_s3(path):
    log_stage("Loading CSV from S3")
    return spark.read.csv(path, header=True, inferSchema=True)

def transform_data(df):
    log_stage("Transforming data")
    df = df.withColumn("datetime", to_timestamp(col("DateTime (UTC)")))
    df = df.select(
        col("Transaction Hash").alias("transaction_hash"),
        col("datetime"),
        col("Price").alias("raw_price"),
        col("Market").alias("marketplace_name"),
        col("Buyer").alias("buyer_address"),
        col("Token ID").alias("token_id"),
        col("Action").alias("action_name")
    ).dropna()
    
    df = df.filter(~col("raw_price").rlike("0 ETH|0 WETH|EDC"))
    df = df.withColumn(
        "price",
        when(col("raw_price").contains("($") & col("raw_price").contains("$"),
             regexp_replace(regexp_extract(col("raw_price"), r"\(\$([\d,]+\.\d+)\)", 1), ",", "")
        ).when(col("raw_price").rlike("USDC|USD"),
             regexp_replace(regexp_extract(col("raw_price"), r"([\d,]+\.\d+)", 1), ",", "")
        ).otherwise(None).cast("double")
    ).drop("raw_price").filter(col("price").isNotNull())
    
    return df

def compute_sellers(df, historical_df):
    log_stage("Computing sellers")
    token_ids_df = df.select("token_id").distinct()
    matching_df = historical_df.join(token_ids_df, "token_id", "inner")
    combined_df = df.select("token_id", "datetime", "buyer_address").unionByName(matching_df).dropDuplicates()
    window_spec = Window.partitionBy("token_id").orderBy("datetime")
    return combined_df.withColumn("seller_address", lag("buyer_address").over(window_spec))

def load_redshift_table(table_name):
    log_stage(f"Loading Redshift table: {table_name}")
    return spark.read.format("io.github.spark_redshift_community.spark.redshift") \
        .option("url", REDSHIFT_URL).option("dbtable", table_name) \
        .option("tempdir", TEMP_S3_PATH).option("user", USER).option("password", PASSWORD) \
        .option("forward_spark_s3_credentials", "true").load()

def append_to_redshift(df, table_name):
    log_stage(f"Appending data to Redshift table: {table_name}")
    df.write.format("io.github.spark_redshift_community.spark.redshift") \
        .option("url", REDSHIFT_URL).option("dbtable", table_name) \
        .option("tempdir", TEMP_S3_PATH).option("user", USER).option("password", PASSWORD) \
        .option("forward_spark_s3_credentials", "true").mode("append").save()

### ETL
try:
    today_str = datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
    raw_path = f"{s3_rawdata_folder}transactions_{today_str}_*.csv"
    raw_df = load_csv_from_s3(raw_path)
    if raw_df.rdd.isEmpty():
        print("No new transaction file found for today. Exiting ETL.")
        sys.exit(0)

    transformed_df = transform_data(raw_df)
    historical_df = load_csv_from_s3(s3_rawdata_folder + "*.csv").select("Token ID", "DateTime (UTC)", "Buyer").withColumnRenamed("Token ID", "token_id").withColumnRenamed("Buyer", "buyer_address").withColumn("datetime", to_timestamp(col("DateTime (UTC)"))).drop("DateTime (UTC)")
    seller_df = compute_sellers(transformed_df, historical_df)
    df = transformed_df.join(seller_df.select("token_id", "datetime", "seller_address"), ["token_id", "datetime"], "left")
    
    # Load Redshift dimension tables
    marketplace_dim = load_redshift_table("marketplaces_dim")
    action_dim = load_redshift_table("actions_dim")
    address_dim = load_redshift_table("addresses_dim")
    time_dim = load_redshift_table("time_dim")
    
    # Insert new dim records
    new_marketplaces = df.select("marketplace_name").distinct().join(marketplace_dim, "marketplace_name", "left_anti")
    new_actions = df.select("action_name").distinct().join(action_dim, "action_name", "left_anti")
    new_addresses = df.select(col("buyer_address").alias("address")).union(df.select(col("seller_address").alias("address")).filter(col("seller_address").isNotNull())).distinct().join(address_dim, "address", "left_anti")
    new_times = df.select("datetime").distinct().join(time_dim, "datetime", "left_anti")

    append_to_redshift(new_marketplaces, "marketplaces_dim")
    append_to_redshift(new_actions, "actions_dim")
    append_to_redshift(new_addresses, "addresses_dim")
    append_to_redshift(new_times, "time_dim")

    # Reload Updated Dimension Tables
    dim_tables = ["time_dim", "marketplaces_dim", "actions_dim", "addresses_dim"]
    dim_dfs = {table: load_redshift_table(table) for table in dim_tables}

    # Insert into transactions_fact
    fact_df = df.join(dim_dfs["time_dim"], "datetime", "left") \
                .join(dim_dfs["marketplaces_dim"], "marketplace_name", "left") \
                .join(dim_dfs["actions_dim"], "action_name", "left") \
                .join(dim_dfs["addresses_dim"].withColumnRenamed("address", "buyer_address_lookup")
                                          .withColumnRenamed("address_id", "buyer_id"),
                    df.buyer_address == col("buyer_address_lookup"), "left") \
                        .join(dim_dfs["addresses_dim"].withColumnRenamed("address", "seller_address_lookup")
                                          .withColumnRenamed("address_id", "seller_id"),
                    df.seller_address == col("seller_address_lookup"), "left")
    
    fact_df = fact_df.withColumn("time_id", col("time_id").cast("bigint"))
    fact_df = fact_df.withColumn("buyer_id", col("buyer_id").cast("bigint"))
    fact_df = fact_df.withColumn("seller_id", col("seller_id").cast("bigint"))
    fact_df = fact_df.withColumn("market_id", col("market_id").cast("bigint"))
    fact_df = fact_df.withColumn("action_id", col("action_id").cast("bigint"))
    
    ###debugging
    fact_df.printSchema()
    fact_df.show(10, truncate=False)
 
    append_to_redshift(fact_df, "transactions_fact")
    
    print("✅ ETL Process Completed Successfully.")
except Exception as e:
    print(f"❌ ETL process failed: {e}")
    exit(1)
finally:
    spark.stop()