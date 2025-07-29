#!/usr/bin/env python3
"""
Interface Streamlit améliorée pour l'extraction de bulletins de salaire
Avec gestion d'erreurs et support de gros fichiers
"""

import streamlit as st
import tempfile
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Extracteur de Bulletins de Salaire",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("📋 Extracteur de Bulletins de Salaire")
st.markdown("*Uploadez vos bulletins PDF pour extraire automatiquement les données importantes*")

# Barre latérale
st.sidebar.title("⚙️ Configuration")

# Importer les modules locaux seulement quand nécessaire
@st.cache_resource
def load_processor():
    """Charger le processeur avec cache"""
    try:
        # Import ici pour éviter les erreurs de chargement
        import sys
        import os
        sys.path.append('/Users/maximejulien/Documents/GitHub/doctr')
        
        from payslip_processor import PayslipProcessor
        processor = PayslipProcessor()
        return processor, None
    except Exception as e:
        return None, str(e)

def process_uploaded_file(uploaded_file, processor):
    """Traiter un fichier uploadé"""
    try:
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Traiter le fichier
        result = processor.process_single_payslip(tmp_path)
        
        # Nettoyer le fichier temporaire
        Path(tmp_path).unlink()
        
        return result, None
    
    except Exception as e:
        return None, str(e)

