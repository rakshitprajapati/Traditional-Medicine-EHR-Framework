"""
Entity-Relationship (ER) Graph Synthesizer
Generates schema node/edge relationships between herbs, phytochemicals, and ICD-11 entities.
"""

from typing import List, Dict

def generate_er_knowledge_graph(formulations: List[Dict]) -> Dict:
    nodes = []
    edges = []

    for item in formulations:
        herb_id = f"herb_{item['namaste_code']}"
        nodes.append({
            "id": herb_id,
            "label": item["sanskrit_name"],
            "type": "NAMASTE_HERB",
            "botanical": item["botanical_name"]
        })

        icd_id = f"icd_{item['icd11_tm2_code']}"
        nodes.append({
            "id": icd_id,
            "label": item["icd11_title"],
            "type": "ICD11_TM2_DIAGNOSIS"
        })

        edges.append({
            "source": herb_id,
            "target": icd_id,
            "relationship": "MAPS_TO_DIAGNOSIS"
        })

        for compound in item.get("active_compounds", []):
            comp_id = f"comp_{compound.replace(' ', '_')}"
            nodes.append({
                "id": comp_id,
                "label": compound,
                "type": "PHYTOCHEMICAL_COMPOUND"
            })
            edges.append({
                "source": herb_id,
                "target": comp_id,
                "relationship": "CONTAINS_ACTIVE_COMPOUND"
            })

    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "nodes": nodes,
        "edges": edges
    }