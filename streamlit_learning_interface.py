#!/usr/bin/env python3
"""
Interface Streamlit interactive pour corriger et entraîner l'extracteur
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List

from advanced_extractor import AdvancedPayslipExtractor
from learning_system import PayslipLearningSystem

def main():
    st.set_page_config(
        page_title="🎓 DocTR Learning Interface",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Interface d'Apprentissage DocTR")
    st.sidebar.title("📚 Menu d'Apprentissage")
    
    # Initialiser les systèmes
    if 'extractor' not in st.session_state:
        st.session_state.extractor = AdvancedPayslipExtractor()
    if 'learning_system' not in st.session_state:
        st.session_state.learning_system = PayslipLearningSystem()
    
    # Menu sidebar
    mode = st.sidebar.selectbox(
        "Mode d'utilisation",
        ["🔍 Extraire et Corriger", "📊 Statistiques d'Apprentissage", "⚙️ Gestion des Patterns"]
    )
    
    if mode == "🔍 Extraire et Corriger":
        extract_and_correct_mode()
    elif mode == "📊 Statistiques d'Apprentissage":
        learning_statistics_mode()
    elif mode == "⚙️ Gestion des Patterns":
        pattern_management_mode()

def extract_and_correct_mode():
    """Mode extraction et correction"""
    st.header("🔍 Extraction et Correction des Bulletins")
    
    # Upload de fichier
    uploaded_file = st.file_uploader(
        "📄 Téléchargez un bulletin de salaire (PDF)",
        type=['pdf'],
        help="Sélectionnez un fichier PDF de bulletin de salaire"
    )
    
    if uploaded_file is not None:
        # Sauvegarder temporairement le fichier
        temp_path = f"/tmp/{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        
        st.success(f"✅ Fichier téléchargé : {uploaded_file.name}")
        
        # Bouton d'extraction
        if st.button("🚀 Extraire les données", type="primary"):
            with st.spinner("🔍 Extraction en cours..."):
                try:
                    # Extraire les données
                    extracted_data = st.session_state.extractor.extract_all_data(temp_path)
                    st.session_state.extracted_data = extracted_data
                    st.session_state.pdf_filename = uploaded_file.name
                    st.success("✅ Extraction terminée !")
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'extraction : {str(e)}")
        
        # Afficher les résultats et permettre les corrections
        if 'extracted_data' in st.session_state:
            show_correction_interface()

def show_correction_interface():
    """Interface de correction"""
    st.subheader("✏️ Correction des Données Extraites")
    
    data = st.session_state.extracted_data
    pdf_filename = st.session_state.pdf_filename
    
    # Tabs pour organiser les sections
    tabs = st.tabs([
        "🏢 Employeur", "👤 Employé", "💼 Emploi", 
        "💰 Salaire", "📊 Totaux", "📅 Dates"
    ])
    
    corrections = {}
    
    with tabs[0]:  # Employeur
        st.write("**Informations Employeur**")
        employer_data = data.get('employer_info', {})
        corrections.update(create_correction_fields("employer_info", employer_data, [
            'company_name', 'address_line1', 'postal_code', 'city', 
            'siret', 'naf_code', 'urssaf_number', 'SIREN'
        ]))
    
    with tabs[1]:  # Employé
        st.write("**Informations Employé**")
        employee_data = data.get('employee_info', {})
        corrections.update(create_correction_fields("employee_info", employee_data, [
            'full_name', 'title', 'matricule', 'social_security',
            'address_line1', 'address_line2', 'postal_code', 'city'
        ]))
    
    with tabs[2]:  # Emploi
        st.write("**Détails d'Emploi**")
        employment_data = data.get('employment_details', {})
        corrections.update(create_correction_fields("employment_details", employment_data, [
            'job_title', 'start_date', 'seniority'
        ]))
    
    with tabs[3]:  # Salaire
        st.write("**Éléments de Salaire**")
        salary_data = data.get('salary_elements', {})
        corrections.update(create_correction_fields("salary_elements", salary_data, [
            'base_salary', 'variable_pay', 'gross_salary', 
            'net_before_tax', 'net_paid', 'social_net'
        ]))
    
    with tabs[4]:  # Totaux
        st.write("**Totaux**")
        totals_data = data.get('totals', {})
        corrections.update(create_correction_fields("totals", totals_data, [
            'taxable_net', 'employer_charges', 'global_cost', 'total_paid'
        ]))
    
    with tabs[5]:  # Dates
        st.write("**Informations de Paiement**")
        payment_data = data.get('payment_info', {})
        corrections.update(create_correction_fields("payment_info", payment_data, [
            'payment_date', 'payment_method'
        ]))
    
    # Bouton pour sauvegarder les corrections
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎓 Enregistrer les Corrections et Apprendre", type="primary", use_container_width=True):
            save_corrections(corrections, pdf_filename, data.get('raw_text', ''))

def create_correction_fields(section_name: str, section_data: Dict, field_names: List[str]) -> Dict:
    """Créer les champs de correction pour une section"""
    corrections = {}
    
    for field_name in field_names:
        if field_name in section_data:
            original_value = section_data[field_name]
            
            # Créer deux colonnes : original et correction
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.text_input(
                    f"📄 {field_name.replace('_', ' ').title()} (Original)",
                    value=original_value,
                    disabled=True,
                    key=f"original_{section_name}_{field_name}"
                )
            
            with col2:
                corrected_value = st.text_input(
                    f"✏️ {field_name.replace('_', ' ').title()} (Corrigé)",
                    value=original_value,
                    key=f"corrected_{section_name}_{field_name}",
                    help="Modifiez cette valeur si elle est incorrecte"
                )
                
                # Enregistrer si différent de l'original
                if corrected_value != original_value:
                    corrections[f"{section_name}.{field_name}"] = {
                        'original': original_value,
                        'corrected': corrected_value,
                        'field_name': field_name
                    }
    
    return corrections

def save_corrections(corrections: Dict, pdf_filename: str, raw_text: str):
    """Sauvegarder les corrections et déclencher l'apprentissage"""
    if not corrections:
        st.info("ℹ️ Aucune correction à enregistrer.")
        return
    
    learning_system = st.session_state.learning_system
    corrections_count = 0
    
    with st.spinner("🎓 Apprentissage en cours..."):
        for field_key, correction_data in corrections.items():
            try:
                learning_system.learn_from_correction(
                    field_name=correction_data['field_name'],
                    pdf_filename=pdf_filename,
                    original_value=correction_data['original'],
                    corrected_value=correction_data['corrected'],
                    raw_text=raw_text,
                    user_feedback=f"Correction manuelle via interface web"
                )
                corrections_count += 1
            except Exception as e:
                st.error(f"❌ Erreur lors de l'apprentissage pour {field_key}: {str(e)}")
    
    if corrections_count > 0:
        st.success(f"🎉 {corrections_count} corrections enregistrées et apprises avec succès !")
        
        # Afficher les améliorations suggérées
        suggestions = learning_system.suggest_improvements()
        if suggestions:
            st.info("💡 **Suggestions d'amélioration :**")
            for suggestion in suggestions:
                st.write(f"  • {suggestion}")
        
        # Proposer de réextraire avec les nouveaux patterns
        if st.button("🔄 Réextraire avec les patterns améliorés"):
            st.rerun()

