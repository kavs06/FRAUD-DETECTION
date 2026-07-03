import pandas as pd
import os
from pathlib import Path
from typing import Tuple
from .config import Config

class DataLoader:
    def __init__(self, data_dir: str = str(Config.DATA_DIR)):
        self.data_dir = Path(data_dir)

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Loads the training datasets and returns them as dataframes.
        """
        print("Loading datasets...")
        
        # Locate files in the data directory by checking for naming patterns
        # Assuming the files are named like Train-1542865627584.csv
        train_file = self._find_file("Train-")
        beneficiary_file = self._find_file("Train_Beneficiarydata")
        inpatient_file = self._find_file("Train_Inpatientdata")
        outpatient_file = self._find_file("Train_Outpatientdata")

        if not all([train_file, beneficiary_file, inpatient_file, outpatient_file]):
            raise FileNotFoundError("Could not find one or more required CSV files in the data directory.")

        train_df = pd.read_csv(train_file)
        bene_df = pd.read_csv(beneficiary_file)
        inpatient_df = pd.read_csv(inpatient_file)
        outpatient_df = pd.read_csv(outpatient_file)
        
        # Fill missing values safely
        inpatient_df.fillna("None", inplace=True)
        outpatient_df.fillna("None", inplace=True)
        bene_df.fillna("Unknown", inplace=True)
        
        return train_df, bene_df, inpatient_df, outpatient_df

    def _find_file(self, prefix: str) -> Path:
        for file in self.data_dir.glob("*.csv"):
            if file.name.startswith(prefix):
                return file
        return None
