#!/usr/bin/env python3
"""
Script pour extraire les données structurées des bulletins de salaire avec docTR
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

from doctr.models import ocr_predictor
from doctr.io import DocumentFile


class PayslipExtractor:
    """Extracteur de données pour bulletins de salaire"""
    
    def __init__(self):
        # Charger le modèle OCR pré-entraîné
        self.model = ocr_predictor(
            det_arch='db_resnet50', 
            reco_arch='crnn_vgg16_bn', 
            pretrained=True
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extraire le texte brut du PDF"""
        # Charger le document
        doc = DocumentFile.from_pdf(pdf_path)
        
        # Effectuer l'OCR
        result = self.model(doc)
        
        # Extraire le texte et les coordonnées
        extracted_data = {
            'pages': [],
            'raw_text': ''
        }
        
        for page_idx, page in enumerate(result.pages):
            page_text = ""
            words_data = []
            
            for block in page.blocks:
                for line in block.lines:
                    line_text = ""
                    for word in line.words:
                        word_text = word.value
                        word_confidence = word.confidence
                        word_geometry = word.geometry
                        
                        words_data.append({
                            'text': word_text,
                            'confidence': word_confidence,
                            'geometry': word_geometry
                        })
                        
                        line_text += word_text + " "
                    page_text += line_text.strip() + "\n"
            
            extracted_data['pages'].append({
                'page_num': page_idx + 1,
                'text': page_text,
                'words': words_data
            })
            extracted_data['raw_text'] += page_text + "\n"
        
        return extracted_data
    
    def parse_payslip_data(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parser les données spécifiques au bulletin de salaire"""
        raw_text = text_data['raw_text']
        
        # Dictionnaire pour stocker les données extraites
        payslip_data = {
            'employee_info': {},
            'employer_info': {},
            'pay_period': {},
            'earnings': [],
            'deductions': [],
            'totals': {},
            'raw_text': raw_text
        }
        
        # Patterns regex pour extraire les informations
        patterns = {
            'employee_name': r'(?:Nom|Salarié|Employé)[:\s]*([A-Z\s]+)',
            'employee_id': r'(?:Matricule|ID|N°)[:\s]*(\d+)',
            'period': r'(?:Période|Mois)[:\s]*(\d{2}/\d{4})',
            'gross_salary': r'(?:Salaire brut|Brut)[:\s]*([0-9,]+\.?\d*)',
            'net_salary': r'(?:Net à payer|Net)[:\s]*([0-9,]+\.?\d*)',
            'social_security': r'(?:Sécurité sociale|SS)[:\s]*([0-9,]+\.?\d*)'
        }
        
        # Extraire les données avec les patterns
        for key, pattern in patterns.items():
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                if key.startswith('employee_'):
                    payslip_data['employee_info'][key.replace('employee_', '')] = match.group(1).strip()
                elif key == 'period':
                    payslip_data['pay_period']['period'] = match.group(1).strip()
                elif key in ['gross_salary', 'net_salary']:
                    payslip_data['totals'][key] = match.group(1).strip()
                else:
                    payslip_data['totals'][key] = match.group(1).strip()
        
        return payslip_data
    
    def extract_payslip(self, pdf_path: str, output_path: str = None) -> Dict[str, Any]:
        """Fonction principale pour extraire les données du bulletin"""
        print(f"📄 Extraction des données de: {pdf_path}")
        
        # Étape 1: OCR
        print("🔍 Extraction du texte avec OCR...")
        text_data = self.extract_text_from_pdf(pdf_path)
        
        # Étape 2: Parsing des données
        print("📊 Analyse des données du bulletin...")
        payslip_data = self.parse_payslip_data(text_data)
        
        # Étape 3: Sauvegarde (optionnel)
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(payslip_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Données sauvegardées dans: {output_path}")
        
        return payslip_data


def main():
    """Fonction principale"""
    # Chemin vers votre bulletin de salaire
    pdf_path = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF"
    
    # Vérifier que le fichier existe
    if not Path(pdf_path).exists():
        print(f"❌ Fichier non trouvé: {pdf_path}")
        return
    
    # Créer l'extracteur
    extractor = PayslipExtractor()
    
    # Extraire les données
    try:
        results = extractor.extract_payslip(
            pdf_path=pdf_path,
            output_path="payslip_extracted_data.json"
        )
        
        # Afficher les résultats
        print("\n" + "="*50)
        print("📋 RÉSULTATS DE L'EXTRACTION")
        print("="*50)
        
        print("\n👤 INFORMATIONS EMPLOYÉ:")
        for key, value in results['employee_info'].items():
            print(f"  {key}: {value}")
        
        print("\n📅 PÉRIODE:")
        for key, value in results['pay_period'].items():
            print(f"  {key}: {value}")
        
        print("\n💰 TOTAUX:")
        for key, value in results['totals'].items():
            print(f"  {key}: {value}")
        
        print(f"\n📝 TEXTE BRUT EXTRAIT:")
        print("-" * 30)
        print(results['raw_text'][:500] + "..." if len(results['raw_text']) > 500 else results['raw_text'])
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")


if __name__ == "__main__":
    main()
