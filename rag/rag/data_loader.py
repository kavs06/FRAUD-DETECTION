"""
Load Medicare datasets for the Healthcare Fraud Detection project.
"""

from pathlib import Path
import pandas as pd

from config import DATA_DIR
from utils.logger import setup_logger

logger = setup_logger()


class DataLoader:
    """
    Loads all Medicare datasets from the data folder.
    """

    def __init__(self):
        self.data_path = DATA_DIR

    def load_csv(self, filename):
        """
        Load a single CSV file.
        """

        file_path = self.data_path / filename

        if not file_path.exists():
            logger.error(f"{filename} not found.")
            raise FileNotFoundError(file_path)

        logger.info(f"Loading {filename}")

        df = pd.read_csv(file_path)

        logger.info(
            f"{filename} loaded successfully "
            f"({df.shape[0]} rows, {df.shape[1]} columns)"
        )

        return df

    def load_all(self):
        """
        Load all project datasets.
        """

        datasets = {
            "train": self.load_csv("Train.csv"),
            "train_beneficiary": self.load_csv("Train_Beneficiarydata.csv"),
            "train_inpatient": self.load_csv("Train_Inpatientdata.csv"),
            "train_outpatient": self.load_csv("Train_Outpatientdata.csv"),
            "test": self.load_csv("Test.csv"),
            "test_beneficiary": self.load_csv("Test_Beneficiarydata.csv"),
            "test_inpatient": self.load_csv("Test_Inpatientdata.csv"),
            "test_outpatient": self.load_csv("Test_Outpatientdata.csv"),
        }

        logger.info("All datasets loaded successfully.")

        return datasets


if __name__ == "__main__":

    loader = DataLoader()

    datasets = loader.load_all()

    print("\nLoaded Datasets\n")

    for name, df in datasets.items():
        print(f"{name:<20} {df.shape}")