def main():
    """Interface principale"""
    
    # Charger le processeur
    processor, error = load_processor()
    
    if processor is None:
        st.error(f"❌ Erreur lors du chargement du processeur: {error}")
        st.info("💡 Assurez-vous que docTR est correctement installé")
        return
    
    # Configuration dans la barre latérale
    st.sidebar.success("✅ Processeur chargé avec succès!")
    
    max_file_size = st.sidebar.slider(
        "Taille max fichier (MB)", 
        min_value=1, 
        max_value=50, 
        value=10
    )
    
    show_raw_text = st.sidebar.checkbox("Afficher le texte brut extrait", value=False)
    
    # Zone d'upload principal
    st.subheader("📤 Upload de fichiers")
    
    # Instructions
    with st.expander("📖 Instructions d'utilisation"):
        st.markdown("""
        1. **Uploadez votre bulletin de salaire** au format PDF
        2. **Attendez le traitement** (peut prendre quelques secondes)
        3. **Consultez les résultats** extraits automatiquement
        4. **Téléchargez les données** au format JSON ou CSV
        
        **Formats supportés:** PDF uniquement
        **Taille max:** {max_file_size} MB
        """.format(max_file_size=max_file_size))
    
    # Upload de fichier avec gestion d'erreurs améliorée
    uploaded_files = st.file_uploader(
        "Choisissez vos bulletins PDF",
        type=['pdf'],
        accept_multiple_files=True,
        help=f"Taille maximum: {max_file_size}MB par fichier"
    )
    
    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} fichier(s) uploadé(s)")
        
        # Vérifier la taille des fichiers
        oversized_files = []
        for file in uploaded_files:
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            if file_size_mb > max_file_size:
                oversized_files.append((file.name, file_size_mb))
        
        if oversized_files:
            st.error("❌ Fichiers trop volumineux:")
            for name, size in oversized_files:
                st.write(f"  - {name}: {size:.1f}MB (max: {max_file_size}MB)")
            return
        
        # Traiter les fichiers
        if st.button("🚀 Traiter les bulletins", type="primary"):
            
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Traitement de {uploaded_file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Traiter le fichier
                result, error = process_uploaded_file(uploaded_file, processor)
                
                if result:
                    results.append(result)
                    st.success(f"✅ {uploaded_file.name} traité avec succès")
                else:
                    st.error(f"❌ Erreur avec {uploaded_file.name}: {error}")
            
            status_text.text("Traitement terminé!")
            
            if results:
                display_results(results, show_raw_text)
    
    # Section d'aide
    st.markdown("---")
    with st.expander("🆘 Aide et dépannage"):
        st.markdown("""
        **Erreurs communes:**
        
        - **Erreur 403:** Fichier trop volumineux ou problème de permissions
        - **Erreur de traitement:** Fichier PDF corrompu ou format non supporté
        - **Données manquantes:** Le bulletin n'est pas dans un format standard français
        
        **Solutions:**
        - Réduisez la taille du fichier PDF
        - Vérifiez que le PDF n'est pas protégé par mot de passe
        - Utilisez les scripts en ligne de commande pour les gros volumes
        """)

def display_results(results, show_raw_text=False):
    """Afficher les résultats"""
    st.subheader("📊 Résultats de l'extraction")
    
    # Onglets pour différentes vues
    tab1, tab2, tab3 = st.tabs(["📋 Résumé", "📄 Détails", "💾 Export"])
    
    with tab1:
        # Résumé en tableau
        summary_data = []
        for result in results:
            summary_data.append({
                'Fichier': result.get('file_name', 'Inconnu'),
                'Employé': result.get('employee_name', 'Inconnu'),
                'Période': result.get('period', 'Inconnue'),
                'Salaire Brut': result.get('gross_salary', 'Inconnu'),
                'Net Payé': result.get('net_paid', 'Inconnu'),
                'Date Paiement': result.get('payment_date', 'Inconnue')
            })
        
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
        
        # Statistiques
        if len(results) > 1:
            st.subheader("📈 Statistiques")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Bulletins traités", len(results))
            
            with col2:
                unique_employees = len(set(r.get('employee_name', '') for r in results))
                st.metric("Employés uniques", unique_employees)
            
            with col3:
                unique_periods = len(set(r.get('period', '') for r in results))
                st.metric("Périodes uniques", unique_periods)
    
    with tab2:
        # Détails par bulletin
        for i, result in enumerate(results):
            with st.expander(f"📄 {result.get('file_name', f'Bulletin {i+1}')}"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**👤 Informations Employé:**")
                    st.write(f"Nom: {result.get('employee_name', 'Inconnu')}")
                    st.write(f"Matricule: {result.get('matricule', 'Inconnu')}")
                    st.write(f"Poste: {result.get('job_title', 'Inconnu')}")
                    st.write(f"Date d'entrée: {result.get('start_date', 'Inconnue')}")
                    
                    st.write("**🏢 Informations Employeur:**")
                    st.write(f"Entreprise: {result.get('employer', 'Inconnue')}")
                    st.write(f"SIRET: {result.get('siret', 'Inconnu')}")
                
                with col2:
                    st.write("**💰 Informations Salariales:**")
                    st.write(f"Période: {result.get('period', 'Inconnue')}")
                    st.write(f"Salaire brut: {result.get('gross_salary', 'Inconnu')} €")
                    st.write(f"Net avant impôt: {result.get('net_before_tax', 'Inconnu')} €")
                    st.write(f"Net payé: {result.get('net_paid', 'Inconnu')} €")
                    st.write(f"Impôt sur le revenu: {result.get('income_tax', 'Inconnu')} €")
                    st.write(f"Date de paiement: {result.get('payment_date', 'Inconnue')}")
                
                if show_raw_text and result.get('raw_text'):
                    st.write("**📝 Texte brut extrait:**")
                    with st.expander("Voir le texte"):
                        st.text_area("", result['raw_text'], height=200, key=f"raw_text_{i}")
    
    with tab3:
        # Options d'export
        st.write("💾 **Télécharger les données:**")
        
        # Préparer les données pour l'export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export JSON
        json_data = json.dumps(results, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Télécharger JSON",
            data=json_data,
            file_name=f"bulletins_extraits_{timestamp}.json",
            mime="application/json"
        )
        
        # Export CSV
        if results:
            # Exclure le texte brut pour le CSV
            csv_data = [{k: v for k, v in result.items() if k != 'raw_text'} for result in results]
            df_export = pd.DataFrame(csv_data)
            csv_string = df_export.to_csv(index=False)
            
            st.download_button(
                label="📊 Télécharger CSV",
                data=csv_string,
                file_name=f"bulletins_extraits_{timestamp}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
