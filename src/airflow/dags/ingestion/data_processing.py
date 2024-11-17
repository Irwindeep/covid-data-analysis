import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

class DataProcessor:
    def validate_data(self, df: pd.DataFrame, required_columns: list) -> pd.DataFrame:
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df.drop_duplicates(inplace=True)
        df = df.map(lambda x: None if pd.isna(x) else x)
        
        return df

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if "age" in df.columns:
            df["age"] = df["age"].astype(int)
        if "session_date" in df.columns:
            df["session_date"] = pd.to_datetime(df["session_date"])
        return df
