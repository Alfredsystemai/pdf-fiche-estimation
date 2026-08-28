"""
app.py — Service de génération PDF pour fiches d'estimation immobilière
La Petite Agence

Déployer sur Railway comme service distinct de n8n.
POST /generate  → JSON → PDF (application/pdf)
GET  /health    → {"status": "ok"}
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Any
from pdf_fiche import generate_pdf

app = FastAPI(title="PDF Fiche Estimation", version="1.0")

SECRET = os.environ.get("PDF_SECRET", "")


class SurfacePiece(BaseModel):
    nom: str
    surface: str = ""


class Surfaces(BaseModel):
    entree: str = ""
    sejour_salon: str = ""
    salle_a_manger: str = ""
    cuisine: str = ""
    chambres: str = ""
    salle_de_bains: str = ""
    salle_d_eau: str = ""
    wc_independants: str = ""
    wc_partages: str = ""
    couloir: str = ""
    placards: str = ""
    autres: List[Any] = []
    notes: str = ""
    surface_habitable: str = ""


class Vendeur(BaseModel):
    civilite: str = ""
    nom: str = ""
    prenom: str = ""
    adresse: str = ""
    telephone: str = ""
    email: str = ""
    notaire: str = ""
    situation_maritale: str = ""


class Caracteristiques(BaseModel):
    # Commun
    raison_estimation: str = ""
    type_bien_detail: str = ""   # T2, T3, F4...
    annee_achat: str = ""
    notaire_achat: str = ""
    prix_achat: str = ""
    reste_a_financer: str = ""
    dpe: str = ""
    ges: str = ""
    dpe_date: str = ""
    diagnostics: List[str] = []
    autre_diagnostic: str = ""
    vis_a_vis: str = ""
    # Appartement
    date_construction_immeuble: str = ""
    syndic: str = ""
    charges_copro: str = ""
    charges_comprenant: str = ""
    taxe_fonciere: str = ""
    chauffage: str = ""
    chauffage_type: str = ""
    ascenseur: Optional[bool] = None
    etage: str = ""
    exposition: str = ""
    huisseries: str = ""
    agrements: List[str] = []
    reglement_copro: str = ""
    # Maison
    date_construction: str = ""
    constructeur: str = ""
    assainissement: str = ""
    assainissement_conforme: Optional[bool] = None
    chauffage_budget: str = ""
    terrain_m2: str = ""
    annexes: List[str] = []
    autres_annexes: str = ""
    mitoyennete: str = ""
    fondations: str = ""
    servitudes: str = ""


class FicheRequest(BaseModel):
    secret: str = ""
    type: str = "appartement"
    date: str = ""
    adresse: str = ""
    vendeur1: Optional[Vendeur] = None
    vendeur2: Optional[Vendeur] = None
    caracteristiques: Optional[Caracteristiques] = None
    surfaces: Optional[Surfaces] = None
    travaux: str = ""
    prix_estimation: str = ""
    estimation: dict = {}
    prix_vendeur: str = ""
    delai_vente: str = ""
    situation_occupante: str = ""
    observations: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
def generate(req: FicheRequest):
    if SECRET and req.secret != SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = req.model_dump()
    try:
        pdf_bytes = generate_pdf(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    adresse_slug = "".join(c if c.isalnum() else "_" for c in (req.adresse or "fiche"))[:40]
    filename = f"fiche_estimation_{adresse_slug}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
