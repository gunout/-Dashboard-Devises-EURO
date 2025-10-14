# dashboard_euro_forex.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Devises Euro - Marché des Changes",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(45deg, #003399, #0055A4, #0077CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        padding: 1rem;
    }
    .currency-card {
        background: linear-gradient(135deg, #003399, #0055A4);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .currency-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .currency-change {
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .positive { background-color: rgba(40, 167, 69, 0.2); color: #28a745; border: 2px solid #28a745; }
    .negative { background-color: rgba(220, 53, 69, 0.2); color: #dc3545; border: 2px solid #dc3545; }
    .neutral { background-color: rgba(108, 117, 125, 0.2); color: #6c757d; border: 2px solid #6c757d; }
    .section-header {
        color: #003399;
        border-bottom: 3px solid #FFCC00;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        font-size: 1.8rem;
    }
    .currency-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .simulator-card {
        background: linear-gradient(135deg, #003399, #0055A4);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .profit-loss-positive {
        background-color: rgba(40, 167, 69, 0.2);
        color: #28a745;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
    }
    .profit-loss-negative {
        background-color: rgba(220, 53, 69, 0.2);
        color: #dc3545;
        border: 2px solid #dc3545;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class EuroForexDashboard:
    def __init__(self):
        self.currencies = self.define_currencies()
        self.historical_data = self.initialize_historical_data()
        self.current_data = self.initialize_current_data()
        
    def define_currencies(self):
        """Définit les paires de devises majeures avec l'Euro"""
        return {
            'EUR/USD': {
                'nom': 'Euro / Dollar Américain',
                'symbole': 'EUR/USD',
                'icone': '🇪🇺🇺🇸',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 1.0850,
                'volatilite': 1.2,
                'volume_journalier': 750.0,
                'pays': ['Zone Euro', 'États-Unis'],
                'banque_centrale': ['BCE', 'Fed'],
                'description': 'La paire de devises la plus échangée au monde'
            },
            'EUR/GBP': {
                'nom': 'Euro / Livre Sterling',
                'symbole': 'EUR/GBP',
                'icone': '🇪🇺🇬🇧',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 0.8520,
                'volatilite': 1.3,
                'volume_journalier': 100.0,
                'pays': ['Zone Euro', 'Royaume-Uni'],
                'banque_centrale': ['BCE', 'BoE'],
                'description': 'Paire croisée importante'
            },
            'EUR/JPY': {
                'nom': 'Euro / Yen Japonais',
                'symbole': 'EUR/JPY',
                'icone': '🇪🇺🇯🇵',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 168.50,
                'volatilite': 1.5,
                'volume_journalier': 120.0,
                'pays': ['Zone Euro', 'Japon'],
                'banque_centrale': ['BCE', 'BoJ'],
                'description': 'Très liquide'
            },
            'EUR/CHF': {
                'nom': 'Euro / Franc Suisse',
                'symbole': 'EUR/CHF',
                'icone': '🇪🇺🇨🇭',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 0.9820,
                'volatilite': 1.2,
                'volume_journalier': 60.0,
                'pays': ['Zone Euro', 'Suisse'],
                'banque_centrale': ['BCE', 'SNB'],
                'description': 'Considérée comme stable'
            },
            'EUR/AUD': {
                'nom': 'Euro / Dollar Australien',
                'symbole': 'EUR/AUD',
                'icone': '🇪🇺🇦🇺',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 1.6320,
                'volatilite': 1.6,
                'volume_journalier': 50.0,
                'pays': ['Zone Euro', 'Australie'],
                'banque_centrale': ['BCE', 'RBA'],
                'description': 'Influencée par les matières premières'
            },
            'EUR/CAD': {
                'nom': 'Euro / Dollar Canadien',
                'symbole': 'EUR/CAD',
                'icone': '🇪🇺🇨🇦',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 1.4820,
                'volatilite': 1.5,
                'volume_journalier': 45.0,
                'pays': ['Zone Euro', 'Canada'],
                'banque_centrale': ['BCE', 'BoC'],
                'description': 'Paire croisée importante'
            }
        }
    
    def initialize_historical_data(self):
        """Initialise les données historiques des devises"""
        dates = pd.date_range('2020-01-01', datetime.now(), freq='D')
        data = []
        
        for date in dates:
            for symbole, info in self.currencies.items():
                base_price = info['prix_base']
                global_impact = 1.0
                
                # Simulation d'impact d'événements
                if date.year == 2020 and date.month <= 6:
                    global_impact *= random.uniform(0.9, 1.1)
                elif date.year == 2021:
                    global_impact *= random.uniform(1.05, 1.15)
                elif date.year >= 2023:
                    global_impact *= random.uniform(0.98, 1.08)
                
                daily_volatility = random.normalvariate(1, info['volatilite']/100)
                seasonal = 1 + 0.003 * np.sin(2 * np.pi * date.dayofyear / 365)
                prix_actuel = base_price * global_impact * daily_volatility * seasonal
                
                data.append({
                    'date': date,
                    'symbole': symbole,
                    'nom': info['nom'],
                    'categorie': info['categorie'],
                    'prix': prix_actuel,
                    'volume': random.uniform(100000, 5000000),
                    'volatilite_jour': abs(daily_volatility - 1) * 100
                })
        
        return pd.DataFrame(data)
    
    def initialize_current_data(self):
        """Initialise les données courantes"""
        current_data = []
        for symbole, info in self.currencies.items():
            last_data = self.historical_data[self.historical_data['symbole'] == symbole].iloc[-1]
            change_pct = random.uniform(-2.0, 2.0)
            
            current_data.append({
                'symbole': symbole,
                'nom': info['nom'],
                'icone': info['icone'],
                'categorie': info['categorie'],
                'unite': info['unite'],
                'prix': last_data['prix'] * (1 + change_pct/100),
                'change_pct': change_pct,
                'volatilite': info['volatilite'],
                'volume_journalier': info['volume_journalier'],
                'pays': info['pays'],
                'banque_centrale': info['banque_centrale'],
                'spread': random.uniform(0.1, 2.0)
            })
        
        return pd.DataFrame(current_data)

    def update_live_data(self):
        """Met à jour les données en temps réel"""
        for idx in self.current_data.index:
            if random.random() < 0.6:
                variation = random.uniform(-1.0, 1.0)
                self.current_data.loc[idx, 'prix'] *= (1 + variation/100)
                self.current_data.loc[idx, 'change_pct'] = variation
                self.current_data.loc[idx, 'volume_journalier'] *= random.uniform(0.8, 1.2)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown(
            '<h1 class="main-header">💱 DASHBOARD DEVISES EURO</h1>', 
            unsafe_allow_html=True
        )
        
        st.markdown(
            '<div style="text-align: center; background: linear-gradient(45deg, #003399, #0055A4); '
            'color: white; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">'
            '<h3>🔴 SURVEILLANCE DES 6 PRINCIPALES PAIRES AVEC L\'EURO</h3>'
            '</div>', 
            unsafe_allow_html=True
        )
        
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_currency_cards(self):
        """Affiche les cartes de devises principales"""
        st.markdown('<h3 class="section-header">💰 TAUX DE CHANGE EN TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        # Afficher 3 devises par ligne
        for i in range(0, len(self.current_data), 3):
            cols = st.columns(min(3, len(self.current_data) - i))
            
            for j, (_, currency) in enumerate(self.current_data.iloc[i:i+3].iterrows()):
                with cols[j]:
                    change_class = "positive" if currency['change_pct'] > 0 else "negative" if currency['change_pct'] < 0 else "neutral"
                    
                    st.markdown(f"""
                    <div class="currency-card">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <span class="currency-icon">{currency['icone']}</span>
                            <div>
                                <h3 style="margin: 0; font-size: 1.2rem;">{currency['symbole']}</h3>
                                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{currency['nom']}</p>
                            </div>
                        </div>
                        <div class="currency-value">{currency['prix']:.4f}</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">{currency['unite']}</div>
                        <div class="currency-change {change_class}">
                            {currency['change_pct']:+.2f}%
                        </div>
                        <div style="margin-top: 1rem; font-size: 0.8rem;">
                            📊 Vol: {currency['volume_journalier']:.1f}B<br>
                            📈 Volatilité: {currency['volatilite']:.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    def create_price_overview(self):
        """Crée la vue d'ensemble des prix"""
        st.markdown('<h3 class="section-header">📈 ANALYSE DES TAUX HISTORIQUES</h3>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_currencies = st.multiselect(
                "Sélectionnez les paires de devises:",
                list(self.currencies.keys()),
                default=list(self.currencies.keys()) # Toutes sélectionnées par défaut
            )
        
        with col2:
            period = st.selectbox(
                "Période d'analyse:",
                ['1 mois', '3 mois', '6 mois', '1 an', '2 ans', 'Toute la période'],
                index=3
            )
        
        filtered_data = self.historical_data[
            self.historical_data['symbole'].isin(selected_currencies)
        ]
        
        if period != 'Toute la période':
            if 'mois' in period:
                months = int(period.split()[0])
                cutoff_date = datetime.now() - timedelta(days=30 * months)
            else:
                years = int(period.split()[0])
                cutoff_date = datetime.now() - timedelta(days=365 * years)
            filtered_data = filtered_data[filtered_data['date'] >= cutoff_date]
        
        fig = px.line(filtered_data, 
                     x='date', 
                     y='prix',
                     color='symbole',
                     title=f'Évolution des Taux de Change ({period})',
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(yaxis_title="Taux de Change")
        st.plotly_chart(fig, width='stretch')

    def create_trading_simulator(self):
        """Crée un simulateur de trading de devises"""
        st.markdown('<h3 class="section-header">💹 SIMULATEUR DE TRADING FOREX</h3>', 
                   unsafe_allow_html=True)
        
        st.markdown("""
        <div class="simulator-card">
            <h4>Simulez vos gains/pertes potentiels sur les paires EUR</h4>
            <p>Configurez votre position de trading et visualisez les résultats basés sur les données historiques.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_pair = st.selectbox(
                "Sélectionnez une paire de devises:",
                list(self.currencies.keys()),
                format_func=lambda x: f"{self.currencies[x]['icone']} {x} - {self.currencies[x]['nom']}"
            )
            
            position_type = st.radio(
                "Type de position:",
                ["Achat (Long)", "Vente (Short)"],
                horizontal=True
            )
            
            investment_amount = st.number_input(
                "Montant de l'investissement (€):",
                min_value=100,
                max_value=100000,
                value=1000,
                step=100
            )
            
            leverage = st.slider(
                "Effet de levier:",
                min_value=1,
                max_value=100,
                value=10,
                step=1
            )
        
        with col2:
            entry_date = st.date_input(
                "Date d'entrée:",
                value=datetime.now() - timedelta(days=30),
                min_value=datetime(2020, 1, 1),
                max_value=datetime.now()
            )
            
            exit_date = st.date_input(
                "Date de sortie:",
                value=datetime.now(),
                min_value=entry_date,
                max_value=datetime.now()
            )
            
            col2a, col2b = st.columns(2)
            with col2a:
                stop_loss_pct = st.number_input(
                    "Stop Loss (%):",
                    min_value=0.1,
                    max_value=20.0,
                    value=2.0,
                    step=0.1
                )
            with col2b:
                take_profit_pct = st.number_input(
                    "Take Profit (%):",
                    min_value=0.1,
                    max_value=20.0,
                    value=5.0,
                    step=0.1
                )
        
        if st.button("Lancer la simulation", type="primary"):
            pair_data = self.historical_data[
                self.historical_data['symbole'] == selected_pair
            ].copy()
            
            filtered_data = pair_data[
                (pair_data['date'] >= pd.to_datetime(entry_date)) & 
                (pair_data['date'] <= pd.to_datetime(exit_date))
            ].reset_index(drop=True)
            
            if len(filtered_data) > 0:
                entry_price = filtered_data.iloc[0]['prix']
                exit_price = filtered_data.iloc[-1]['prix']
                
                if position_type == "Achat (Long)":
                    pip_change = (exit_price - entry_price) / (0.0001 if 'JPY' not in selected_pair else 0.01)
                    price_change_pct = ((exit_price - entry_price) / entry_price) * 100
                else:
                    pip_change = (entry_price - exit_price) / (0.0001 if 'JPY' not in selected_pair else 0.01)
                    price_change_pct = ((entry_price - exit_price) / entry_price) * 100
                
                leveraged_investment = investment_amount * leverage
                profit_loss = leveraged_investment * (price_change_pct / 100)
                roi = (profit_loss / investment_amount) * 100
                
                stop_loss_triggered = False
                take_profit_triggered = False
                
                for i in range(1, len(filtered_data)):
                    current_price = filtered_data.iloc[i]['prix']
                    
                    if position_type == "Achat (Long)":
                        if current_price <= entry_price * (1 - stop_loss_pct/100):
                            stop_loss_triggered = True
                            exit_price = current_price
                            # Recalculer
                            pip_change = (exit_price - entry_price) / (0.0001 if 'JPY' not in selected_pair else 0.01)
                            price_change_pct = ((exit_price - entry_price) / entry_price) * 100
                            profit_loss = leveraged_investment * (price_change_pct / 100)
                            roi = (profit_loss / investment_amount) * 100
                            break
                        if current_price >= entry_price * (1 + take_profit_pct/100):
                            take_profit_triggered = True
                            exit_price = current_price
                            # Recalculer
                            pip_change = (exit_price - entry_price) / (0.0001 if 'JPY' not in selected_pair else 0.01)
                            price_change_pct = ((exit_price - entry_price) / entry_price) * 100
                            profit_loss = leveraged_investment * (price_change_pct / 100)
                            roi = (profit_loss / investment_amount) * 100
                            break
                    else:
                        if current_price >= entry_price * (1 + stop_loss_pct/100):
                            stop_loss_triggered = True
                            exit_price = current_price
                            # Recalculer
                            pip_change = (entry_price - exit_price) / (0.0001 if 'JPY' not in selected_pair else 0.01)
                            price_change_pct = ((entry_price - exit_price) / entry_price) * 100
                            profit_loss = leveraged_investment * (price_change_pct / 100)
                            roi = (profit_loss / investment_amount) * 100
                            break
                        if current_price <= entry_price * (1 - take_profit_pct/100):
                            take_profit_triggered = True
                            exit_price = current_price
                            # Recalculer
                            pip_change = (entry_price - exit_price) / (0.0001 if 'JPY' not in selected_pair else 0.01)
                            price_change_pct = ((entry_price - exit_price) / entry_price) * 100
                            profit_loss = leveraged_investment * (price_change_pct / 100)
                            roi = (profit_loss / investment_amount) * 100
                            break
                
                st.markdown("### Résultats de la simulation")
                
                col_result1, col_result2, col_result3 = st.columns(3)
                
                with col_result1:
                    st.metric("Prix d'entrée", f"{entry_price:.5f}", f"{entry_date}")
                with col_result2:
                    st.metric("Prix de sortie", f"{exit_price:.5f}", f"{exit_date if not stop_loss_triggered and not take_profit_triggered else 'Déclenché'}")
                with col_result3:
                    st.metric("Variation en pips", f"{pip_change:.1f}", f"{price_change_pct:+.2f}%")
                
                profit_loss_class = "profit-loss-positive" if profit_loss >= 0 else "profit-loss-negative"
                profit_loss_symbol = "+" if profit_loss >= 0 else ""
                
                st.markdown(f"""
                <div class="{profit_loss_class}">
                    <h3>Gain/Perte: {profit_loss_symbol}€{profit_loss:.2f}</h3>
                    <p>ROI: {profit_loss_symbol}{roi:.2f}%</p>
                    <p>Investissement: €{investment_amount:.2f} (Levier: {leverage}x)</p>
                    <p>Valeur position: €{leveraged_investment:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if stop_loss_triggered:
                    st.warning(f"⚠️ Stop Loss déclenché à {exit_price:.5f}")
                elif take_profit_triggered:
                    st.success(f"✅ Take Profit déclenché à {exit_price:.5f}")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=filtered_data['date'], y=filtered_data['prix'], mode='lines', name='Prix', line=dict(color='#003399')))
                fig.add_trace(go.Scatter(x=[filtered_data.iloc[0]['date']], y=[entry_price], mode='markers', name='Entrée', marker=dict(color='green', size=10)))
                fig.add_trace(go.Scatter(x=[filtered_data.iloc[-1]['date'] if not stop_loss_triggered and not take_profit_triggered else filtered_data.iloc[min(i, len(filtered_data)-1)]['date']], y=[exit_price], mode='markers', name='Sortie', marker=dict(color='red', size=10)))
                
                if position_type == "Achat (Long)":
                    fig.add_hline(y=entry_price * (1 - stop_loss_pct/100), line_dash="dash", line_color="red", annotation_text="Stop Loss")
                    fig.add_hline(y=entry_price * (1 + take_profit_pct/100), line_dash="dash", line_color="green", annotation_text="Take Profit")
                else:
                    fig.add_hline(y=entry_price * (1 + stop_loss_pct/100), line_dash="dash", line_color="red", annotation_text="Stop Loss")
                    fig.add_hline(y=entry_price * (1 - take_profit_pct/100), line_dash="dash", line_color="green", annotation_text="Take Profit")
                
                fig.update_layout(title=f"Évolution du prix - {selected_pair}", xaxis_title="Date", yaxis_title="Prix", height=500)
                st.plotly_chart(fig, width='stretch')
            else:
                st.error("Aucune donnée disponible pour la période sélectionnée.")

    def run(self):
        """Exécute le dashboard"""
        self.display_header()
        
        menu = st.sidebar.selectbox(
            "Navigation",
            ["Vue d'ensemble", "Analyse des prix", "Simulateur de trading"]
        )
        
        if menu == "Vue d'ensemble":
            self.display_currency_cards()
        elif menu == "Analyse des prix":
            self.create_price_overview()
        elif menu == "Simulateur de trading":
            self.create_trading_simulator()
        
        if st.sidebar.button("Mettre à jour les données"):
            self.update_live_data()
            st.rerun() # Correction ici

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = EuroForexDashboard()
    dashboard.run()