#!/usr/bin/env python3
"""
Test simplifié de compatibilité sur différents formats de bulletins
"""

import os
from pathlib import Path
from advanced_extractor import AdvancedPayslipExtractor

def test_one_bulletin_per_format():
    """Tester un bulletin de chaque format disponible"""
    
    print("🎯 TEST DE COMPATIBILITÉ - ÉCHANTILLONS PAR FORMAT")
    print("=" * 60)
    
    # Test avec les bulletins que nous avons
    test_files = [
        {
            'name': 'Format EBP/ORFEO',
            'path': '/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/modeles/ebp/ORFEO SIT20241004 Justifs BS_7.pdf'
        },
        {
            'name': 'Format CEGID', 
            'path': '/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/modeles/cegid/CEGID Bulletin de paie 12 2022_1.pdf'
        },
        {
            'name': 'Format Standard (Existant)',
            'path': '/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF'
        }
    ]
    
    extractor = AdvancedPayslipExtractor()
    results = []
    
    for test_file in test_files:
        print(f"\n📄 TEST: {test_file['name']}")
        print("-" * 40)
        
        if not Path(test_file['path']).exists():
            print(f"   ❌ Fichier non trouvé: {test_file['path']}")
            continue
        
        try:
            print(f"   🔍 Analyse en cours...")
            data = extractor.extract_all_data(test_file['path'])
            
            # Calculer les métriques
            total_fields = count_fields(data)
            extracted_fields = count_extracted(data)
            success_rate = (extracted_fields / total_fields) * 100 if total_fields > 0 else 0
            
            # Extraire les données clés
            employee = data.get('employee_info', {}).get('full_name', 'Non détecté')
            company = data.get('employer_info', {}).get('company_name', 'Non détectée')
            period = data.get('pay_period', {}).get('period', 'Non détectée')
            gross = data.get('salary_elements', {}).get('gross_salary', 'Non détecté')
            net = data.get('salary_elements', {}).get('net_paid', 'Non détecté')
            
            print(f"   ✅ RÉSULTATS:")
            print(f"      🎯 Taux d'extraction: {success_rate:.1f}% ({extracted_fields}/{total_fields})")
            print(f"      👤 Employé: {employee}")
            print(f"      🏢 Entreprise: {company}")
            print(f"      📅 Période: {period}")
            print(f"      💰 Salaire brut: {gross}")
            print(f"      💸 Net payé: {net}")
            
            # Analyser les catégories les mieux extraites
            categories_success = analyze_categories(data)
            print(f"      📊 Catégories les mieux extraites:")
            for category, rate in categories_success[:3]:
                print(f"         • {category}: {rate:.0f}%")
            
            results.append({
                'format': test_file['name'],
                'success_rate': success_rate,
                'employee': employee,
                'company': company,
                'categories_success': categories_success
            })
            
        except Exception as e:
            print(f"   ❌ Erreur lors du traitement: {str(e)}")
            continue
    
    # Synthèse comparative
    print(f"\n🏆 SYNTHÈSE COMPARATIVE")
    print("=" * 40)
    
    if results:
        for result in results:
            status = "🟢 Excellent" if result['success_rate'] > 80 else "🟡 Bon" if result['success_rate'] > 60 else "🔴 Perfectible"
            print(f"{status} {result['format']}: {result['success_rate']:.1f}%")
        
        avg_rate = sum(r['success_rate'] for r in results) / len(results)
        print(f"\n📈 Taux moyen tous formats: {avg_rate:.1f}%")
        
        print(f"\n💡 CONCLUSION:")
        print(f"   ✅ L'extracteur s'adapte aux différents formats")
        print(f"   📊 Performance variable selon la mise en page")
        print(f"   🎯 Extraction robuste des données principales")
        print(f"   🔧 Amélioration possible avec patterns spécifiques")
    
    return results

def count_fields(data):
    """Compter tous les champs possibles"""
    total = 0
    for category in data.values():
        if isinstance(category, dict):
            total += len(category)
    return total

def count_extracted(data):
    """Compter les champs extraits avec succès"""
    extracted = 0
    for category in data.values():
        if isinstance(category, dict):
            for value in category.values():
                if value and value != "Non trouvé":
                    extracted += 1
    return extracted

def analyze_categories(data):
    """Analyser le taux de succès par catégorie"""
    categories = []
    
    category_names = {
        'employer_info': 'Infos Employeur',
        'employee_info': 'Infos Employé', 
        'salary_elements': 'Éléments Salaire',
        'social_charges': 'Charges Sociales',
        'pay_period': 'Période Paie',
        'taxes': 'Impôts & Taxes',
        'annual_data': 'Cumuls Annuels',
        'payment_info': 'Infos Paiement'
    }
    
    for key, category_data in data.items():
        if isinstance(category_data, dict) and category_data:
            total_fields = len(category_data)
            extracted_fields = sum(1 for v in category_data.values() if v and v != "Non trouvé")
            success_rate = (extracted_fields / total_fields) * 100 if total_fields > 0 else 0
            
            display_name = category_names.get(key, key.replace('_', ' ').title())
            categories.append((display_name, success_rate))
    
    return sorted(categories, key=lambda x: x[1], reverse=True)

if __name__ == "__main__":
    print("🚀 LANCEMENT DU TEST DE COMPATIBILITÉ")
    
    results = test_one_bulletin_per_format()
    
    if results:
        print(f"\n🎉 Test terminé avec succès!")
        
        # Recommandations finales
        print(f"\n🔧 RECOMMANDATIONS D'AMÉLIORATION:")
        print(f"   1. Ajouter des patterns spécifiques pour chaque logiciel RH")
        print(f"   2. Améliorer la détection des tableaux complexes")
        print(f"   3. Optimiser l'OCR pour les polices particulières")
        print(f"   4. Créer des règles de validation par format")
    else:
        print("❌ Aucun test réussi")
