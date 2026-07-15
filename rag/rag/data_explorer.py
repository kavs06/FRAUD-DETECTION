"""
Explore Medicare datasets.

Prints column names, shapes, and sample records
to help design the Provider Investigation Report.
"""

from rag.data_loader import DataLoader


def explore():
    loader = DataLoader()
    datasets = loader.load_all()

    for name, df in datasets.items():
        print("\n" + "=" * 80)
        print(f"Dataset : {name}")
        print("=" * 80)

        print("\nShape:")
        print(df.shape)

        print("\nColumns:")
        for col in df.columns:
            print(f" - {col}")

        print("\nFirst 5 Rows:")
        print(df.head())


if __name__ == "__main__":
    explore()