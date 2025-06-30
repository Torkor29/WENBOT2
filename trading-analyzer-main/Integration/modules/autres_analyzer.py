import pandas as pd
import os
import re
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import LineChart, Reference, PieChart, BarChart
from datetime import datetime
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import numpy as np

class AutresAnalyzer:
    def __init__(self):
        """Initialisation de l'analyseur pour autres instruments"""
        pass
    
    def process_files(self, file_paths, task_id=None, task_status=None):
        """Traite les fichiers Excel et retourne les résultats"""
        try:
            # Mise à jour du statut
            if task_status and task_id:
                task_status[task_id].update({
                    'progress': 20,
                    'message': 'Lecture des fichiers...'
                })
            
            # Lecture des fichiers
            dfs = []
            for file_path in file_paths:
                df = pd.read_excel(file_path)
                dfs.append(df)
            
            if task_status and task_id:
                task_status[task_id].update({
                    'progress': 40,
                    'message': 'Analyse des données...'
                })
            
            # Exemple simple d'analyse
            df = pd.concat(dfs)
            df['Profit'] = df['Profit'].astype(float)
            df['Solde_cumule'] = 10000 + df['Profit'].cumsum()
            
            # Calcul du drawdown
            df['Peak'] = df['Solde_cumule'].cummax()
            df['Drawdown'] = df['Peak'] - df['Solde_cumule']
            df['Drawdown_pct'] = (df['Drawdown'] / df['Peak']) * 100
            
            if task_status and task_id:
                task_status[task_id].update({
                    'progress': 80,
                    'message': 'Finalisation de l\'analyse...'
                })
            
            return df
            
        except Exception as e:
            if task_status and task_id:
                task_status[task_id].update({
                    'status': 'error',
                    'error': str(e)
                })
            raise e
    
    def create_excel_report(self, df, reports_folder, timestamp):
        """Crée un rapport Excel avec les résultats"""
        # Créer le nom du fichier
        report_filename = os.path.join(reports_folder, f'rapport_autres_{timestamp}.xlsx')
        
        # Sauvegarder en Excel
        with pd.ExcelWriter(report_filename) as writer:
            df.to_excel(writer, sheet_name='Trades', index=False)
            
            # Créer un résumé
            summary = pd.DataFrame({
                'Métrique': [
                    'Nombre total de trades',
                    'Trades gagnants',
                    'Trades perdants',
                    'Taux de réussite',
                    'Profit total',
                    'Rendement',
                    'Drawdown maximum'
                ],
                'Valeur': [
                    len(df),
                    len(df[df['Profit'] > 0]),
                    len(df[df['Profit'] < 0]),
                    f"{(len(df[df['Profit'] > 0]) / len(df) * 100):.1f}%",
                    f"{df['Profit'].sum():.2f}€",
                    f"{((df['Solde_cumule'].iloc[-1] - 10000) / 10000 * 100):.1f}%",
                    f"{df['Drawdown_pct'].max():.1f}%"
                ]
            })
            summary.to_excel(writer, sheet_name='Résumé', index=False)
        
        return report_filename 