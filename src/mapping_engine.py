"""
Traditional Medicine EHR Integration Framework
Semantic Translation Engine: NAMASTE <-> WHO ICD-11 TM2 <-> HL7 FHIR R4
Author: Kolawada Rakshit (NFSU Goa)
"""

import json
from typing import List, Dict, Optional
from pydantic import BaseModel

class MedicationMapping(BaseModel):
    namaste_code: str
    sanskrit_name: str
    botanical_name: str
    icd11_tm2_code: str
    icd11_title: str
    active_compounds: List[str]
    indications: List[str]

class TerminologyTranslator:
    def __init__(self, data_path: str = "data/sample_namaste_mappings.json"):
        with open(data_path) as f:
            self.data = json.load(f)["formulations"]
            self.by_code = {item["namaste_code"]: item for item in self.data}
            self.by_name = {item["sanskrit_name"].lower(): item for item in self.data}

    def search_by_term(self, query: str) -> Optional[Dict]:
        q = query.strip().lower()
        if q in self.by_name:
            return self.by_name[q]
        for item in self.data:
            if q in item["botanical_name"].lower() or q in item["namaste_code"].lower():
                return item
        return None

    def export_fhir_medication_statement(self, item: Dict, patient_id: str) -> Dict:
        """
        Synthesizes an HL7 FHIR R4 MedicationStatement resource with ICD-11 TM2 coding
        """
        return {
            "resourceType": "MedicationStatement",
            "id": f"tm-med-{item['namaste_code'].lower()}",
            "status": "active",
            "subject": {"reference": f"Patient/{patient_id}"},
            "medicationCodeableConcept": {
                "coding": [
                    {
                        "system": "http://ayush.gov.in/namaste",
                        "code": item["namaste_code"],
                        "display": f"{item['sanskrit_name']} ({item['botanical_name']})"
                    },
                    {
                        "system": "http://id.who.int/icd11/mms",
                        "code": item["icd11_tm2_code"],
                        "display": item["icd11_title"]
                    }
                ],
                "text": item["sanskrit_name"]
            },
            "reasonCode": [
                {
                    "coding": [
                        {
                            "system": "http://id.who.int/icd11/mms",
                            "code": item["icd11_tm2_code"],
                            "display": item["icd11_title"]
                        }
                    ],
                    "text": ", ".join(item["indications"])
                }
            ]
        }

    def check_interaction(self, namaste_code: str, western_drugs: List[str]) -> List[Dict]:
        """
        Scans for adverse drug-herb interactions against concurrent pharmaceutical prescriptions
        """
        item = self.by_code.get(namaste_code)
        if not item or not item.get("contraindicated_drugs"):
            return []

        alerts = []
        for contraindicated in item["contraindicated_drugs"]:
            for drug in western_drugs:
                if contraindicated["generic_name"].lower() in drug.lower():
                    alerts.append({
                        "herb": item["sanskrit_name"],
                        "western_drug": contraindicated["generic_name"],
                        "severity": contraindicated["severity"],
                        "clinical_warning": contraindicated["warning"]
                    })
        return alerts