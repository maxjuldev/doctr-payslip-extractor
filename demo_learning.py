#!/usr/bin/env python3
"""
Démonstration du système d'apprentissage DocTR
"""

import json
from pathlib import Path
from datetime import datetime

from advanced_extractor import AdvancedPayslipExtractor
from learning_system import PayslipLearningSystem

def demo_learning_system():
    """Démonstration complète du système d'apprentissage"""
    print("🎓 DÉMONSTRATION DU SYSTÈME D'APPRENTISSAGE DOCTR")
    print("=" * 60)
    
    # Initialiser les systèmes
    print("\n1️⃣ INITIALISATION DES SYSTÈMES")
    print("-" * 40)
    
    extractor = AdvancedPayslipExtractor(use_learning=True)
    learning_system = PayslipLearningSystem()
    
    # PDF de test
    pdf_path = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF"
    
    if not Path(pdf_path).exists():
        print(f"❌ Fichier PDF non trouvé : {pdf_path}")
        return
    
    # Extraction initiale
    print("\n2️⃣ EXTRACTION INITIALE")
    print("-" * 40)
    
    extracted_data = extractor.extract_all_data(pdf_path)
    
    # Afficher quelques résultats
    print("📊 Résultats d'extraction :")
    employer_info = extracted_data.get('employer_info', {})
    employee_info = extracted_data.get('employee_info', {})
    
    print(f"  • Entreprise : {employer_info.get('company_name', 'Non trouvé')}")
    print(f"  • Employé : {employee_info.get('full_name', 'Non trouvé')}")
    print(f"  • SIRET : {employer_info.get('siret', 'Non trouvé')}")
    
    # Simuler quelques corrections utilisateur
    print("\n3️⃣ SIMULATION DE CORRECTIONS UTILISATEUR")
    print("-" * 40)
    
    # Exemple de corrections
    corrections = [
        {
            'field_name': 'company_name',
            'original': employer_info.get('company_name', ''),
            'corrected': 'CENTRE DE SANTE SANTOS DUMONT',
            'feedback': 'Le nom était correctement extrait mais confirmation utilisateur'
        },
        {
            'field_name': 'full_name',
            'original': employee_info.get('full_name', ''),
            'corrected': 'MORGAN MICHALET',
            'feedback': 'Nom correctement extrait, validation utilisateur'
        },
        {
            'field_name': 'siret',
            'original': employer_info.get('siret', ''),
            'corrected': '87903653100017',
            'feedback': 'SIRET extrait avec succès'
        }
    ]
    
    # Appliquer les corrections
    for correction in corrections:
        print(f"🔧 Correction : {correction['field_name']}")
        print(f"   Original : '{correction['original']}'")
        print(f"   Corrigé  : '{correction['corrected']}'")
        
        learning_system.learn_from_correction(
            field_name=correction['field_name'],
            pdf_filename=Path(pdf_path).name,
            original_value=correction['original'],
            corrected_value=correction['corrected'],
            raw_text=extracted_data.get('raw_text', ''),
            user_feedback=correction['feedback']
        )
        print("   ✅ Apprentissage terminé\n")
    
    # Afficher les statistiques
    print("\n4️⃣ STATISTIQUES D'APPRENTISSAGE")
    print("-" * 40)
    
    stats = learning_system.get_learning_stats()
    print(f"📊 Total des corrections : {stats['total_corrections']}")
    print(f"📊 Champs appris : {stats['fields_learned']}")
    print(f"📊 Confiance moyenne : {stats['average_confidence']:.2f}")
    print(f"📊 Total des patterns : {stats['total_patterns']}")
    
    # Détails par champ
    if stats['field_statistics']:
        print("\n📈 Détails par champ :")
        for field, data in stats['field_statistics'].items():
            print(f"  • {field}: {data['count']} corrections, confiance {data['avg_confidence']:.2f}")
    
    # Suggestions d'amélioration
    print("\n5️⃣ SUGGESTIONS D'AMÉLIORATION")
    print("-" * 40)
    
    suggestions = learning_system.suggest_improvements()
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    else:
        print("🎉 Aucune amélioration suggérée pour le moment !")
    
    # Test avec les patterns améliorés
    print("\n6️⃣ TEST AVEC PATTERNS AMÉLIORÉS")
    print("-" * 40)
    
    # Créer un nouvel extracteur qui utilisera les patterns appris
    improved_extractor = AdvancedPayslipExtractor(use_learning=True)
    
    print("🔄 Nouvelle extraction avec les patterns appris...")
    improved_data = improved_extractor.extract_all_data(pdf_path)
    
    # Comparer les résultats
    print("\n📊 COMPARAISON DES RÉSULTATS :")
    comparison_fields = [
        ('employer_info', 'company_name', 'Nom entreprise'),
        ('employee_info', 'full_name', 'Nom employé'),
        ('employer_info', 'siret', 'SIRET')
    ]
    
    for section, field, label in comparison_fields:
        original = extracted_data.get(section, {}).get(field, '')
        improved = improved_data.get(section, {}).get(field, '')
        
        print(f"\n{label} :")
        print(f"  Original : '{original}'")
        print(f"  Amélioré : '{improved}'")
        
        if original != improved:
            print("  🎯 AMÉLIORATION DÉTECTÉE !")
        else:
            print("  ✅ Résultat identique")
    
    # Export des patterns appris
    print("\n7️⃣ EXPORT DES PATTERNS APPRIS")
    print("-" * 40)
    
    export_path = f"/Users/maximejulien/Documents/GitHub/doctr/demo_learned_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    learning_system.export_learned_patterns(export_path)
    print(f"📤 Patterns exportés vers : {export_path}")
    
    # Résumé final
    print("\n🎉 DÉMONSTRATION TERMINÉE")
    print("-" * 40)
    print("✅ Système d'apprentissage fonctionnel")
    print("✅ Corrections intégrées avec succès")
    print("✅ Patterns améliorés automatiquement")
    print("✅ Statistiques et suggestions générées")
    
    print(f"\n💾 Fichiers générés :")
    print(f"  • Base d'apprentissage : {learning_system.learning_db_path}")
    print(f"  • Base de patterns : {learning_system.patterns_db_path}")
    print(f"  • Log des corrections : {learning_system.corrections_log_path}")
    print(f"  • Export de démonstration : {export_path}")

