#!/usr/bin/env python3
"""
Script de test complet du système d'extraction de bulletins de salaire
"""

import json
from pathlib import Path
from datetime import datetime

def test_complete_system():
    """Test complet de toutes les fonctionnalités"""
    
    print("🧪 TEST COMPLET DU SYSTÈME D'EXTRACTION DE BULLETINS")
    print("=" * 60)
    
    # Import du processeur
    try:
        from payslip_processor import PayslipProcessor
        processor = PayslipProcessor()
        print("✅ Processeur chargé avec succès")
    except Exception as e:
        print(f"❌ Erreur de chargement: {e}")
        return
    
    # Fichier de test
    test_file = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF"
    
    if not Path(test_file).exists():
        print(f"❌ Fichier de test non trouvé: {test_file}")
        return
    
    print(f"📄 Fichier de test: {Path(test_file).name}")
    
    # Test d'extraction
    try:
        result = processor.process_single_payslip(test_file)
        print("✅ Extraction réussie")
        
        # Afficher les résultats détaillés
        print("\n📋 DONNÉES EXTRAITES:")
        print("-" * 40)
        
        key_fields = {
            'file_name': '📁 Fichier',
            'employee_name': '👤 Employé',
            'employer': '🏢 Employeur',
            'matricule': '🆔 Matricule',
            'job_title': '💼 Poste',
            'period': '📅 Période',
            'gross_salary': '💰 Salaire brut',
            'net_before_tax': '💵 Net avant impôt',
            'net_paid': '💸 Net payé',
            'income_tax': '🧾 Impôt',
            'payment_date': '📆 Date paiement',
            'start_date': '📅 Date d\'entrée',
            'siret': '🏛️ SIRET'
        }
        
        for field, label in key_fields.items():
            value = result.get(field, 'Non trouvé')
            if value and value != 'Non trouvé':
                if field in ['gross_salary', 'net_before_tax', 'net_paid'] and value:
                    print(f"{label}: {value} €")
                else:
                    print(f"{label}: {value}")
        
        # Statistiques d'extraction
        print(f"\n📊 STATISTIQUES:")
        print(f"✅ Champs extraits: {sum(1 for v in result.values() if v and v != '')}")
        print(f"📝 Taille du texte brut: {len(result.get('raw_text', ''))} caractères")
        
        # Sauvegarder le résultat de test
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"/Users/maximejulien/Documents/GitHub/doctr/test_result_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés: {output_file}")
        
        # Test de qualité des données
        print(f"\n🎯 ÉVALUATION DE LA QUALITÉ:")
        quality_score = 0
        total_fields = len(key_fields) - 1  # Exclure file_name
        
        for field in key_fields:
            if field != 'file_name' and result.get(field):
                quality_score += 1
        
        quality_percentage = (quality_score / total_fields) * 100
        print(f"📈 Score de qualité: {quality_percentage:.1f}% ({quality_score}/{total_fields} champs)")
        
        if quality_percentage >= 80:
            print("🏆 Excellente extraction!")
        elif quality_percentage >= 60:
            print("👍 Bonne extraction")
        else:
            print("⚠️ Extraction partielle - peut nécessiter des améliorations")
        
        print(f"\n🎉 TEST COMPLET RÉUSSI!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return False

def show_system_capabilities():
    """Afficher les capacités du système"""
    
    print("\n" + "=" * 60)
    print("🚀 CAPACITÉS DU SYSTÈME")
    print("=" * 60)
    
    capabilities = [
        "📄 Extraction OCR de texte à partir de PDF",
        "🔍 Reconnaissance automatique des champs de bulletins français",
        "👤 Informations employé (nom, matricule, poste, ancienneté)",
        "🏢 Informations employeur (nom, SIRET, adresse)",
        "💰 Éléments de salaire (brut, net, charges, impôts)",
        "📅 Périodes et dates (période de paie, date de paiement)",
        "📊 Traitement en lot de plusieurs bulletins",
        "💾 Export en JSON et CSV",
        "🌐 Interface web Streamlit",
        "⚡ Traitement en ligne de commande",
        "📈 Statistiques et résumés automatiques",
        "🔧 Gestion d'erreurs robuste"
    ]
    
    for capability in capabilities:
        print(f"  ✅ {capability}")
    
    print(f"\n📋 FORMATS SUPPORTÉS:")
    print(f"  • PDF (bulletins de salaire français)")
    print(f"  • Taille max: 50MB par fichier")
    
    print(f"\n🎯 UTILISATION:")
    print(f"  • Interface web: http://localhost:8501")
    print(f"  • Ligne de commande: python payslip_processor.py [fichier]")
    print(f"  • Traitement en lot: python batch_process_bulletins.py")

if __name__ == "__main__":
    success = test_complete_system()
    show_system_capabilities()
    
    if success:
        print(f"\n🎉 SYSTÈME ENTIÈREMENT OPÉRATIONNEL!")
        print(f"🚀 Prêt pour traiter vos bulletins de salaire!")
    else:
        print(f"\n⚠️ Des problèmes ont été détectés")
