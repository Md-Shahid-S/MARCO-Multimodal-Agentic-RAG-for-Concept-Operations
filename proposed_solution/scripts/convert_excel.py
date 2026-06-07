import pandas as pd
import json
import os

excel_path = 'marco/data/base/azizikhadem-devops-msa-mapping-rag-a973c6b/devopsmsa.xlsx'
output_path = 'marco/data/base/concept_pairs.json'

os.makedirs(os.path.dirname(output_path), exist_ok=True)

df = pd.read_excel(excel_path)
# Rename columns to match plan's expectation if necessary
# Plan uses: devops_concept, msa_concept, definition, taxonomy_category, evidence_type
# Excel has: reference_name, devops_concept, microservice_architecture_concept

df = df.rename(columns={
    'microservice_architecture_concept': 'msa_concept'
})

# Add missing fields as empty if not present to avoid KeyError in builder
if 'definition' not in df.columns:
    df['definition'] = ""
if 'taxonomy_category' not in df.columns:
    df['taxonomy_category'] = "Deployment Automation" # Default

concepts = df.to_dict('records')

with open(output_path, 'w') as f:
    json.dump(concepts, f, indent=2)

print(f"Successfully converted {len(concepts)} pairs to {output_path}")
