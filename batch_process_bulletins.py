#!/usr/bin/env python3
"""
Script de traitement en lot pour extraire TOUTES les données des bulletins d'un dossier
Utilise l'extracteur avancé pour capturer 79+ champs de données
"""

import os
from pathlib import Path
from advanced_extractor import AdvancedPayslipExtractor
import json
import csv
from datetime import datetime


def process_payslip_directory():
    """Traiter tous les bulletins du dossier avec extraction complète"""
    
    # Dossier contenant vos bulletins
    bulletins_folder = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire"
    
    print("🚀 TRAITEMENT EN LOT AVANCÉ DES BULLETINS DE SALAIRE")
    print("=" * 60)
    print(f"📁 Dossier source: {bulletins_folder}")
    
    # Vérifier que le dossier existe
    if not Path(bulletins_folder).exists():
        print(f"❌ Dossier non trouvé: {bulletins_folder}")
        return
    
    # Créer l'extracteur avancé
    extractor = AdvancedPayslipExtractor()
    
    # Trouver tous les PDFs
    pdf_files = list(Path(bulletins_folder).glob("*.pdf")) + list(Path(bulletins_folder).glob("*.PDF"))
    
    if not pdf_files:
        print(f"❌ Aucun fichier PDF trouvé dans {bulletins_folder}")
        return
    
    print(f"� {len(pdf_files)} fichier(s) PDF trouvé(s)")
    
    # Traiter chaque fichier
    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n� Traitement {i}/{len(pdf_files)}: {pdf_file.name}")
        
        try:
            data = extractor.extract_all_data(str(pdf_file))
            results.append(data)
            
            # Afficher les infos principales
            employee = data.get('employee_info', {}).get('full_name', 'Inconnu')
            period = data.get('pay_period', {}).get('period', 'Inconnue')
            gross = data.get('salary_elements', {}).get('gross_salary', 'Inconnu')
            net = data.get('salary_elements', {}).get('net_paid', 'Inconnu')
            
            print(f"  ✅ {employee} - {period}")
            print(f"     💰 Brut: {gross} € | Net: {net} €")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            continue
    
    if results:
        # Sauvegarder les résultats
        save_advanced_results(results, bulletins_folder)
        
        # Afficher les statistiques
        display_advanced_statistics(results)
        
    else:
        print("❌ Aucun bulletin traité avec succès")


def save_advanced_results(results, output_dir):
    """Sauvegarder les résultats avec l'extracteur avancé"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sauvegarder en JSON détaillé
    json_path = Path(output_dir) / f"extraction_complete_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Créer un CSV avec les champs principaux
    csv_path = Path(output_dir) / f"bulletins_resume_{timestamp}.csv"
    
    # Préparer les données pour le CSV
    csv_data = []
    for result in results:
        row = {
            'Nom_Employe': result.get('employee_info', {}).get('full_name', ''),
            'Periode': result.get('pay_period', {}).get('period', ''),
            'Entreprise': result.get('employer_info', {}).get('company_name', ''),
            'Salaire_Brut': result.get('salary_elements', {}).get('gross_salary', ''),
            'Net_Paye': result.get('salary_elements', {}).get('net_paid', ''),
            'Net_Imposable': result.get('salary_elements', {}).get('taxable_net', ''),
            'Heures_Travaillees': result.get('work_info', {}).get('hours_worked', ''),
            'Conges_Acquis': result.get('leave_info', {}).get('vacation_balance', ''),
            'Cumul_Brut_Annuel': result.get('annual_data', {}).get('cumulative_gross', ''),
            'Cumul_Net_Annuel': result.get('annual_data', {}).get('cumulative_net', ''),
            'Date_Paiement': result.get('payment_info', {}).get('payment_date', ''),
            'Nombre_Champs_Extraits': len([v for v in flatten_dict(result).values() if v and v != 'Non trouvé'])
        }
        csv_data.append(row)
    
    # Écrire le CSV
    if csv_data:
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
    
    print(f"\n💾 FICHIERS SAUVEGARDÉS:")
    print(f"   📄 JSON détaillé: {json_path}")
    print(f"   📊 CSV résumé: {csv_path}")

def flatten_dict(d, parent_key='', sep='_'):
    """Aplatir un dictionnaire imbriqué"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def display_advanced_statistics(results):
    """Afficher des statistiques avancées"""
    print(f"\n📊 STATISTIQUES D'EXTRACTION AVANCÉES")
    print("=" * 50)
    
    # Calculs généraux
    total_bulletins = len(results)
    total_fields_possible = 79  # Nombre de champs dans l'extracteur avancé
    
    # Analyser les taux d'extraction
    extraction_rates = []
    salary_data = []
    
    for result in results:
        flat_data = flatten_dict(result)
        extracted_fields = len([v for v in flat_data.values() if v and v != 'Non trouvé'])
        extraction_rate = (extracted_fields / total_fields_possible) * 100
        extraction_rates.append(extraction_rate)
        
        # Collecter les données salariales
        gross = result.get('salary_elements', {}).get('gross_salary', '')
        net = result.get('salary_elements', {}).get('net_paid', '')
        
        if gross and gross != 'Non trouvé':
            try:
                amount = float(gross.replace(',', '.').replace(' ', '').replace('€', ''))
                salary_data.append(('brut', amount))
            except:
                pass
        
        if net and net != 'Non trouvé':
            try:
                amount = float(net.replace(',', '.').replace(' ', '').replace('€', ''))
                salary_data.append(('net', amount))
            except:
                pass
    
    # Afficher les statistiques
    if extraction_rates:
        avg_extraction = sum(extraction_rates) / len(extraction_rates)
        print(f"🎯 Taux d'extraction moyen: {avg_extraction:.1f}%")
        print(f"📈 Meilleur taux: {max(extraction_rates):.1f}%")
        print(f"📉 Taux le plus bas: {min(extraction_rates):.1f}%")
    
    if salary_data:
        gross_amounts = [amount for type_, amount in salary_data if type_ == 'brut']
        net_amounts = [amount for type_, amount in salary_data if type_ == 'net']
        
        if gross_amounts:
            print(f"💰 Salaire brut moyen: {sum(gross_amounts)/len(gross_amounts):,.2f} €")
            print(f"💎 Salaire brut max: {max(gross_amounts):,.2f} €")
        
        if net_amounts:
            print(f"💸 Net payé moyen: {sum(net_amounts)/len(net_amounts):,.2f} €")
    
    # Analyser les champs les plus/moins trouvés
    field_success = {}
    for result in results:
        flat_data = flatten_dict(result)
        for field, value in flat_data.items():
            if field not in field_success:
                field_success[field] = 0
            if value and value != 'Non trouvé':
                field_success[field] += 1
    
    # Top 5 champs les mieux extraits
    best_fields = sorted(field_success.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n🏆 TOP 5 CHAMPS LES MIEUX EXTRAITS:")
    for field, count in best_fields:
        percentage = (count / total_bulletins) * 100
        print(f"   {field}: {percentage:.0f}% ({count}/{total_bulletins})")
    
    print(f"\n📋 RÉSUMÉ:")
    print(f"   • {total_bulletins} bulletin(s) traité(s)")
    print(f"   • {total_fields_possible} champs possibles par bulletin")
    print(f"   • Extraction complète des données employeur, employé, salaire, charges, etc.")
    print(f"   • Sauvegarde JSON détaillée + CSV résumé")


if __name__ == "__main__":
    process_payslip_directory()