def learning_statistics_mode():
    """Mode statistiques d'apprentissage"""
    st.header("📊 Statistiques d'Apprentissage")
    
    learning_system = st.session_state.learning_system
    stats = learning_system.get_learning_stats()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Corrections", stats['total_corrections'])
    
    with col2:
        st.metric("Champs Appris", stats['fields_learned'])
    
    with col3:
        st.metric("Confiance Moyenne", f"{stats['average_confidence']:.2f}")
    
    with col4:
        st.metric("Total Patterns", stats['total_patterns'])
    
    # Graphiques
    if stats['field_statistics']:
        st.subheader("📈 Statistiques par Champ")
        
        # Préparer les données pour le graphique
        field_data = []
        for field, data in stats['field_statistics'].items():
            field_data.append({
                'Champ': field.replace('_', ' ').title(),
                'Corrections': data['count'],
                'Confiance': data['avg_confidence']
            })
        
        df = pd.DataFrame(field_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(df.set_index('Champ')['Corrections'])
            st.caption("Nombre de corrections par champ")
        
        with col2:
            st.bar_chart(df.set_index('Champ')['Confiance'])
            st.caption("Confiance moyenne par champ")
    
    # Suggestions d'amélioration
    st.subheader("💡 Suggestions d'Amélioration")
    suggestions = learning_system.suggest_improvements()
    
    if suggestions:
        for suggestion in suggestions:
            st.info(suggestion)
    else:
        st.success("🎉 Excellent ! Aucune amélioration nécessaire pour le moment.")
    
    # Export des données
    st.subheader("📤 Export des Données")
    if st.button("📊 Exporter les Patterns Appris"):
        export_path = f"/Users/maximejulien/Documents/GitHub/doctr/learned_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        learning_system.export_learned_patterns(export_path)
        st.success(f"✅ Patterns exportés vers : {export_path}")

def pattern_management_mode():
    """Mode gestion des patterns"""
    st.header("⚙️ Gestion des Patterns")
    
    learning_system = st.session_state.learning_system
    
    # Afficher les patterns actuels
    st.subheader("🔍 Patterns Actuels")
    
    patterns_data = []
    for pattern in learning_system.pattern_rules:
        patterns_data.append({
            'Champ': pattern.field_name,
            'Pattern': pattern.pattern[:50] + "..." if len(pattern.pattern) > 50 else pattern.pattern,
            'Priorité': pattern.priority,
            'Taux de Succès': f"{pattern.success_rate:.2f}",
            'Utilisations': pattern.usage_count,
            'Dernière Utilisation': pattern.last_used or "Jamais"
        })
    
    if patterns_data:
        df = pd.DataFrame(patterns_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ℹ️ Aucun pattern disponible. Commencez par faire quelques corrections.")
    
    # Outils de maintenance
    st.subheader("🛠️ Outils de Maintenance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Réinitialiser les Patterns"):
            if st.session_state.get('confirm_reset', False):
                learning_system.pattern_rules = learning_system._initialize_default_patterns()
                learning_system._save_patterns_database()
                st.success("✅ Patterns réinitialisés !")
                st.session_state.confirm_reset = False
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ Cliquez à nouveau pour confirmer la réinitialisation")
    
    with col2:
        if st.button("🧹 Nettoyer les Patterns Faibles"):
            weak_patterns = [p for p in learning_system.pattern_rules if p.success_rate < 0.3]
            if weak_patterns:
                learning_system.pattern_rules = [p for p in learning_system.pattern_rules if p.success_rate >= 0.3]
                learning_system._save_patterns_database()
                st.success(f"✅ {len(weak_patterns)} patterns faibles supprimés !")
            else:
                st.info("ℹ️ Aucun pattern faible à supprimer.")
    
    with col3:
        if st.button("📊 Recalculer les Statistiques"):
            # Recalculer les statistiques
            for pattern in learning_system.pattern_rules:
                pattern.usage_count = len([e for e in learning_system.learning_entries 
                                         if e.field_name == pattern.field_name])
            learning_system._save_patterns_database()
            st.success("✅ Statistiques recalculées !")

if __name__ == "__main__":
    main()
