import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

def _get_merged_parquet_path(tx_path: Path) -> Path:
    """
    Determines the path for the merged parquet file.
    If 'raw' is in the directory path, it is mapped to 'processed'.
    The filename is derived as {prefix}_merged.parquet.
    """
    tx_name = tx_path.name.lower()
    if "train" in tx_name:
        prefix = "train"
    elif "test" in tx_name:
        prefix = "test"
    else:
        # Fallback to suffix-free name if no standard train/test pattern is found
        prefix = tx_path.stem.replace("_transaction", "")
        
    parent_parts = list(tx_path.parent.parts)
    if "raw" in parent_parts:
        idx = len(parent_parts) - 1 - parent_parts[::-1].index("raw")
        parent_parts[idx] = "processed"
        processed_dir = Path(*parent_parts)
    else:
        processed_dir = tx_path.parent
        
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir / f"{prefix}_merged.parquet"

def load_and_merge(transaction_path: str | Path, identity_path: str | Path) -> pd.DataFrame:
    """
    Loads transaction and identity datasets, adds a 'has_identity' flag, and
    merges them on TransactionID. Automatically caches the merged result as a 
    Parquet file (e.g., train_merged.parquet) under the processed directory
    and loads from this cache on subsequent runs.
    
    Parameters:
    -----------
    transaction_path : str or Path
        Path to the transaction CSV.
    identity_path : str or Path
        Path to the identity CSV.
        
    Returns:
    --------
    pd.DataFrame
        Merged dataset containing all transactions and their corresponding identity details.
    """
    tx_path = Path(transaction_path)
    id_path = Path(identity_path)
    
    parquet_path = _get_merged_parquet_path(tx_path)
    
    # Check if the fully merged parquet cache is already available
    if parquet_path.exists():
        logger.info(f"Loading cached merged parquet from: {parquet_path}")
        return pd.read_parquet(parquet_path)
        
    logger.info("Merged parquet cache not found. Reading raw CSVs...")
    
    if not tx_path.exists():
        raise FileNotFoundError(f"Transaction file not found at: {tx_path}")
    if not id_path.exists():
        raise FileNotFoundError(f"Identity file not found at: {id_path}")
        
    # Read the raw CSVs using high-performance pyarrow engine
    logger.info(f"Reading transaction CSV from: {tx_path}")
    tx_df = pd.read_csv(tx_path, engine="pyarrow")
    
    logger.info(f"Reading identity CSV from: {id_path}")
    id_df = pd.read_csv(id_path, engine="pyarrow")
    
    logger.info("Computing 'has_identity' flag before merging...")
    tx_df["has_identity"] = tx_df["TransactionID"].isin(id_df["TransactionID"]).astype(int)
    
    logger.info("Merging transaction and identity datasets on TransactionID...")
    merged_df = pd.merge(tx_df, id_df, on="TransactionID", how="left")
    
    logger.info(f"Caching merged dataset to parquet at: {parquet_path}")
    merged_df.to_parquet(parquet_path, index=False)
    
    logger.info(f"Merged shape: {merged_df.shape}")
    return merged_df
