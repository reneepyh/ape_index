CREATE TABLE "time_dim" (
  "time_id" BIGINT IDENTITY(1,1) PRIMARY KEY,
  "datetime" TIMESTAMP UNIQUE NOT NULL
);

CREATE TABLE "addresses_dim" (
  "address_id" BIGINT IDENTITY(1,1) PRIMARY KEY,
  "address" VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE "marketplaces_dim" (
  "market_id" BIGINT IDENTITY(1,1) PRIMARY KEY,
  "marketplace_name" VARCHAR(25) UNIQUE NOT NULL
);

CREATE TABLE "actions_dim" (
  "action_id" BIGINT IDENTITY(1,1) PRIMARY KEY,
  "action_name" VARCHAR(25) UNIQUE NOT NULL
);

CREATE TABLE "transactions_fact" (
  "time_id" BIGINT NOT NULL,
  "buyer_id" BIGINT NOT NULL,
  "seller_id" BIGINT,
  "token_id" BIGINT NOT NULL,
  "market_id" BIGINT NOT NULL,
  "action_id" BIGINT NOT NULL,
  "price" DOUBLE PRECISION NOT NULL,
  "transaction_hash" VARCHAR(255) NOT NULL,

  PRIMARY KEY (time_id, buyer_id, token_id, market_id, action_id)
)
SORTKEY (time_id);

COMMENT ON COLUMN "transactions_fact"."price" IS 'Price must be non-negative';

ALTER TABLE "transactions_fact" ADD FOREIGN KEY ("time_id") REFERENCES "time_dim" ("time_id");

ALTER TABLE "transactions_fact" ADD FOREIGN KEY ("buyer_id") REFERENCES "addresses_dim" ("address_id");

ALTER TABLE "transactions_fact" ADD FOREIGN KEY ("seller_id") REFERENCES "addresses_dim" ("address_id");

ALTER TABLE "transactions_fact" ADD FOREIGN KEY ("market_id") REFERENCES "marketplaces_dim" ("market_id");

ALTER TABLE "transactions_fact" ADD FOREIGN KEY ("action_id") REFERENCES "actions_dim" ("action_id");
