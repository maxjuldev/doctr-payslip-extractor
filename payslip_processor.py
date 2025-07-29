#!/usr/bin/env python3
"""
Script final pour extraction de données de bulletins de salaire
Interface utilisateur et traitement en lot
"""

import json
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Any
import os

from doctr.models import ocr_predictor
from doctr.io import DocumentFile


class PayslipProcessor:
    """Processeur de bulletins de salaire avec interface utilisateur"""
    
    def __init__(self):
        print("🔍 Initialisation du processeur de bulletins...")
        self.model = ocr_predictor(pretrained=True)
        print("✅ Modèle OCR chargé avec succès!")
    
    def process_single_payslip(self, pdf_path: str) -> Dict[str, Any]:
        """Traiter un seul bulletin de salaire"""
        # Charger et extraire le texte
        doc = DocumentFile.from_pdf(pdf_path)
        result = self.model(doc)
        
        # Extraire le texte
        full_text = ""
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join([word.value for word in line.words])
                    full_text += line_text + "\n"
        
        # Parser les données importantes
        import re
        
        data = {
            'file_name': Path(pdf_path).name,
            'employer': self._extract_pattern(full_text, r'(?:^|\n)([A-ZÀ-Ÿ\s&]+)\n[0-9]+'),
            'employee_name': self._extract_pattern(full_text, r'(?:Madame|Monsieur|M\.|Mme)\s+([A-ZÀ-Ÿ\s]+)(?=\n[0-9]|\nAPPT)'),
            'matricule': self._extract_pattern(full_text, r'Matricule\s*:?\s*([0-9]+)'),
            'period': self._extract_pattern(full_text, r'Période\s+([A-ZÀ-Ÿ]+\s+[0-9]{4})'),
            'job_title': self._extract_pattern(full_text, r'Emploi\s*-\s*([A-ZÀ-Ÿ\s-]+)'),
            'gross_salary': self._extract_amount(full_text, r'Salaire\s+brut\s+([0-9\s,]+\.?[0-9]*)'),
            'net_before_tax': self._extract_amount(full_text, r'Net\s+à\s+payer\s+avant\s+impôt[^0-9]*([0-9\s,]+\.?[0-9]*)'),
            'net_paid': self._extract_amount(full_text, r'Net\s+payé?\s+([0-9\s,]+\.?[0-9]*)'),
            'income_tax': self._extract_amount(full_text, r'Impôt\s+sur\s+le\s+revenu[^0-9]*([0-9\s,]+\.?[0-9]*)'),
            'payment_date': self._extract_pattern(full_text, r'Paiement\s+le\s+([0-9]{2}/[0-9]{2}/[0-9]{4})'),
            'siret': self._extract_pattern(full_text, r'Siret\s*:?\s*([0-9\s]+)'),
            'start_date': self._extract_pattern(full_text, r'Entrée\s*:?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})'),
            'raw_text': full_text
        }
        
        return data
    
    def _extract_pattern(self, text: str, pattern: str) -> str:
        """Extraire un pattern du texte"""
        import re
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else ""
    
    def _extract_amount(self, text: str, pattern: str) -> str:
        """Extraire un montant et le formater"""
        import re
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            amount = match.group(1).strip()
            # Nettoyer les espaces dans les nombres
            amount = re.sub(r'(\d)\s+(\d)', r'\1\2', amount)
            return amount
        return ""
    
    def process_directory(self, directory_path: str, output_format: str = 'json') -> List[Dict[str, Any]]:
        """Traiter tous les PDFs d'un dossier"""
        directory = Path(directory_path)
        pdf_files = list(directory.glob("*.pdf")) + list(directory.glob("*.PDF"))
        
        if not pdf_files:
            print(f"❌ Aucun fichier PDF trouvé dans {directory_path}")
            return []
        
        print(f"📁 Traitement de {len(pdf_files)} fichier(s) PDF...")
        
        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"📄 Traitement {i}/{len(pdf_files)}: {pdf_file.name}")
            try:
                data = self.process_single_payslip(str(pdf_file))
                results.append(data)
                print(f"  ✅ {data.get('employee_name', 'Inconnu')} - {data.get('period', 'Période inconnue')}")
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
                continue
        
        # Sauvegarder les résultats
        self._save_results(results, output_format, directory)
        
        return results
    
    def _save_results(self, results: List[Dict[str, Any]], format_type: str, directory: Path):
        """Sauvegarder les résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type.lower() == 'csv':
            output_file = directory / f"bulletins_extraits_{timestamp}.csv"
            self._save_csv(results, output_file)
        else:  # JSON par défaut
            output_file = directory / f"bulletins_extraits_{timestamp}.json"
            self._save_json(results, output_file)
        
        print(f"💾 Résultats sauvegardés dans: {output_file}")
    
    def _save_json(self, results: List[Dict[str, Any]], output_file: Path):
        """Sauvegarder en JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def _save_csv(self, results: List[Dict[str, Any]], output_file: Path):
        """Sauvegarder en CSV"""
        if not results:
            return
        
        # Exclure raw_text du CSV pour la lisibilité
        fieldnames = [k for k in results[0].keys() if k != 'raw_text']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                row = {k: v for k, v in result.items() if k != 'raw_text'}
                writer.writerow(row)
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Afficher un résumé des résultats"""
        if not results:
            print("❌ Aucun résultat à afficher")
            return
        
        print("\n" + "="*80)
        print("📊 RÉSUMÉ DES BULLETINS TRAITÉS")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 Bulletin {i}:")
            print(f"  📁 Fichier: {result.get('file_name', 'Inconnu')}")
            print(f"  👤 Employé: {result.get('employee_name', 'Inconnu')}")
            print(f"  🏢 Employeur: {result.get('employer', 'Inconnu')}")
            print(f"  📅 Période: {result.get('period', 'Inconnue')}")
            print(f"  💰 Salaire brut: {result.get('gross_salary', 'Inconnu')} €")
            print(f"  💸 Net payé: {result.get('net_paid', 'Inconnu')} €")
            print(f"  📆 Date paiement: {result.get('payment_date', 'Inconnue')}")


def main():
    """Interface en ligne de commande"""
    parser = argparse.ArgumentParser(description="Extraction de données de bulletins de salaire avec docTR")
    parser.add_argument("path", help="Chemin vers un fichier PDF ou un dossier contenant des PDFs")
    parser.add_argument("--format", choices=['json', 'csv'], default='json', 
                       help="Format de sortie (json ou csv)")
    parser.add_argument("--summary", action='store_true', 
                       help="Afficher un résumé des résultats")
    
    args = parser.parse_args()
    
    # Créer le processeur
    processor = PayslipProcessor()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"❌ Chemin non trouvé: {args.path}")
        return
    
    print(f"🚀 Démarrage du traitement de: {args.path}")
    
    try:
        if path.is_file() and path.suffix.lower() == '.pdf':
            # Traiter un seul fichier
            print("📄 Traitement d'un fichier unique...")
            result = processor.process_single_payslip(str(path))
            results = [result]
            
            # Sauvegarder
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if args.format == 'csv':
                output_file = path.parent / f"bulletin_extrait_{timestamp}.csv"
                processor._save_csv(results, output_file)
            else:
                output_file = path.parent / f"bulletin_extrait_{timestamp}.json"
                processor._save_json(results, output_file)
            
            print(f"💾 Résultats sauvegardés dans: {output_file}")
            
        elif path.is_dir():
            # Traiter un dossier
            results = processor.process_directory(str(path), args.format)
        else:
            print("❌ Le chemin doit être un fichier PDF ou un dossier")
            return
        
        # Afficher le résumé si demandé
        if args.summary and results:
            processor.print_summary(results)
        
        print(f"\n✅ Traitement terminé! {len(results)} bulletin(s) traité(s)")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    # Import datetime ici pour éviter les erreurs
    from datetime import datetime
    
    # Si aucun argument, traiter le fichier exemple
    if len(os.sys.argv) == 1:
        print("🔧 Mode test - traitement du bulletin exemple...")
        processor = PayslipProcessor()
        pdf_path = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF"
        
        if Path(pdf_path).exists():
            result = processor.process_single_payslip(pdf_path)
            processor.print_summary([result])
            
            # Sauvegarder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(f"/Users/maximejulien/Documents/GitHub/doctr/bulletin_test_{timestamp}.json")
            processor._save_json([result], output_file)
            print(f"💾 Résultats sauvegardés dans: {output_file}")
        else:
            print("❌ Fichier exemple non trouvé")
    else:
        main()
