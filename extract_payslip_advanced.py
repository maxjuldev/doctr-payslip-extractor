#!/usr/bin/env python3
"""
Script avancé pour extraire les données des bulletins de salaire avec docTR
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from doctr.models import ocr_predictor
from doctr.io import DocumentFile


class PayslipExtractorAdvanced:
    """Extracteur avancé pour bulletins de salaire français"""
    
    def __init__(self):
        print("🔍 Chargement du modèle OCR...")
        self.model = ocr_predictor(pretrained=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extraire le texte du PDF avec OCR"""
        print(f"📄 Chargement du PDF: {pdf_path}")
        
        # Charger le document
        print("📖 Lecture du document...")
        doc = DocumentFile.from_pdf(pdf_path)
        
        # Effectuer l'OCR
        print("🔍 Extraction du texte...")
        result = self.model(doc)
        
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
    
    def parse_payslip_advanced(self, text: str) -> Dict[str, Any]:
        """Parser avancé pour extraire toutes les données du bulletin"""
        print("📊 Analyse avancée du texte extrait...")
        
        # Structure pour stocker toutes les données
        payslip_data = {
            'employer_info': {},
            'employee_info': {},
            'pay_period': {},
            'employment_details': {},
            'salary_elements': {},
            'deductions': {},
            'totals': {},
            'social_charges': {},
            'tax_info': {},
            'leave_info': {},
            'raw_text': text
        }
        
        # === INFORMATIONS EMPLOYEUR ===
        employer_patterns = {
            'company_name': r'(?:^|\n)([A-ZÀ-Ÿ\s&]+)\n[0-9]+',
            'siret': r'Siret\s*:?\s*([0-9\s]+)',
            'naf_code': r'Code\s*Naf\s*:?\s*([0-9A-Z]+)',
            'urssaf': r'Urssaf/Msa\s*:?\s*([0-9A-Z]+)'
        }
        
        # === INFORMATIONS EMPLOYÉ ===
        employee_patterns = {
            'matricule': r'Matricule\s*:?\s*([0-9]+)',
            'social_security': r'No\s*SS\s*:?\s*([0-9]+)',
            'full_name': r'(?:Madame|Monsieur|M\.|Mme)\s+([A-ZÀ-Ÿ\s]+)(?=\n[0-9]|\nAPPT|\n[A-Z]{2,})',
            'job_title': r'Emploi\s*-\s*([A-ZÀ-Ÿ\s-]+)',
            'start_date': r'Entrée\s*:?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})',
            'seniority': r'Ancienneté[:\s-]*([0-9]+\s*an[s]?\s*(?:et\s*[0-9]+\s*mois)?)'
        }
        
        # === PÉRIODE DE PAIE ===
        period_patterns = {
            'period': r'Période\s+([A-ZÀ-Ÿ]+\s+[0-9]{4})',
            'payment_date': r'Paiement\s+le\s+([0-9]{2}/[0-9]{2}/[0-9]{4})',
            'payment_method': r'par\s+(Chèque|Virement|Espèces)'
        }
        
        # === ÉLÉMENTS DE SALAIRE ===
        salary_patterns = {
            'base_salary': r'Salaire\s+de\s+base\s+([0-9\s,]+\.?[0-9]*)',
            'gross_salary': r'Salaire\s+brut\s+([0-9\s,]+\.?[0-9]*)',
            'variable_pay': r'Rémunération\s+variable[^0-9]*([0-9\s,]+\.?[0-9]*)',
            'net_before_tax': r'Net\s+à\s+payer\s+avant\s+impôt[^0-9]*([0-9\s,]+\.?[0-9]*)',
            'net_paid': r'Net\s+payé?\s+([0-9\s,]+\.?[0-9]*)',
            'social_net': r'Montant\s+net\s+social\s+([0-9\s,]+\.?[0-9]*)'
        }
        
        # === CHARGES ET COTISATIONS ===
        charges_patterns = {
            'total_deductions': r'Total\s+des\s+retenues\s+([0-9\s,]+\.?[0-9]*)',
            'social_charges': r'Ch\.\s+patronales\s+([0-9\s,]+\.?[0-9]*)',
            'unemployment': r'Assurance\s+chômage[^0-9]*([0-9\s,]+\.?[0-9]*)',
            'health_insurance': r'Maladie[^0-9]*([0-9\s,]+\.?[0-9]*)',
            'pension': r'Vieillesse[^0-9]*([0-9\s,]+\.?[0-9]*)'
        }
        
        # === IMPÔTS ===
        tax_patterns = {
            'income_tax': r'Impôt\s+sur\s+le\s+revenu[^0-9]*([0-9\s,]+\.?[0-9]*)',
            'tax_rate': r'Taux\s+personnalisé[^0-9]*([0-9,]+\.?[0-9]*)',
            'yearly_tax_cumul': r'cumul\s+PAS\s+annuel[^0-9]*([0-9\s,]+\.?[0-9]*)'
        }
        
        # === CONGÉS ===
        leave_patterns = {
            'acquired_leave': r'Acquis[^0-9]*([0-9]+\.?[0-9]*)',
            'taken_leave': r'Pris[^0-9]*([0-9]+\.?[0-9]*)',
            'remaining_leave': r'Solde[^0-9]*([0-9]+\.?[0-9]*)'
        }
        
        # Extraction avec tous les patterns
        all_patterns = {
            'employer_info': employer_patterns,
            'employee_info': employee_patterns,
            'pay_period': period_patterns,
            'salary_elements': salary_patterns,
            'deductions': charges_patterns,
            'tax_info': tax_patterns,
            'leave_info': leave_patterns
        }
        
        for category, patterns in all_patterns.items():
            for key, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    # Nettoyer les valeurs numériques
                    if any(char.isdigit() for char in value):
                        # Remplacer les espaces dans les nombres
                        value = re.sub(r'(\d)\s+(\d)', r'\1\2', value)
                    payslip_data[category][key] = value
        
        # === TOTAUX ANNUELS ET MENSUELS ===
        monthly_match = re.search(r'Mensuel\s+([0-9\s,]+\.?[0-9]*)', text, re.IGNORECASE)
        if monthly_match:
            payslip_data['totals']['monthly_gross'] = monthly_match.group(1).strip()
        
        yearly_match = re.search(r'Annuel\s+([0-9\s,]+\.?[0-9]*)', text, re.IGNORECASE)
        if yearly_match:
            payslip_data['totals']['yearly_gross'] = yearly_match.group(1).strip()
        
        return payslip_data
    
    def format_output(self, data: Dict[str, Any]) -> str:
        """Formater la sortie pour affichage"""
        output = []
        output.append("=" * 60)
        output.append("📋 BULLETIN DE SALAIRE - DONNÉES EXTRAITES")
        output.append("=" * 60)
        
        # Informations employeur
        if data['employer_info']:
            output.append("\n🏢 INFORMATIONS EMPLOYEUR:")
            for key, value in data['employer_info'].items():
                output.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Informations employé
        if data['employee_info']:
            output.append("\n👤 INFORMATIONS EMPLOYÉ:")
            for key, value in data['employee_info'].items():
                output.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Période de paie
        if data['pay_period']:
            output.append("\n📅 PÉRIODE DE PAIE:")
            for key, value in data['pay_period'].items():
                output.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Éléments de salaire
        if data['salary_elements']:
            output.append("\n💰 ÉLÉMENTS DE SALAIRE:")
            for key, value in data['salary_elements'].items():
                output.append(f"  {key.replace('_', ' ').title()}: {value} €")
        
        # Charges et cotisations
        if data['deductions']:
            output.append("\n📉 CHARGES ET COTISATIONS:")
            for key, value in data['deductions'].items():
                output.append(f"  {key.replace('_', ' ').title()}: {value} €")
        
        # Informations fiscales
        if data['tax_info']:
            output.append("\n🧾 INFORMATIONS FISCALES:")
            for key, value in data['tax_info'].items():
                output.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Congés
        if data['leave_info']:
            output.append("\n🏖️ CONGÉS:")
            for key, value in data['leave_info'].items():
                output.append(f"  {key.replace('_', ' ').title()}: {value} jours")
        
        # Totaux
        if data['totals']:
            output.append("\n📊 TOTAUX:")
            for key, value in data['totals'].items():
                output.append(f"  {key.replace('_', ' ').title()}: {value} €")
        
        return "\n".join(output)
    
    def extract_payslip_complete(self, pdf_path: str, output_json: str = None) -> Dict[str, Any]:
        """Fonction principale complète"""
        print("🚀 Démarrage de l'extraction complète...")
        
        # Vérifier le fichier
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"Fichier non trouvé: {pdf_path}")
        
        # Extraire le texte
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            raise ValueError("Aucun texte extrait du PDF")
        
        print("✅ Texte extrait avec succès!")
        
        # Parser les données
        parsed_data = self.parse_payslip_advanced(text)
        
        # Sauvegarder si demandé
        if output_json:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Données complètes sauvegardées dans: {output_json}")
        
        return parsed_data


def main():
    """Fonction principale"""
    pdf_path = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF"
    
    # Créer l'extracteur
    extractor = PayslipExtractorAdvanced()
    
    try:
        # Extraire les données
        results = extractor.extract_payslip_complete(
            pdf_path=pdf_path,
            output_json="bulletin_complet.json"
        )
        
        # Afficher les résultats formatés
        formatted_output = extractor.format_output(results)
        print(formatted_output)
        
        print(f"\n📄 Données brutes disponibles dans: bulletin_complet.json")
        print(f"📝 Pour voir le texte brut extrait, consultez le champ 'raw_text' du JSON")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    main()