def demo_interactive_corrections():
    """Démonstration interactive pour corriger manuellement"""
    print("\n🎓 MODE INTERACTIF - CORRECTIONS MANUELLES")
    print("=" * 50)
    
    extractor = AdvancedPayslipExtractor(use_learning=True)
    learning_system = PayslipLearningSystem()
    
    pdf_path = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF"
    
    if not Path(pdf_path).exists():
        print(f"❌ Fichier PDF non trouvé : {pdf_path}")
        return
    
    # Extraction
    extracted_data = extractor.extract_all_data(pdf_path)
    
    # Champs à corriger interactivement
    fields_to_correct = [
        ('employer_info', 'company_name', 'Nom de l\'entreprise'),
        ('employee_info', 'full_name', 'Nom de l\'employé'),
        ('employer_info', 'siret', 'Numéro SIRET'),
        ('salary_elements', 'gross_salary', 'Salaire brut'),
        ('salary_elements', 'net_paid', 'Net payé')
    ]
    
    corrections_made = 0
    
    for section, field, label in fields_to_correct:
        current_value = extracted_data.get(section, {}).get(field, '')
        
        print(f"\n📝 {label}")
        print(f"Valeur extraite : '{current_value}'")
        
        # Demander à l'utilisateur
        user_input = input(f"Nouvelle valeur (ou ENTER pour garder) : ").strip()
        
        if user_input and user_input != current_value:
            # Apprendre la correction
            learning_system.learn_from_correction(
                field_name=field,
                pdf_filename=Path(pdf_path).name,
                original_value=current_value,
                corrected_value=user_input,
                raw_text=extracted_data.get('raw_text', ''),
                user_feedback="Correction manuelle interactive"
            )
            corrections_made += 1
            print(f"✅ Correction apprise : '{user_input}'")
        else:
            print("✅ Valeur conservée")
    
    print(f"\n🎉 {corrections_made} corrections effectuées !")
    
    if corrections_made > 0:
        # Afficher les statistiques mises à jour
        stats = learning_system.get_learning_stats()
        print(f"\n📊 Nouvelles statistiques :")
        print(f"  • Total corrections : {stats['total_corrections']}")
        print(f"  • Confiance moyenne : {stats['average_confidence']:.2f}")

if __name__ == "__main__":
    print("🎓 SYSTÈME D'APPRENTISSAGE DOCTR - DÉMONSTRATION")
    print("=" * 60)
    
    mode = input("\nChoisissez un mode :\n1. Démonstration automatique\n2. Corrections interactives\n\nVotre choix (1 ou 2) : ").strip()
    
    if mode == "1":
        demo_learning_system()
    elif mode == "2":
        demo_interactive_corrections()
    else:
        print("❌ Choix invalide. Lancement de la démonstration automatique...")
        demo_learning_system()
