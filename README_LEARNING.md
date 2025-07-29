# 🎓 Système d'Apprentissage DocTR

## 📋 Vue d'ensemble

Le système d'apprentissage DocTR permet à l'application d'**apprendre automatiquement** comment mieux extraire les informations des bulletins de salaire en se basant sur vos corrections.

## 🚀 Fonctionnalités

### ✨ **Apprentissage Automatique**
- 🎯 **Correction assistée** : Corrigez facilement les erreurs d'extraction
- 🧠 **Amélioration continue** : L'application apprend de chaque correction
- 📊 **Patterns dynamiques** : Création automatique de nouveaux patterns
- 📈 **Statistiques en temps réel** : Suivi des performances

### 🔧 **Outils de Gestion**
- 📚 **Base de données d'apprentissage** : Historique de toutes les corrections
- 🎯 **Gestion des patterns** : Visualisation et modification des règles
- 📊 **Analytics avancées** : Métriques de performance détaillées
- 💡 **Suggestions intelligentes** : Recommandations d'amélioration

## 🛠️ Installation et Utilisation

### 1. **Démarrage Rapide**

```bash
# Lancer l'interface d'apprentissage
streamlit run streamlit_learning_interface.py

# Ou tester le système
python demo_learning.py
```

### 2. **Interface Web Interactive**

L'interface Streamlit propose 3 modes :

#### 🔍 **Mode Extraction et Correction**
- Téléchargez un PDF de bulletin
- Visualisez les données extraites
- Corrigez les erreurs facilement
- L'application apprend automatiquement

#### 📊 **Mode Statistiques**
- Métriques de performance
- Graphiques de progression
- Suggestions d'amélioration
- Export des données

#### ⚙️ **Mode Gestion des Patterns**
- Visualisation des règles actives
- Nettoyage des patterns faibles
- Réinitialisation si nécessaire

### 3. **Intégration dans l'Extracteur**

```python
from advanced_extractor import AdvancedPayslipExtractor
from learning_system import PayslipLearningSystem

# Créer l'extracteur avec apprentissage
extractor = AdvancedPayslipExtractor(use_learning=True)

# Extraire les données
data = extractor.extract_all_data("bulletin.pdf")

# Apprendre d'une correction
learning_system = PayslipLearningSystem()
learning_system.learn_from_correction(
    field_name="company_name",
    pdf_filename="bulletin.pdf", 
    original_value="ENTREPRISE ABC123",
    corrected_value="ENTREPRISE ABC",
    raw_text=data['raw_text'],
    user_feedback="Suppression du numéro à la fin"
)
```

## 📁 Structure des Fichiers

```
doctr/
├── learning_system.py              # 🧠 Système d'apprentissage principal
├── streamlit_learning_interface.py # 🖥️ Interface web interactive
├── demo_learning.py               # 🎮 Démonstration du système
├── advanced_extractor.py          # 🔍 Extracteur avec apprentissage
├── learning_database.json         # 📚 Base des corrections
├── patterns_database.json         # 🎯 Base des patterns
└── corrections_log.json           # 📋 Log des corrections
```

## 🎯 Comment Utiliser l'Apprentissage

### **Étape 1 : Extraire un bulletin**
```python
# L'extracteur utilise automatiquement les patterns appris
extractor = AdvancedPayslipExtractor(use_learning=True)
data = extractor.extract_all_data("bulletin.pdf")
```

### **Étape 2 : Identifier les erreurs**
- Vérifiez les données extraites
- Notez les champs incorrects ou manquants

### **Étape 3 : Effectuer les corrections**
```python
learning_system = PayslipLearningSystem()

# Pour chaque erreur trouvée
learning_system.learn_from_correction(
    field_name="nom_du_champ",
    pdf_filename="nom_fichier.pdf",
    original_value="valeur_extraite_incorrecte", 
    corrected_value="valeur_correcte",
    raw_text=texte_brut_du_pdf,
    user_feedback="Explication optionnelle"
)
```

### **Étape 4 : Réextraire avec les améliorations**
```python
# Le nouvel extracteur utilisera les patterns améliorés
improved_extractor = AdvancedPayslipExtractor(use_learning=True)
improved_data = improved_extractor.extract_all_data("bulletin.pdf")
```

## 📊 Métriques et Statistiques

### **Métriques Principales**
- 📈 **Taux de réussite** : Pourcentage de champs correctement extraits
- 🎯 **Confiance moyenne** : Fiabilité des patterns utilisés  
- 📚 **Nombre de corrections** : Total des apprentissages effectués
- 🔄 **Fréquence d'utilisation** : Patterns les plus sollicités

