import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .mapping_engine import TerminologyTranslator
from .er_graph_generator import generate_er_knowledge_graph

app = FastAPI(
    title="Traditional Medicine EHR Interoperability Gateway",
    description="NFSU Healthcare API bridging NAMASTE and WHO ICD-11 TM2 standards",
    version="1.0.0"
)

translator = TerminologyTranslator()

class DrugCheckRequest(BaseModel):
    namaste_code: str
    concurrent_western_drugs: List[str]

class FHIRRequest(BaseModel):
    namaste_code: str
    patient_id: str = "PT-ANON-7782"

@app.get("/")
def root():
    return {
        "service": "Traditional Medicine EHR Interoperability Framework",
        "institution": "National Forensic Sciences University (Goa Campus)",
        "status": "OPERATIONAL",
        "supported_standards": ["WHO ICD-11 TM2", "HL7 FHIR R4", "AYUSH NAMASTE"]
    }

@app.get("/api/v1/terminology/search")
def search_term(q: str):
    result = translator.search_by_term(q)
    if not result:
        raise HTTPException(status_code=404, detail="Terminology not found in NAMASTE catalog")
    return {"query": q, "mapping": result}

@app.post("/api/v1/interactions/check")
def check_interaction(payload: DrugCheckRequest):
    alerts = translator.check_interaction(payload.namaste_code, payload.concurrent_western_drugs)
    return {
        "namaste_code": payload.namaste_code,
        "checked_drugs_count": len(payload.concurrent_western_drugs),
        "interaction_detected": len(alerts) > 0,
        "clinical_alerts": alerts
    }

@app.post("/api/v1/fhir/medication-statement")
def export_fhir(payload: FHIRRequest):
    item = translator.by_code.get(payload.namaste_code)
    if not item:
        raise HTTPException(status_code=404, detail="Invalid NAMASTE code")
    bundle = translator.export_fhir_medication_statement(item, payload.patient_id)
    return bundle

@app.get("/api/v1/graph/schema")
def get_er_graph():
    return generate_er_knowledge_graph(translator.data)