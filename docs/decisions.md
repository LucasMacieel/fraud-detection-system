# Data Loading

## Parquet and Caching

The raw CSV files are quite large (nearly 1.3GB combined). Parsing them in each iteration introduces a significant performance bottleneck in the load data process. To solve this, an automatic Parquet caching mechanism was implemented. When loading the dataset, the utility first checks if there is an existing Parquet file related to the original CSV. If it does not exist, it loads the train and test CSVs using the optimized Pyarrow engine, merges, and caches them as a single Parquet file, and loads that.

## The 'has_identity' Flag

Not all transactions in the dataset have a corresponding identity information. Fraudsters often attempt to perform transactions anonymously, making this missingness a valuable predictive signal. Because of that, a binary flag, 'has_identity', was computed and added as a feature. This flag was added before the left join of the datasets because computing this feature beforehand using 'isin()' is more efficient than performing null checks post-join.

## Left Join for Dataset Merge

A left join was performed on the transactions dataset on the *TransactionID* column. This was preferred to preserve all the transactions, regardless of whether they have a matching identity record. Doing an inner join would result in a massive training data loss, since a large portion of the transactions do not have an identity associated with it.
