import pandas as pd
from features.load_data import load_and_merge

def test_load_and_merge(tmp_path):
    # 1. Create mock transaction data
    tx_data = pd.DataFrame({
        "TransactionID": [1, 2, 3],
        "TransactionAmt": [10.5, 99.0, 5.0],
        "ProductCD": ["W", "H", "C"]
    })
    
    # 2. Create mock identity data (ID 1 and 2 exist, 3 does not)
    id_data = pd.DataFrame({
        "TransactionID": [1, 2],
        "DeviceType": ["mobile", "desktop"],
        "DeviceInfo": ["iPhone", "Windows"]
    })
    
    # Write mock data to temporary CSV files under a "raw" folder
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    tx_csv = raw_dir / "train_transaction.csv"
    id_csv = raw_dir / "train_identity.csv"
    
    tx_data.to_csv(tx_csv, index=False)
    id_data.to_csv(id_csv, index=False)
    
    # Corresponding expected merged parquet path under a "processed" folder
    processed_dir = tmp_path / "processed"
    merged_parquet = processed_dir / "train_merged.parquet"
    
    # Ensure parquet file does not exist initially
    assert not merged_parquet.exists()
    
    # 3. Call load_and_merge first time (should read CSV, cache to Parquet, and merge)
    merged_df = load_and_merge(tx_csv, id_csv)
    
    # Verify outputs
    assert len(merged_df) == 3
    assert "has_identity" in merged_df.columns
    # Check that has_identity is 1 for TransactionID 1 and 2, and 0 for 3
    assert merged_df.loc[merged_df["TransactionID"] == 1, "has_identity"].values[0] == 1
    assert merged_df.loc[merged_df["TransactionID"] == 2, "has_identity"].values[0] == 1
    assert merged_df.loc[merged_df["TransactionID"] == 3, "has_identity"].values[0] == 0
    
    # Check that left join worked (DeviceType is NaN for TransactionID 3)
    assert merged_df.loc[merged_df["TransactionID"] == 1, "DeviceType"].values[0] == "mobile"
    assert pd.isna(merged_df.loc[merged_df["TransactionID"] == 3, "DeviceType"].values[0])
    
    # Verify that merged parquet file was created
    assert merged_parquet.exists()
    
    # Modify the CSV file slightly to prove that next load will read from cached Parquet (ignoring CSV changes)
    tx_data_modified = pd.DataFrame({
        "TransactionID": [1, 2, 3],
        "TransactionAmt": [9999.9, 99.0, 5.0],
        "ProductCD": ["W", "H", "C"]
    })
    tx_data_modified.to_csv(tx_csv, index=False)
    
    # 4. Call load_and_merge second time
    merged_df_2 = load_and_merge(tx_csv, id_csv)
    
    # It should load cached Parquet, so TransactionAmt for ID 1 should be 10.5, NOT the modified 9999.9
    assert merged_df_2.loc[merged_df_2["TransactionID"] == 1, "TransactionAmt"].values[0] == 10.5