### **Analyses Avancées**
- 📊 **Performance par champ** : Quels champs nécessitent le plus de corrections
- 🎯 **Évolution temporelle** : Amélioration de la précision dans le temps
- 💡 **Suggestions d'optimisation** : Recommandations automatiques

## 🎮 Exemples d'Utilisation

### **Exemple 1 : Correction Simple**
```python
# Correction d'un nom d'entreprise mal extrait
learning_system.learn_from_correction(
    field_name="company_name",
    pdf_filename="bulletin_mars_2024.pdf",
    original_value="CENTRE MEDICAL SANTOS DUMONT76543",
    corrected_value="CENTRE MEDICAL SANTOS DUMONT", 
    raw_text=texte_complet,
    user_feedback="Suppression du code numérique à la fin"
)
```

### **Exemple 2 : Nouveau Pattern**
```python
# Apprendre un nouveau format de numéro SIRET
learning_system.learn_from_correction(
    field_name="siret",
    pdf_filename="nouveau_format.pdf", 
    original_value="",  # Non détecté initialement
    corrected_value="12345678901234",
    raw_text=texte_complet,
    user_feedback="SIRET au format XXXXX XXX XXX XXXX"
)
```

### **Exemple 3 : Utilisation Interface Web**
1. Lancez : `streamlit run streamlit_learning_interface.py`
2. Téléchargez votre PDF
3. Cliquez "Extraire les données"
4. Corrigez les champs incorrects
5. Cliquez "Enregistrer les Corrections et Apprendre"
6. 🎉 L'application s'améliore automatiquement !

## 🔧 Configuration Avancée

### **Patterns Personnalisés**
```python
# Ajouter un pattern manuel
learning_system = PayslipLearningSystem()
new_pattern = PatternRule(
    field_name="custom_field",
    pattern=r"Pattern_RegEx_Personnalisé",
    priority=1,
    success_rate=0.9,
    usage_count=0,
    last_used=""
)
learning_system.pattern_rules.append(new_pattern)
learning_system._save_patterns_database()
```

### **Export/Import des Données**
```python
# Exporter les patterns appris
learning_system.export_learned_patterns("backup_patterns.json")

# Les fichiers sont automatiquement sauvegardés dans :
# - learning_database.json  (apprentissage)
# - patterns_database.json  (patterns)  
# - corrections_log.json    (historique)
```

## 🎯 Conseils d'Optimisation

### **Pour une Meilleure Précision :**
1. **Corrigez régulièrement** : Plus vous corrigez, mieux le système apprend
2. **Soyez spécifique** : Ajoutez des commentaires lors des corrections
3. **Testez différents formats** : Utilisez des bulletins variés
4. **Surveillez les statistiques** : Identifiez les champs problématiques

### **Maintenance Recommandée :**
- 🧹 **Nettoyage mensuel** : Supprimez les patterns avec faible confiance
- 📊 **Analyse hebdomadaire** : Vérifiez les métriques de performance  
- 🔄 **Sauvegarde régulière** : Exportez vos patterns appris
- 🎯 **Tests de régression** : Validez sur des bulletins déjà traités

## 🚨 Dépannage

### **Problèmes Courants**

**❌ "Système d'apprentissage non disponible"**
```bash
# Vérifiez que tous les fichiers sont présents
ls learning_system.py streamlit_learning_interface.py
```

**❌ "Pattern appris échoué"**
- Les patterns complexes peuvent parfois échouer
- Le système utilise automatiquement le pattern de fallback
- Corrigez à nouveau pour améliorer le pattern

**❌ "Aucune amélioration détectée"**
- Normal si les données étaient déjà correctes
- Le système apprend quand même pour confirmer les patterns

### **Réinitialisation Complète**
```python
# Supprimer toutes les données d'apprentissage
import os
os.remove("learning_database.json")
os.remove("patterns_database.json") 
os.remove("corrections_log.json")

# Ou via l'interface web : Mode "Gestion des Patterns" > "Réinitialiser"
```

## 🎉 Conclusion

Le système d'apprentissage DocTR transforme votre extracteur en **assistant intelligent** qui s'améliore continuellement. Plus vous l'utilisez, plus il devient précis !

**Prochaines étapes :**
1. 🚀 Lancez la démonstration : `python demo_learning.py`
2. 🖥️ Essayez l'interface web : `streamlit run streamlit_learning_interface.py` 
3. 📚 Commencez à corriger vos premiers bulletins
4. 📊 Observez les améliorations dans les statistiques

**Bon apprentissage ! 🎓**
