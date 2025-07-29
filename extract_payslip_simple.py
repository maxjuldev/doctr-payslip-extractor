#!/usr/bin/env python3
"""
Script simple pour tester l'extraction OCR avec docTR
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

from doctr.models import ocr_predictor
from doctr.io import DocumentFile


def extract_text_from_pdf_simple(pdf_path: str) -> str:
    """Version simplifiée pour extraire juste le texte"""
    print(f"📄 Chargement du PDF: {pdf_path}")
    
    try:
        # Utiliser un modèle plus léger
        print("🔍 Chargement du modèle OCR...")
        model = ocr_predictor(pretrained=True)  # Utilise les modèles par défaut
        
        # Charger le document
        print("📖 Lecture du document...")
        doc = DocumentFile.from_pdf(pdf_path)
        
        # Effectuer l'OCR
        print("🔍 Extraction du texte...")
        result = model(doc)
        
        # Extraire le texte
        full_text = ""
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = ""
                    for word in line.words:
                        line_text += word.value + " "
                    full_text += line_text.strip() + "\n"
        
        return full_text
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return ""


def parse_payslip_simple(text: str) -> Dict[str, Any]:
    """Parser simple pour extraire les données du bulletin"""
    print("📊 Analyse du texte extrait...")
    
    # Données extraites
    data = {
        'employee_info': {},
        'pay_info': {},
        'amounts': {},
        'raw_text': text
    }
    
    # Rechercher les informations communes dans les bulletins français
    patterns = {
        'nom': r'(?:nom|salarié)[:\s]*([A-Z\s]+)',
        'prenom': r'(?:prénom)[:\s]*([A-Z\s]+)',
        'matricule': r'(?:matricule|n°)[:\s]*(\d+)',
        'periode': r'(?:période|mois)[:\s]*([0-9/]+)',
        'salaire_brut': r'(?:salaire brut|brut)[:\s]*([0-9,]+\.?\d*)',
        'net_payer': r'(?:net à payer|net)[:\s]*([0-9,]+\.?\d*)',
        'cotisations': r'(?:cotisations)[:\s]*([0-9,]+\.?\d*)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if key in ['nom', 'prenom', 'matricule']:
                data['employee_info'][key] = match.group(1).strip()
            elif key == 'periode':
                data['pay_info'][key] = match.group(1).strip()
            else:
                data['amounts'][key] = match.group(1).strip()
    
    return data


def main():
    """Fonction principale"""
    pdf_path = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF"
    
    if not Path(pdf_path).exists():
        print(f"❌ Fichier non trouvé: {pdf_path}")
        return
    
    print("🚀 Démarrage de l'extraction OCR...")
    
    # Extraire le texte
    text = extract_text_from_pdf_simple(pdf_path)
    
    if text:
        print("✅ Texte extrait avec succès!")
        print("\n" + "="*50)
        print("📝 TEXTE BRUT EXTRAIT:")
        print("="*50)
        print(text[:1000] + "..." if len(text) > 1000 else text)
        
        # Parser les données
        parsed_data = parse_payslip_simple(text)
        
        print("\n" + "="*50)
        print("📋 DONNÉES PARSÉES:")
        print("="*50)
        
        print("\n👤 Informations employé:")
        for key, value in parsed_data['employee_info'].items():
            print(f"  {key}: {value}")
        
        print("\n📅 Informations période:")
        for key, value in parsed_data['pay_info'].items():
            print(f"  {key}: {value}")
        
        print("\n💰 Montants:")
        for key, value in parsed_data['amounts'].items():
            print(f"  {key}: {value}")
        
        # Sauvegarder les résultats
        with open("bulletin_analyse.json", "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        
        print("\n💾 Résultats sauvegardés dans: bulletin_analyse.json")
    
    else:
        print("❌ Impossible d'extraire le texte")


if __name__ == "__main__":
    main()
