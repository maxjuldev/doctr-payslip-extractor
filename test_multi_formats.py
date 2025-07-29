#!/usr/bin/env python3
"""
Test de compatibilité avec différents formats de bulletins de paie
Teste l'adaptabilité de l'extracteur sur divers logiciels RH
"""

import os
from pathlib import Path
from advanced_extractor import AdvancedPayslipExtractor
import json

def test_multiple_formats():
    """Tester l'extracteur sur différents formats de bulletins"""
    
    print("🧪 TEST DE COMPATIBILITÉ MULTI-FORMATS")
    print("=" * 60)
    
    # Différents dossiers de formats
    test_folders = {
        "EBP (ORFEO)": "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/modeles/ebp",
        "CEGID": "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/modeles/cegid",
        "Bulletins Existants": "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire"
    }
    
    extractor = AdvancedPayslipExtractor()
    all_results = {}
    
    for format_name, folder_path in test_folders.items():
        print(f"\n📁 TEST DU FORMAT: {format_name}")
        print("-" * 40)
        
        if not Path(folder_path).exists():
            print(f"   ⚠️  Dossier non trouvé: {folder_path}")
            continue
        
        # Trouver les PDFs
        pdf_files = list(Path(folder_path).glob("*.pdf")) + list(Path(folder_path).glob("*.PDF"))
        
        if not pdf_files:
            print(f"   ⚠️  Aucun PDF trouvé dans {folder_path}")
            continue
        
        print(f"   📄 {len(pdf_files)} fichier(s) trouvé(s)")
        
        format_results = []
        
        for pdf_file in pdf_files:
            print(f"   🔍 Analyse: {pdf_file.name}")
            
            try:
                # Test d'extraction
                data = extractor.extract_all_data(str(pdf_file))
                
                # Calculer le taux de succès
                total_fields = count_total_fields(data)
                extracted_fields = count_extracted_fields(data)
                success_rate = (extracted_fields / total_fields) * 100 if total_fields > 0 else 0
                
                # Extraire les infos clés
                employee = data.get('employee_info', {}).get('full_name', 'Non détecté')
                company = data.get('employer_info', {}).get('company_name', 'Non détecté')
                period = data.get('pay_period', {}).get('period', 'Non détectée')
                gross = data.get('salary_elements', {}).get('gross_salary', 'Non détecté')
                net = data.get('salary_elements', {}).get('net_paid', 'Non détecté')
                
                result_summary = {
                    'file_name': pdf_file.name,
                    'format_detected': format_name,
                    'success_rate': success_rate,
                    'total_fields': total_fields,
                    'extracted_fields': extracted_fields,
                    'employee': employee,
                    'company': company,
                    'period': period,
                    'gross_salary': gross,
                    'net_paid': net,
                    'full_data': data
                }
                
                format_results.append(result_summary)
                
                print(f"      ✅ Taux: {success_rate:.1f}% ({extracted_fields}/{total_fields})")
                print(f"      👤 Employé: {employee}")
                print(f"      🏢 Entreprise: {company}")
                print(f"      💰 Brut: {gross} | Net: {net}")
                
            except Exception as e:
                print(f"      ❌ Erreur: {str(e)[:100]}...")
                continue
        
        all_results[format_name] = format_results
        
        # Statistiques par format
        if format_results:
            avg_success = sum(r['success_rate'] for r in format_results) / len(format_results)
            print(f"   📊 Taux moyen pour {format_name}: {avg_success:.1f}%")
    
    # Analyse comparative
    print(f"\n🎯 ANALYSE COMPARATIVE DES FORMATS")
    print("=" * 50)
    
    for format_name, results in all_results.items():
        if results:
            avg_rate = sum(r['success_rate'] for r in results) / len(results)
            best_rate = max(r['success_rate'] for r in results)
            worst_rate = min(r['success_rate'] for r in results)
            
            print(f"\n📋 {format_name}:")
            print(f"   📄 Bulletins testés: {len(results)}")
            print(f"   🎯 Taux moyen: {avg_rate:.1f}%")
            print(f"   📈 Meilleur: {best_rate:.1f}%")
            print(f"   📉 Plus bas: {worst_rate:.1f}%")
            
            # Identifier les champs les mieux extraits par format
            common_fields = analyze_common_fields(results)
            if common_fields:
                print(f"   🏆 Champs les plus fiables:")
                for field in common_fields[:3]:
                    print(f"      • {field}")
    
    return all_results

def count_total_fields(data):
    """Compter le nombre total de champs possibles"""
    total = 0
    for category in data.values():
        if isinstance(category, dict):
            total += len(category)
    return total

def count_extracted_fields(data):
    """Compter le nombre de champs extraits avec succès"""
    extracted = 0
    for category in data.values():
        if isinstance(category, dict):
            for value in category.values():
                if value and value != "Non trouvé":
                    extracted += 1
    return extracted

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

def analyze_common_fields(results):
    """Analyser les champs les plus communément extraits"""
    field_success = {}
    
    for result in results:
        flat_data = flatten_dict(result['full_data'])
        for field, value in flat_data.items():
            if field not in field_success:
                field_success[field] = 0
            if value and value != 'Non trouvé':
                field_success[field] += 1
    
    # Trier par fréquence d'extraction
    sorted_fields = sorted(field_success.items(), key=lambda x: x[1], reverse=True)
    return [field for field, count in sorted_fields if count > 0]

def save_compatibility_report(all_results):
    """Sauvegarder le rapport de compatibilité"""
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report_path = f"rapport_compatibilite_{timestamp}.json"
    
    # Préparer le rapport
    report = {
        'test_date': datetime.now().isoformat(),
        'formats_tested': list(all_results.keys()),
        'total_bulletins': sum(len(results) for results in all_results.values()),
        'results_by_format': {}
    }
    
    for format_name, results in all_results.items():
        if results:
            report['results_by_format'][format_name] = {
                'bulletins_count': len(results),
                'average_success_rate': sum(r['success_rate'] for r in results) / len(results),
                'best_success_rate': max(r['success_rate'] for r in results),
                'worst_success_rate': min(r['success_rate'] for r in results),
                'detailed_results': results
            }
    
    # Sauvegarder
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Rapport de compatibilité sauvegardé: {report_path}")
    return report_path

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU TEST DE COMPATIBILITÉ MULTI-FORMATS")
    
    results = test_multiple_formats()
    
    if results:
        report_file = save_compatibility_report(results)
        
        print(f"\n🎉 TEST TERMINÉ!")
        print(f"📊 L'extracteur a été testé sur différents formats de bulletins")
        print(f"📁 Rapport détaillé disponible dans: {report_file}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   • L'extracteur utilise des patterns regex adaptatifs")
        print(f"   • Plus de 79 champs sont recherchés sur chaque bulletin")
        print(f"   • Le système s'adapte automatiquement aux différentes mises en page")
        print(f"   • Les taux de succès varient selon la qualité OCR et la structure")
    else:
        print("❌ Aucun résultat de test disponible")
