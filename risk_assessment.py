import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

class RiskAssessment:
    def _init_(self, fema_df, merged_df):
        self.fema_df = fema_df
        self.merged_df = merged_df

    def get_disaster_history(self, state, city, years=5):
        try:
            disasters = self.fema_df[
                (self.fema_df['STATE'].str.upper() == state.upper())
            ].copy()
            
            disasters['declarationdate'] = pd.to_datetime(disasters['declarationdate'], errors='coerce')
            cutoff_date = datetime.now() - pd.DateOffset(years=years)
            recent_disasters = disasters[disasters['declarationdate'] >= cutoff_date]
            
            disaster_categories = recent_disasters['incidenttype'].value_counts().to_dict()
            disaster_timeline = recent_disasters[['declarationdate', 'incidenttype']].sort_values('declarationdate')
            
            return {
                'total_disasters': len(recent_disasters),
                'disaster_types': disaster_categories,
                'timeline': disaster_timeline,
                'most_frequent': list(disaster_categories.keys())[0] if disaster_categories else None
            }
        except Exception as e:
            print(f"Error getting disaster history: {str(e)}")
            return {
                'total_disasters': 0,
                'disaster_types': {},
                'timeline': pd.DataFrame(),
                'most_frequent': None
            }

    def get_climate_risk_score(self, state, city):
        try:
            disaster_data = self.get_disaster_history(state, city)
            climate_data = self._get_simulated_climate_data(state)
            
            disaster_score = min(disaster_data['total_disasters'] * 5, 100)
            climate_score = self._calculate_climate_severity_score(climate_data)
            vulnerability_score = self._calculate_vulnerability_score(state, city)
            
            overall_score = (0.4 * disaster_score) + (0.3 * climate_score) + (0.3 * vulnerability_score)
            
            return {
                'overall_score': round(overall_score, 1),
                'disaster_score': round(disaster_score, 1),
                'climate_score': round(climate_score, 1),
                'vulnerability_score': round(vulnerability_score, 1),
                'recommendation': self._get_risk_recommendation(overall_score)
            }
        except Exception as e:
            print(f"Error calculating risk score: {str(e)}")
            return {
                'overall_score': 0,
                'disaster_score': 0,
                'climate_score': 0,
                'vulnerability_score': 0,
                'recommendation': {'level': 'ERROR', 'action': 'Error', 'description': 'Calculation failed'}
            }

    def _get_simulated_climate_data(self, state):
        coastal_states = ['FL', 'LA', 'TX', 'CA', 'NY', 'NC', 'SC', 'GA', 'ME', 'VA']
        southern_states = ['FL', 'GA', 'SC', 'NC', 'VA', 'TX', 'LA', 'MS', 'AL', 'AR', 'OK', 'TN', 'KY']
        
        return {
            'avg_temp_max': 38 if state in southern_states else 30,
            'avg_temp_min': 10 if state in southern_states else -5,
            'total_precipitation': 1600 if state in coastal_states else 800,
            'drought_risk': 0.3 if state in southern_states else 0.1
        }

    def _calculate_climate_severity_score(self, climate_data):
        score = 0
        if climate_data.get('avg_temp_max', 0) > 35: score += 30
        if climate_data.get('avg_temp_min', 0) < 0: score += 20
        if climate_data.get('total_precipitation', 0) > 1500: score += 25
        if climate_data.get('drought_risk', 0) > 0.5: score += 25
        return min(score, 100)

    def _calculate_vulnerability_score(self, state, city):
        score = 0
        coastal_states = ['FL', 'LA', 'TX', 'CA', 'NY', 'NC', 'SC', 'GA', 'ME', 'VA']
        if state in coastal_states: score += 40
        
        flood_keywords = ['river', 'delta', 'bay', 'port', 'coast']
        if any(kw in city.lower() for kw in flood_keywords): score += 30
        
        return min(score + np.random.randint(0, 30), 100)

    def _get_risk_recommendation(self, score):
        if score < 30:
            return {'level': 'LOW', 'action': 'Invest', 'description': 'Low risk area', 'color': '#059669'}
        elif score < 60:
            return {'level': 'MODERATE', 'action': 'Invest with Caution', 'description': 'Moderate risk', 'color': '#f59e0b'}
        else:
            return {'level': 'HIGH', 'action': 'Wait', 'description': 'High risk area', 'color': '#dc2626'}

    def create_risk_visualization(self, risk_data):
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[
                    risk_data['climate_score'],
                    risk_data['disaster_score'],
                    risk_data['vulnerability_score']
                ],
                theta=['Climate Risk', 'Disaster Risk', 'Vulnerability'],
                fill='toself',
                name='Risk Profile',
                line_color='#2563eb',
                fillcolor='rgba(37, 99, 235, 0.2)'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%')
                ),
                title=f'Risk Profile (Score: {risk_data["overall_score"]}%)',
                height=400
            )
            return fig
        except Exception as e:
            print(f"Error creating visualization: {str(e)}")
            return go.Figure()