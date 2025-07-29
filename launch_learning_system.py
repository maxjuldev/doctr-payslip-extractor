#!/usr/bin/env python3
"""
Script de lancement rapide pour le système DocTR avec apprentissage
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time

def print_header():
    """Afficher l'en-tête du système"""
    print("🎓" + "=" * 60 + "🎓")
    print("   SYSTÈME D'APPRENTISSAGE DOCTR - LANCEMENT RAPIDE")
    print("🎓" + "=" * 60 + "🎓")

def check_dependencies():
    """Vérifier que toutes les dépendances sont présentes"""
    print("\n🔍 Vérification des dépendances...")
    
    required_files = [
        "advanced_extractor.py",
        "learning_system.py", 
        "streamlit_learning_interface.py",
        "demo_learning.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Fichiers manquants : {', '.join(missing_files)}")
        return False
    
    print("✅ Tous les fichiers requis sont présents")
    return True

def launch_web_interface():
    """Lancer l'interface web d'apprentissage"""
    print("\n🚀 Lancement de l'interface web d'apprentissage...")
    
    try:
        # Lancer Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_learning_interface.py",
            "--server.port", "8502",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        time.sleep(3)
        
        # Ouvrir le navigateur
        url = "http://localhost:8502"
        print(f"🌐 Ouverture de l'interface : {url}")
        webbrowser.open(url)
        
        print("✅ Interface web lancée avec succès !")
        print("📝 Vous pouvez maintenant :")
        print("   • Télécharger des bulletins PDF")
        print("   • Corriger les extractions")
        print("   • Voir les statistiques d'apprentissage")
        print("   • Gérer les patterns")
        
        return process
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement : {e}")
        return None

def launch_demo():
    """Lancer la démonstration"""
    print("\n🎮 Lancement de la démonstration...")
    
    try:
        subprocess.run([sys.executable, "demo_learning.py"], check=True)
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration : {e}")

def launch_simple_extraction():
    """Lancer une extraction simple"""
    print("\n🔍 Extraction simple d'un bulletin...")
    
    pdf_path = "/Users/maximejulien/Library/CloudStorage/OneDrive-FHB/Documents/Perso/testBS/bulletinsàextraire/BULLETIN DE SALAIRE-BULLETINS-2024 03 MICHALET MORGAN-1231-2024.PDF"
    
    if not Path(pdf_path).exists():
        print(f"❌ Fichier PDF non trouvé : {pdf_path}")
        return
    
    try:
        from advanced_extractor import AdvancedPayslipExtractor
        
        extractor = AdvancedPayslipExtractor(use_learning=True)
        data = extractor.extract_all_data(pdf_path)
        
        # Afficher quelques résultats clés
        print("📊 Résultats d'extraction :")
        employer = data.get('employer_info', {})
        employee = data.get('employee_info', {})
        salary = data.get('salary_elements', {})
        
        print(f"  🏢 Entreprise : {employer.get('company_name', 'Non trouvé')}")
        print(f"  👤 Employé : {employee.get('full_name', 'Non trouvé')}")  
        print(f"  💰 Salaire brut : {salary.get('gross_salary', 'Non trouvé')} €")
        print(f"  💵 Net payé : {salary.get('net_paid', 'Non trouvé')} €")
        
        print("✅ Extraction terminée avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction : {e}")

def show_stats():
    """Afficher les statistiques d'apprentissage"""
    print("\n📊 Statistiques d'apprentissage...")
    
    try:
        from learning_system import PayslipLearningSystem
        
        learning_system = PayslipLearningSystem()
        stats = learning_system.get_learning_stats()
        
        print(f"📈 Total des corrections : {stats['total_corrections']}")
        print(f"🎯 Champs appris : {stats['fields_learned']}")
        print(f"📊 Confiance moyenne : {stats['average_confidence']:.2f}")
        print(f"🔧 Total des patterns : {stats['total_patterns']}")
        
        if stats['field_statistics']:
            print("\n📋 Détails par champ :")
            for field, data in stats['field_statistics'].items():
                print(f"  • {field}: {data['count']} corrections, confiance {data['avg_confidence']:.2f}")
        
        # Suggestions
        suggestions = learning_system.suggest_improvements()
        if suggestions:
            print("\n💡 Suggestions d'amélioration :")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des stats : {e}")

def main():
    """Menu principal"""
    print_header()
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Impossible de continuer sans tous les fichiers requis.")
        return
    
    while True:
        print("\n🎯 QUE VOULEZ-VOUS FAIRE ?")
        print("-" * 40)
        print("1. 🌐 Lancer l'interface web d'apprentissage")
        print("2. 🎮 Voir la démonstration")
        print("3. 🔍 Extraction simple d'un bulletin")  
        print("4. 📊 Afficher les statistiques")
        print("5. 📚 Aide et documentation")
        print("6. 🚪 Quitter")
        print("-" * 40)
        
        choice = input("\nVotre choix (1-6) : ").strip()
        
        if choice == "1":
            process = launch_web_interface()
            if process:
                input("\n⏸️  Appuyez sur ENTER pour arrêter l'interface web...")
                process.terminate()
                print("🛑 Interface web arrêtée.")
                
        elif choice == "2":
            launch_demo()
            
        elif choice == "3":
            launch_simple_extraction()
            
        elif choice == "4":
            show_stats()
            
        elif choice == "5":
            show_help()
            
        elif choice == "6":
            print("\n👋 Au revoir ! Merci d'avoir utilisé DocTR Learning System.")
            break
            
        else:
            print("❌ Choix invalide. Veuillez choisir entre 1 et 6.")

def show_help():
    """Afficher l'aide"""
    print("\n📚 AIDE ET DOCUMENTATION")
    print("-" * 40)
    print("🎓 Le système d'apprentissage DocTR vous permet de :")
    print("   • Corriger les erreurs d'extraction automatiquement")
    print("   • Améliorer la précision au fil du temps")
    print("   • Gérer les patterns d'extraction")
    print("   • Suivre les performances via des statistiques")
    print()
    print("📖 Documentation complète : README_LEARNING.md")
    print("🌐 Interface web : http://localhost:8502 (quand lancée)")
    print("🎮 Démonstration : python demo_learning.py")
    print("🔍 Extraction simple : python advanced_extractor.py")
    print()
    print("💡 Conseil : Commencez par la démonstration pour comprendre le système !")

if __name__ == "__main__":
    main()
