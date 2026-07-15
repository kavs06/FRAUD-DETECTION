from rag.data_loader import DataLoader

loader = DataLoader()
datasets = loader.load_all()

print(datasets["train"].columns.tolist())
print(datasets["train_beneficiary"].columns.tolist())
print(datasets["train_inpatient"].columns.tolist())
print(datasets["train_outpatient"].columns.tolist())