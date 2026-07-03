import pandas as pd
from typing import Dict, List

class DocumentBuilder:
    def __init__(self, train_df: pd.DataFrame, bene_df: pd.DataFrame, inpatient_df: pd.DataFrame, outpatient_df: pd.DataFrame):
        self.train_df = train_df
        self.bene_df = bene_df
        self.inpatient_df = inpatient_df
        self.outpatient_df = outpatient_df

    def build_documents(self) -> List[Dict]:
        """
        Aggregates data by provider and creates a textual summary document for each.
        Returns a list of dictionaries with 'Provider' and 'Document' keys.
        """
        print("Building provider documents...")
        
        # Combine claims to aggregate features by Provider
        self.inpatient_df['ClaimType'] = 'Inpatient'
        self.outpatient_df['ClaimType'] = 'Outpatient'
        
        # Keep relevant columns to merge
        cols_to_keep = ['Provider', 'BeneID', 'ClaimID', 'InscClaimAmtReimbursed', 'ClmDiagnosisCode_1', 'ClmProcedureCode_1', 'ClaimType']
        
        inpatient_subset = self.inpatient_df[cols_to_keep] if set(cols_to_keep).issubset(self.inpatient_df.columns) else self.inpatient_df
        outpatient_subset = self.outpatient_df[cols_to_keep] if set(cols_to_keep).issubset(self.outpatient_df.columns) else self.outpatient_df
        
        all_claims = pd.concat([inpatient_subset, outpatient_subset], ignore_index=True)
        
        # Merge with Beneficiary details
        if 'BeneID' in all_claims.columns and 'BeneID' in self.bene_df.columns:
            all_claims = all_claims.merge(self.bene_df, on='BeneID', how='left')
        
        # Group by Provider
        documents = []
        
        provider_groups = all_claims.groupby('Provider')
        
        for provider_id, group in provider_groups:
            # Basic stats
            total_claims = len(group)
            unique_beneficiaries = group['BeneID'].nunique() if 'BeneID' in group.columns else 0
            
            reimbursement_col = 'InscClaimAmtReimbursed'
            avg_reimbursement = group[reimbursement_col].mean() if reimbursement_col in group.columns else 0
            max_reimbursement = group[reimbursement_col].max() if reimbursement_col in group.columns else 0
            
            # Diagnosis codes (Top 5)
            diag_col = 'ClmDiagnosisCode_1'
            if diag_col in group.columns:
                top_diagnosis = group[diag_col].value_counts().head(5).index.tolist()
                top_diagnosis = [str(x) for x in top_diagnosis if x != "None"]
            else:
                top_diagnosis = []
                
            # Procedure codes (Top 5)
            proc_col = 'ClmProcedureCode_1'
            if proc_col in group.columns:
                top_procedures = group[proc_col].value_counts().head(5).index.tolist()
                top_procedures = [str(x) for x in top_procedures if x != "None"]
            else:
                top_procedures = []
                
            # Fraud Label
            fraud_label = "Unknown"
            if 'Provider' in self.train_df.columns and 'PotentialFraud' in self.train_df.columns:
                label_row = self.train_df[self.train_df['Provider'] == provider_id]
                if not label_row.empty:
                    fraud_label = label_row.iloc[0]['PotentialFraud']

            # Build readable text document
            doc_text = f"Provider ID: {provider_id}\n"
            doc_text += f"Fraud Label: {'Yes' if fraud_label == 'Yes' else ('No' if fraud_label == 'No' else 'Unknown')}\n"
            doc_text += f"Total Claims: {total_claims}\n"
            doc_text += f"Number of Beneficiaries: {unique_beneficiaries}\n"
            doc_text += f"Average Reimbursement: ${avg_reimbursement:,.2f}\n"
            doc_text += f"Maximum Reimbursement: ${max_reimbursement:,.2f}\n"
            doc_text += f"Top Diagnosis Codes: {', '.join(top_diagnosis) if top_diagnosis else 'None recorded'}\n"
            doc_text += f"Top Procedure Codes: {', '.join(top_procedures) if top_procedures else 'None recorded'}\n"
            
            # Additional Context
            inpatient_count = len(group[group.get('ClaimType') == 'Inpatient'])
            outpatient_count = len(group[group.get('ClaimType') == 'Outpatient'])
            doc_text += f"Inpatient Claims: {inpatient_count}\n"
            doc_text += f"Outpatient Claims: {outpatient_count}\n"
            
            documents.append({
                "provider_id": provider_id,
                "text": doc_text
            })
            
        return documents
