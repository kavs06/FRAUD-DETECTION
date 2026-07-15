"""
Document Builder

Converts Medicare datasets into human-readable investigation reports
for Retrieval-Augmented Generation (RAG).
"""

from pathlib import Path
from collections import Counter

import pandas as pd
from langchain_core.documents import Document

from config import DATA_DIR
from rag.data_loader import DataLoader
from utils.logger import setup_logger

logger = setup_logger()


class DocumentBuilder:
    """
    Builds investigation documents from Medicare datasets.
    """

    def __init__(self):

        self.loader = DataLoader()

        self.documents = []

        self.provider_statistics = {}

        self.output_dir = Path(DATA_DIR).parent / "documents"

        self.output_dir.mkdir(exist_ok=True)

    def load_data(self):
        """
        Load all datasets.
        """

        logger.info("Loading datasets...")

        self.datasets = self.loader.load_all()

        logger.info("Datasets loaded successfully.")

    def prepare_claims(self):
        """
        Combine inpatient and outpatient claims into a single dataframe.
        """

        logger.info("Preparing claim dataset...")

        inpatient = self.datasets["train_inpatient"].copy()
        outpatient = self.datasets["train_outpatient"].copy()

        inpatient["ClaimType"] = "Inpatient"
        outpatient["ClaimType"] = "Outpatient"

        self.claims = pd.concat(
            [inpatient, outpatient],
            ignore_index=True
        )

        logger.info(f"Combined claims: {len(self.claims)}")

    def merge_provider_labels(self):
        """
        Merge provider fraud labels into the claims dataframe.
        """

        logger.info("Merging provider fraud labels...")

        fraud_labels = self.datasets["train"]

        self.claims = self.claims.merge(
            fraud_labels,
            on="Provider",
            how="left"
        )

        logger.info("Fraud labels merged successfully.")

    def calculate_provider_statistics(self):
        """
        Calculate statistics for every provider.
        """

        logger.info("Calculating provider statistics...")

        self.provider_statistics = {}

        grouped = self.claims.groupby("Provider")

        for provider_id, group in grouped:

            fraud_label = group["PotentialFraud"].iloc[0]

            total_claims = len(group)

            inpatient_claims = (
                group["ClaimType"] == "Inpatient"
            ).sum()

            outpatient_claims = (
                group["ClaimType"] == "Outpatient"
            ).sum()

            unique_beneficiaries = group["BeneID"].nunique()

            total_reimbursement = (
                group["InscClaimAmtReimbursed"].sum()
            )

            average_reimbursement = (
                group["InscClaimAmtReimbursed"].mean()
            )

            diagnosis_columns = [
                col
                for col in group.columns
                if col.startswith("ClmDiagnosisCode_")
            ]

            diagnosis_codes = []

            for col in diagnosis_columns:
                diagnosis_codes.extend(
                    group[col]
                    .dropna()
                    .astype(str)
                    .tolist()
                )

            top_diagnosis = [
                code
                for code, _ in Counter(
                    diagnosis_codes
                ).most_common(5)
            ]

            procedure_columns = [
                col
                for col in group.columns
                if col.startswith("ClmProcedureCode_")
            ]

            procedure_codes = []

            for col in procedure_columns:
                procedure_codes.extend(
                    group[col]
                    .dropna()
                    .astype(str)
                    .tolist()
                )

            top_procedures = [
                code
                for code, _ in Counter(
                    procedure_codes
                ).most_common(5)
            ]

            self.provider_statistics[provider_id] = {

                "fraud_label": fraud_label,

                "total_claims": int(total_claims),

                "inpatient_claims": int(inpatient_claims),

                "outpatient_claims": int(outpatient_claims),

                "unique_beneficiaries": int(
                    unique_beneficiaries
                ),

                "total_reimbursement": float(
                    total_reimbursement
                ),

                "average_reimbursement": float(
                    average_reimbursement
                ),

                "top_diagnosis_codes": top_diagnosis,

                "top_procedure_codes": top_procedures,
            }

        logger.info(
            f"Statistics calculated for "
            f"{len(self.provider_statistics)} providers."
        )

    def build_provider_documents(self):
        """
        Generate investigation reports for every provider and
        convert them into LangChain Documents.
        """

        logger.info("Generating Provider Investigation Reports...")

        self.documents = []

        for provider_id, stats in self.provider_statistics.items():

            # -----------------------------
            # Risk Level
            # -----------------------------

            if stats["fraud_label"] == "Yes":
                risk_level = "High"
            elif stats["average_reimbursement"] > 10000:
                risk_level = "Medium"
            else:
                risk_level = "Low"

            # -----------------------------
            # Risk Factors
            # -----------------------------

            risk_factors = []

            if stats["fraud_label"] == "Yes":
                risk_factors.append("Provider labelled as fraudulent.")

            if stats["average_reimbursement"] > 10000:
                risk_factors.append("High average reimbursement.")

            if stats["total_claims"] > 100:
                risk_factors.append("Large number of submitted claims.")

            if len(stats["top_diagnosis_codes"]) >= 5:
                risk_factors.append("Repeated diagnosis patterns observed.")

            if len(risk_factors) == 0:
                risk_factors.append("No major fraud indicators detected.")

            # -----------------------------
            # Recommendation
            # -----------------------------

            if risk_level == "High":
                recommendation = (
                    "Immediate detailed fraud investigation recommended."
                )

            elif risk_level == "Medium":
                recommendation = (
                    "Monitor provider and perform targeted audit."
                )

            else:
                recommendation = (
                    "Routine monitoring recommended."
                )

            # -----------------------------
            # Report
            # -----------------------------

            report = f"""
==========================================
HEALTHCARE PROVIDER INVESTIGATION REPORT
==========================================

Provider ID:
{provider_id}

Fraud Label:
{stats['fraud_label']}

Risk Level:
{risk_level}

Total Claims:
{stats['total_claims']}

Inpatient Claims:
{stats['inpatient_claims']}

Outpatient Claims:
{stats['outpatient_claims']}

Unique Beneficiaries:
{stats['unique_beneficiaries']}

Total Reimbursement:
${stats['total_reimbursement']:.2f}

Average Reimbursement:
${stats['average_reimbursement']:.2f}

Top Diagnosis Codes:
{", ".join(stats['top_diagnosis_codes'])}

Top Procedure Codes:
{", ".join(stats['top_procedure_codes'])}

Risk Factors:
{chr(10).join("- " + x for x in risk_factors)}

Recommendation:
{recommendation}

Source:
Project Dataset
"""

            # -----------------------------
            # Save LangChain Document
            # -----------------------------

            document = Document(
                page_content=report,
                metadata={
                    "provider_id": provider_id,
                    "fraud_label": stats["fraud_label"],
                    "risk_level": risk_level,
                    "document_type": "provider_report",
                    "source": "project_dataset"
                }
            )

            self.documents.append(document)

        logger.info(
            f"Generated {len(self.documents)} Provider Investigation Reports."
        )

    def save_documents(self):
        """
        Save generated reports.

        (Implementation in next step.)
        """

        pass

    def get_documents(self):
        """
        Return LangChain Documents.
        """

        return self.documents


if __name__ == "__main__":

    builder = DocumentBuilder()

    builder.load_data()

    builder.prepare_claims()

    builder.merge_provider_labels()

    builder.calculate_provider_statistics()

    builder.build_provider_documents()

    print("\nTotal Providers :", len(builder.provider_statistics))

    print("Documents Generated :", len(builder.documents))

    print("\nSample Investigation Report\n")

    print(builder.documents[0].page_content)

    print("\nMetadata\n")

    print(builder.documents[0].metadata)
