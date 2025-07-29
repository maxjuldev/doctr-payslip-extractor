#!/usr/bin/env python3
"""
Système d'apprentissage automatique pour l'extracteur de bulletins de salaire
Permet à l'application d'apprendre et de s'améliorer automatiquement
"""

import json
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import difflib
from dataclasses import dataclass, asdict

@dataclass
class LearningEntry:
    """Structure pour une entrée d'apprentissage"""
    field_name: str
    pdf_filename: str
    original_value: str
    corrected_value: str
    pattern_found: str
    new_pattern: str
    confidence: float
    timestamp: str
    user_feedback: str = ""

@dataclass
class PatternRule:
    """Règle de pattern pour extraction"""
    field_name: str
    pattern: str
    priority: int
    success_rate: float
    usage_count: int
    last_used: str

class PayslipLearningSystem:
    """Système d'apprentissage pour l'extraction de bulletins"""
    
    def __init__(self):
        self.learning_db_path = "/Users/maximejulien/Documents/GitHub/doctr/learning_database.json"
        self.patterns_db_path = "/Users/maximejulien/Documents/GitHub/doctr/patterns_database.json"
        self.corrections_log_path = "/Users/maximejulien/Documents/GitHub/doctr/corrections_log.json"
        
        self.learning_entries = self._load_learning_database()
        self.pattern_rules = self._load_patterns_database()
        self.corrections_log = self._load_corrections_log()
    
    def _load_learning_database(self) -> List[LearningEntry]:
        """Charger la base de données d'apprentissage"""
        if Path(self.learning_db_path).exists():
            with open(self.learning_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [LearningEntry(**entry) for entry in data]
        return []
    
    def _load_patterns_database(self) -> List[PatternRule]:
        """Charger la base de données des patterns"""
        if Path(self.patterns_db_path).exists():
            with open(self.patterns_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [PatternRule(**pattern) for pattern in data]
        return self._initialize_default_patterns()
    
    def _load_corrections_log(self) -> List[Dict]:
        """Charger le log des corrections"""
        if Path(self.corrections_log_path).exists():
            with open(self.corrections_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _initialize_default_patterns(self) -> List[PatternRule]:
        """Initialiser les patterns par défaut"""
        default_patterns = [
            # Employeur
            PatternRule("company_name", r'(?:^|\n)([A-ZÀ-Ÿ\s&]+)\n[0-9]+', 1, 0.8, 0, ""),
            PatternRule("siret", r'Siret\s*:?\s*([0-9]+)', 1, 0.9, 0, ""),
            PatternRule("naf_code", r'Code\s*Naf\s*:?\s*([0-9A-Z]+)', 1, 0.9, 0, ""),
            
            # Employé
            PatternRule("full_name", r'(?:Madame|Monsieur|M\.|Mme)\s+([A-ZÀ-Ÿ\s]+)', 1, 0.8, 0, ""),
            PatternRule("matricule", r'Matricule\s*:?\s*([0-9]+)', 1, 0.9, 0, ""),
            PatternRule("social_security", r'No\s*SS\s*:?\s*([0-9]+)', 1, 0.9, 0, ""),
            
            # Salaire
            PatternRule("gross_salary", r'Salaire\s+brut\s+([0-9\s,]+\.?[0-9]*)', 1, 0.8, 0, ""),
            PatternRule("net_paid", r'Net\s+payé?\s+([0-9\s,]+\.?[0-9]*)', 1, 0.8, 0, ""),
            
            # Dates
            PatternRule("start_date", r'Entrée\s*:?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})', 1, 0.9, 0, ""),
            PatternRule("payment_date", r'Paiement\s+le\s+([0-9]{2}/[0-9]{2}/[0-9]{4})', 1, 0.9, 0, ""),
        ]
        return default_patterns
    
    def learn_from_correction(self, field_name: str, pdf_filename: str, 
                            original_value: str, corrected_value: str, 
                            raw_text: str, user_feedback: str = ""):
        """Apprendre d'une correction utilisateur"""
        print(f"📚 Apprentissage : {field_name} = '{corrected_value}'")
        
        # Trouver le pattern actuel
        current_pattern = self._find_current_pattern(field_name)
        
        # Générer un nouveau pattern basé sur la correction
        new_pattern = self._generate_pattern_from_correction(
            field_name, corrected_value, raw_text
        )
        
        # Calculer la confiance
        confidence = self._calculate_confidence(corrected_value, raw_text, new_pattern)
        
        # Créer l'entrée d'apprentissage
        learning_entry = LearningEntry(
            field_name=field_name,
            pdf_filename=pdf_filename,
            original_value=original_value,
            corrected_value=corrected_value,
            pattern_found=current_pattern,
            new_pattern=new_pattern,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            user_feedback=user_feedback
        )
        
        self.learning_entries.append(learning_entry)
        
        # Mettre à jour les patterns
        self._update_patterns(learning_entry)
        
        # Sauvegarder
        self._save_learning_database()
        self._save_patterns_database()
        
        # Logger la correction
        self._log_correction(learning_entry)
        
        print(f"✅ Apprentissage terminé. Nouveau pattern : {new_pattern}")
        print(f"🎯 Confiance : {confidence:.2f}")
    
    def _find_current_pattern(self, field_name: str) -> str:
        """Trouver le pattern actuellement utilisé pour un champ"""
        for pattern_rule in self.pattern_rules:
            if pattern_rule.field_name == field_name:
                return pattern_rule.pattern
        return ""
    
    def _generate_pattern_from_correction(self, field_name: str, 
                                        corrected_value: str, raw_text: str) -> str:
        """Générer un nouveau pattern basé sur la correction"""
        # Normaliser la valeur corrigée pour la recherche
        search_value = re.escape(corrected_value.strip())
        
        # Chercher le contexte autour de la valeur dans le texte
        lines = raw_text.split('\n')
        context_patterns = []
        
        for i, line in enumerate(lines):
            if corrected_value.strip() in line:
                # Analyser le contexte avant et après
                before_context = ""
                after_context = ""
                
                # Contexte de la ligne précédente
                if i > 0:
                    before_context = lines[i-1].strip()
                
                # Contexte de la ligne suivante
                if i < len(lines) - 1:
                    after_context = lines[i+1].strip()
                
                # Générer des patterns basés sur le contexte
                patterns = self._create_context_patterns(
                    field_name, corrected_value, line, before_context, after_context
                )
                context_patterns.extend(patterns)
        
        # Retourner le pattern le plus spécifique
        if context_patterns:
            return max(context_patterns, key=len)  # Le plus spécifique
        
        # Pattern de fallback
        return rf'{re.escape(corrected_value)}'
    
    def _create_context_patterns(self, field_name: str, value: str, 
                               current_line: str, before_line: str, after_line: str) -> List[str]:
        """Créer des patterns basés sur le contexte"""
        patterns = []
        escaped_value = re.escape(value)
        
        # Patterns basés sur les mots-clés courants
        field_keywords = {
            'company_name': ['CENTRE', 'SOCIETE', 'ENTREPRISE', 'SAS', 'SARL'],
            'siret': ['Siret', 'SIRET'],
            'naf_code': ['Naf', 'NAF', 'Code'],
            'matricule': ['Matricule', 'MATRICULE'],
            'social_security': ['SS', 'Sécurité', 'sociale'],
            'gross_salary': ['brut', 'BRUT', 'Salaire'],
            'net_paid': ['Net', 'NET', 'payé'],
            'start_date': ['Entrée', 'ENTREE', 'début'],
            'payment_date': ['Paiement', 'PAIEMENT', 'versé']
        }
        
        keywords = field_keywords.get(field_name, [])
        
        # Pattern 1: Mot-clé suivi de la valeur
        for keyword in keywords:
            if keyword.lower() in current_line.lower():
                pattern = rf'{keyword}\s*:?\s*([^\\n]*{escaped_value}[^\\n]*)'
                patterns.append(pattern)
        
        # Pattern 2: Valeur après deux-points ou égal
        if ':' in current_line or '=' in current_line:
            pattern = rf'[^\\n]*[:=]\s*([^\\n]*{escaped_value}[^\\n]*)'
            patterns.append(pattern)
        
        # Pattern 3: Valeur seule sur une ligne
        if current_line.strip() == value.strip():
            if before_line:
                # Utiliser la ligne précédente comme contexte
                pattern = rf'{re.escape(before_line)}\\n({escaped_value})'
                patterns.append(pattern)
        
        # Pattern 4: Valeur avec chiffres (pour montants, dates, etc.)
        if re.search(r'\d', value):
            pattern = rf'([0-9\s,]+\.?[0-9]*{escaped_value}[0-9\s,]*\.?[0-9]*)'
            patterns.append(pattern)
        
        return patterns
    
    def _calculate_confidence(self, value: str, text: str, pattern: str) -> float:
        """Calculer la confiance du pattern"""
        try:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Plus il y a de correspondances exactes, plus la confiance est élevée
                exact_matches = [m for m in matches if value in str(m)]
                confidence = len(exact_matches) / len(matches)
                return min(confidence, 1.0)
            return 0.0
        except:
            return 0.0
    
    def _update_patterns(self, learning_entry: LearningEntry):
        """Mettre à jour la base de patterns"""
        # Chercher le pattern existant
        existing_pattern = None
        for i, pattern_rule in enumerate(self.pattern_rules):
            if pattern_rule.field_name == learning_entry.field_name:
                existing_pattern = pattern_rule
                break
        
        if existing_pattern:
            # Mettre à jour le pattern existant si le nouveau est meilleur
            if learning_entry.confidence > existing_pattern.success_rate:
                existing_pattern.pattern = learning_entry.new_pattern
                existing_pattern.success_rate = learning_entry.confidence
                existing_pattern.priority += 1
                existing_pattern.last_used = learning_entry.timestamp
            existing_pattern.usage_count += 1
        else:
            # Créer un nouveau pattern
            new_pattern = PatternRule(
                field_name=learning_entry.field_name,
                pattern=learning_entry.new_pattern,
                priority=1,
                success_rate=learning_entry.confidence,
                usage_count=1,
                last_used=learning_entry.timestamp
            )
            self.pattern_rules.append(new_pattern)
    
    def _log_correction(self, learning_entry: LearningEntry):
        """Logger une correction"""
        correction_log = {
            'timestamp': learning_entry.timestamp,
            'field': learning_entry.field_name,
            'pdf': learning_entry.pdf_filename,
            'original': learning_entry.original_value,
            'corrected': learning_entry.corrected_value,
            'confidence': learning_entry.confidence,
            'user_feedback': learning_entry.user_feedback
        }
        
        self.corrections_log.append(correction_log)
        
        # Sauvegarder le log
        with open(self.corrections_log_path, 'w', encoding='utf-8') as f:
            json.dump(self.corrections_log, f, indent=2, ensure_ascii=False)
    
    def get_best_pattern(self, field_name: str) -> str:
        """Obtenir le meilleur pattern pour un champ"""
        field_patterns = [p for p in self.pattern_rules if p.field_name == field_name]
        if field_patterns:
            # Trier par taux de succès et priorité
            best_pattern = max(field_patterns, 
                             key=lambda p: (p.success_rate, p.priority, p.usage_count))
            return best_pattern.pattern
        return ""
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques d'apprentissage"""
        total_corrections = len(self.learning_entries)
        fields_learned = len(set(entry.field_name for entry in self.learning_entries))
        avg_confidence = sum(entry.confidence for entry in self.learning_entries) / max(total_corrections, 1)
        
        field_stats = {}
        for entry in self.learning_entries:
            field = entry.field_name
            if field not in field_stats:
                field_stats[field] = {'count': 0, 'avg_confidence': 0}
            field_stats[field]['count'] += 1
            field_stats[field]['avg_confidence'] += entry.confidence
        
        # Calculer les moyennes
        for field in field_stats:
            field_stats[field]['avg_confidence'] /= field_stats[field]['count']
        
        return {
            'total_corrections': total_corrections,
            'fields_learned': fields_learned,
            'average_confidence': avg_confidence,
            'field_statistics': field_stats,
            'total_patterns': len(self.pattern_rules),
            'last_learning': self.learning_entries[-1].timestamp if self.learning_entries else None
        }
    
    def suggest_improvements(self) -> List[str]:
        """Suggérer des améliorations"""
        suggestions = []
        
        # Analyser les patterns avec faible confiance
        low_confidence_patterns = [p for p in self.pattern_rules if p.success_rate < 0.5]
        if low_confidence_patterns:
            suggestions.append(f"🔍 {len(low_confidence_patterns)} patterns ont une faible confiance et nécessitent plus d'apprentissage")
        
        # Analyser les champs jamais corrigés
        corrected_fields = set(entry.field_name for entry in self.learning_entries)
        all_fields = set(p.field_name for p in self.pattern_rules)
        uncorrected_fields = all_fields - corrected_fields
        if uncorrected_fields:
            suggestions.append(f"📝 {len(uncorrected_fields)} champs n'ont jamais été corrigés : {', '.join(uncorrected_fields)}")
        
        # Analyser les corrections récentes
        if len(self.learning_entries) > 0:
            recent_corrections = [e for e in self.learning_entries 
                                if (datetime.now() - datetime.fromisoformat(e.timestamp)).days <= 7]
            if len(recent_corrections) > 5:
                suggestions.append(f"🚀 {len(recent_corrections)} corrections cette semaine. Le système s'améliore rapidement!")
        
        return suggestions
    
    def _save_learning_database(self):
        """Sauvegarder la base d'apprentissage"""
        data = [asdict(entry) for entry in self.learning_entries]
        with open(self.learning_db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_patterns_database(self):
        """Sauvegarder la base de patterns"""
        data = [asdict(pattern) for pattern in self.pattern_rules]
        with open(self.patterns_db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_learned_patterns(self, output_path: str):
        """Exporter les patterns appris"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_learning_stats(),
            'patterns': [asdict(p) for p in self.pattern_rules],
            'recent_corrections': [asdict(e) for e in self.learning_entries[-10:]],
            'suggestions': self.suggest_improvements()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Patterns exportés vers : {output_path}")


def main():
    """Test du système d'apprentissage"""
    learning_system = PayslipLearningSystem()
    
    print("🎓 SYSTÈME D'APPRENTISSAGE DOCTR - TEST")
    print("=" * 50)
    
    # Simuler quelques apprentissages
    raw_text_sample = """
    CENTRE DE SANTE SANTOS DUMONT
    276277025
    RUE SANTOS DUMONT
    BULLETIN DE SALAIRE
    27930 GUICHAINVILLE
    Siret 87903653100017 Code Naf: 8690F
    Matricule: 00027
    No SS: 291069720980802
    Madame MORGAN MICHALET
    Salaire brut 10224.00
    Net payé 7142.72
    """
    
    # Apprendre des corrections
    learning_system.learn_from_correction(
        "company_name", 
        "test_bulletin.pdf",
        "CENTRE DE SANTE SANTOS DUMONT276277025",
        "CENTRE DE SANTE SANTOS DUMONT",
        raw_text_sample,
        "Le nom de l'entreprise était mal extrait avec le numéro"
    )
    
    # Afficher les statistiques
    stats = learning_system.get_learning_stats()
    print("\n📊 STATISTIQUES D'APPRENTISSAGE:")
    print(f"Total corrections: {stats['total_corrections']}")
    print(f"Champs appris: {stats['fields_learned']}")
    print(f"Confiance moyenne: {stats['average_confidence']:.2f}")
    
    # Afficher les suggestions
    suggestions = learning_system.suggest_improvements()
    print("\n💡 SUGGESTIONS D'AMÉLIORATION:")
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    # Exporter les patterns
    learning_system.export_learned_patterns("/Users/maximejulien/Documents/GitHub/doctr/learned_patterns_export.json")


if __name__ == "__main__":
    main()
