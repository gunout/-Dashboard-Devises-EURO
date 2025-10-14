# dashboard_yfinance_final.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Devises Euro - Temps Réel",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé (identique)
st.markdown("""
<style>
    .main-header { font-size: 2.8rem; background: linear-gradient(45deg, #003399, #0055A4, #0077CC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 2rem; font-weight: bold; padding: 1rem; }
    .currency-card { background: linear-gradient(135deg, #003399, #0055A4); color: white; padding: 1.5rem; border-radius: 15px; margin: 0.5rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .currency-value { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
    .currency-change { font-size: 1.2rem; padding: 0.5rem 1rem; border-radius: 25px; display: inline-block; margin-top: 0.5rem; }
    .positive { background-color: rgba(40, 167, 69, 0.2); color: #28a745; border: 2px solid #28a745; }
    .negative { background-color: rgba(220, 53, 69, 0.2); color: #dc3545; border: 2px solid #dc3545; }
    .neutral { background-color: rgba(108, 117, 125, 0.2); color: #6c757d; border: 2px solid #6c757d; }
    .section-header { color: #003399; border-bottom: 3px solid #FFCC00; padding-bottom: 0.5rem; margin-top: 2rem; font-size: 1.8rem; }
    .currency-icon { font-size: 2rem; margin-right: 1rem; }
    .simulator-card { background: linear-gradient(135deg, #003399, #0055A4); color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .profit-loss-positive { background-color: rgba(40, 167, 69, 0.2); color: #28a745; border: 2px solid #28a745; padding: 1rem; border-radius: 10px; font-weight: bold; text-align: center; }
    .profit-loss-negative { background-color: rgba(220, 53, 69, 0.2); color: #dc3545; border: 2px solid #dc3545; padding: 1rem; border-radius: 10px; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

class YFinanceEuroForexDashboard:
    def __init__(self):
        self.currencies = self.define_currencies()
        self.historical_data = pd.DataFrame()
        self.current_data = pd.DataFrame()
        self.last_update_time = None
        self.fetch_all_data() # Récupérer les données au démarrage

    def define_currencies(self):
        """Définit les paires de devises avec l'Euro et leur ticker yfinance."""
        return {
            'EUR/USD': {'nom': 'Euro / Dollar Américain', 'icone': '🇪🇺🇺🇸', 'yfinance_ticker': 'EURUSD=X'},
            'EUR/GBP': {'nom': 'Euro / Livre Sterling', 'icone': '🇪🇺🇬🇧', 'yfinance_ticker': 'EURGBP=X'},
            'EUR/JPY': {'nom': 'Euro / Yen Japonais', 'icone': '🇪🇺🇯🇵', 'yfinance_ticker': 'EURJPY=X'},
            'EUR/CHF': {'nom': 'Euro / Franc Suisse', 'icone': '🇪🇺🇨🇭', 'yfinance_ticker': 'EURCHF=X'},
            'EUR/AUD': {'nom': 'Euro / Dollar Australien', 'icone': '🇪🇺🇦🇺', 'yfinance_ticker': 'EURAUD=X'},
            'EUR/CAD': {'nom': 'Euro / Dollar Canadien', 'icone': '🇪🇺🇨🇦', 'yfinance_ticker': 'EURCAD=X'},
        }

    def fetch_all_data(self):
        """Récupère les données historiques et actuelles via yfinance."""
        all_historical_data = []
        current_rates_data = []
        
        tickers = [info['yfinance_ticker'] for info in self.currencies.values()]
        
        try:
            # Récupérer les données historiques (2 ans) pour le graphique et le simulateur
            hist_data = yf.download(tickers, period="2y", interval="1d")['Close']
            
            # Récupérer les données actuelles
            tickers_obj = yf.Tickers(tickers)
            
            for symbol, info in self.currencies.items():
                ticker = info['yfinance_ticker']
                
                # Données historiques
                if ticker in hist_data.columns:
                    df_hist = hist_data[[ticker]].dropna().copy()
                    df_hist.columns = ['prix']
                    df_hist['symbole'] = symbol
                    df_hist['nom'] = info['nom']
                    all_historical_data.append(df_hist)
                
                # Données actuelles
                current_price = tickers_obj.tickers[ticker].info.get('regularMarketPrice')
                previous_close = tickers_obj.tickers[ticker].info.get('previousClose')
                
                if current_price and previous_close:
                    change_pct = ((current_price - previous_close) / previous_close) * 100
                    current_rates_data.append({
                        'symbole': symbol,
                        'nom': info['nom'],
                        'icone': info['icone'],
                        'prix': current_price,
                        'change_pct': change_pct,
                        'yfinance_ticker': ticker
                    })

            if all_historical_data:
                self.historical_data = pd.concat(all_historical_data).reset_index()
                # --- CORRECTION ICI ---
                self.historical_data.rename(columns={'index': 'Date'}, inplace=True)
            
            if current_rates_data:
                self.current_data = pd.DataFrame(current_rates_data)
            
            self.last_update_time = datetime.now().strftime('%H:%M:%S')

        except Exception as e:
            st.error(f"Erreur lors de la récupération des données depuis yfinance: {e}")
            st.warning("Veuillez vérifier votre connexion internet ou réessayer plus tard.")

    def update_live_data(self):
        """Met à jour uniquement les données actuelles pour un rafraîchissement rapide."""
        current_rates_data = []
        tickers = [info['yfinance_ticker'] for info in self.currencies.values()]
        try:
            tickers_obj = yf.Tickers(tickers)
            for symbol, info in self.currencies.items():
                ticker = info['yfinance_ticker']
                current_price = tickers_obj.tickers[ticker].info.get('regularMarketPrice')
                previous_close = tickers_obj.tickers[ticker].info.get('previousClose')
                if current_price and previous_close:
                    change_pct = ((current_price - previous_close) / previous_close) * 100
                    current_rates_data.append({
                        'symbole': symbol, 'nom': info['nom'], 'icone': info['icone'],
                        'prix': current_price, 'change_pct': change_pct, 'yfinance_ticker': ticker
                    })
            if current_rates_data:
                self.current_data = pd.DataFrame(current_rates_data)
            self.last_update_time = datetime.now().strftime('%H:%M:%S')
        except Exception as e:
            st.sidebar.error(f"Erreur de mise à jour: {e}")

    def display_header(self):
        """Affiche l'en-tête du dashboard."""
        st.markdown('<h1 class="main-header">💱 DASHBOARD DEVISES EURO (TEMPS RÉEL)</h1>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; background: linear-gradient(45deg, #003399, #0055A4); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;"><h3>🔴 DONNÉES EN DIRECT DEPUIS YAHOO FINANCE</h3></div>', unsafe_allow_html=True)
        
        if self.last_update_time:
            st.sidebar.markdown(f"**🕐 Dernière mise à jour: {self.last_update_time}**")

    def display_currency_cards(self):
        """Affiche les cartes de devises avec les données en temps réel."""
        st.markdown('<h3 class="section-header">💰 TAUX DE CHANGE EN TEMPS RÉEL</h3>', unsafe_allow_html=True)
        
        if not self.current_data.empty:
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
                            <div class="currency-value">{currency['prix']:.5f}</div>
                            <div class="currency-change {change_class}">{currency['change_pct']:+.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("Chargement des données...")

    def create_price_overview(self):
        """Crée la vue d'ensemble des prix avec de vraies données historiques."""
        st.markdown('<h3 class="section-header">📈 ANALYSE DES TAUX HISTORIQUES</h3>', unsafe_allow_html=True)
        
        # --- CORRECTION ICI ---
        if self.historical_data.empty or 'Date' not in self.historical_data.columns:
            st.warning("Les données historiques ne sont pas encore chargées ou sont corrompues. Veuillez mettre à jour les données.")
            return

        col1, col2 = st.columns(2)
        
        with col1:
            selected_currencies = st.multiselect(
                "Sélectionnez les paires de devises:",
                list(self.currencies.keys()),
                default=list(self.currencies.keys())
            )
        
        with col2:
            period = st.selectbox(
                "Période d'analyse:",
                ['1 mois', '3 mois', '6 mois', '1 an', '2 ans'],
                index=3
            )
        
        filtered_data = self.historical_data[self.historical_data['symbole'].isin(selected_currencies)]
        
        if period != '2 ans':
            if 'mois' in period:
                months = int(period.split()[0])
                cutoff_date = datetime.now() - timedelta(days=30 * months)
            else:
                years = int(period.split()[0])
                cutoff_date = datetime.now() - timedelta(days=365 * years)
            # --- CORRECTION ICI ---
            filtered_data = filtered_data[filtered_data['Date'] >= cutoff_date]
        
        # --- CORRECTION ICI ---
        fig = px.line(filtered_data, x='Date', y='prix', color='symbole', title=f'Évolution des Taux de Change ({period})')
        fig.update_layout(yaxis_title="Taux de Change")
        st.plotly_chart(fig, width='stretch')

    def create_trading_simulator(self):
        """Crée un simulateur de trading basé sur de vraies données historiques."""
        st.markdown('<h3 class="section-header">💹 SIMULATEUR DE TRADING HISTORIQUE</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="simulator-card">
            <h4>Simulez vos gains/pertes sur une période passée réelle</h4>
            <p>Configurez votre position et analysez le résultat avec les données historiques de Yahoo Finance.</p>
        </div>
        """, unsafe_allow_html=True)

        # --- CORRECTION ICI ---
        if self.historical_data.empty or 'Date' not in self.historical_data.columns:
            st.warning("Les données historiques ne sont pas encore disponibles ou sont corrompues. Veuillez mettre à jour les données.")
            return

        col1, col2 = st.columns(2)
        
        with col1:
            selected_pair = st.selectbox("Sélectionnez une paire de devises:", list(self.currencies.keys()))
            position_type = st.radio("Type de position:", ["Achat (Long)", "Vente (Short)"], horizontal=True)
            investment_amount = st.number_input("Montant de l'investissement (€):", min_value=100, max_value=100000, value=1000, step=100)
            leverage = st.slider("Effet de levier:", min_value=1, max_value=30, value=10, step=1)
        
        with col2:
            pair_data = self.historical_data[self.historical_data['symbole'] == selected_pair]
            # --- CORRECTION ICI ---
            if pair_data.empty or 'Date' not in pair_data.columns:
                st.error(f"Aucune donnée historique trouvée ou corrompue pour la paire {selected_pair}. Essayez de mettre à jour les données.")
                return

            # --- CORRECTION ICI ---
            min_date = pair_data['Date'].min().date()
            max_date = pair_data['Date'].max().date()
            
            entry_date = st.date_input("Date d'entrée:", value=min_date, min_value=min_date, max_value=max_date)
            exit_date = st.date_input("Date de sortie:", value=max_date, min_value=entry_date, max_value=max_date)
            
            col2a, col2b = st.columns(2)
            with col2a:
                stop_loss_pct = st.number_input("Stop Loss (%):", min_value=0.1, max_value=20.0, value=2.0, step=0.1)
            with col2b:
                take_profit_pct = st.number_input("Take Profit (%):", min_value=0.1, max_value=20.0, value=5.0, step=0.1)
        
        if st.button("Lancer la simulation", type="primary"):
            # --- CORRECTION ICI ---
            filtered_pair_data = pair_data[(pair_data['Date'] >= pd.to_datetime(entry_date)) & (pair_data['Date'] <= pd.to_datetime(exit_date))].reset_index(drop=True)
            
            if len(filtered_pair_data) > 1:
                entry_price = filtered_pair_data.iloc[0]['prix']
                exit_price = filtered_pair_data.iloc[-1]['prix']
                
                # Simulation Stop Loss / Take Profit
                stop_loss_triggered = False
                take_profit_triggered = False
                
                for i in range(1, len(filtered_pair_data)):
                    current_price = filtered_pair_data.iloc[i]['prix']
                    if position_type == "Achat (Long)":
                        if current_price <= entry_price * (1 - stop_loss_pct/100):
                            stop_loss_triggered = True
                            exit_price = current_price
                            break
                        if current_price >= entry_price * (1 + take_profit_pct/100):
                            take_profit_triggered = True
                            exit_price = current_price
                            break
                    else: # Vente (Short)
                        if current_price >= entry_price * (1 + stop_loss_pct/100):
                            stop_loss_triggered = True
                            exit_price = current_price
                            break
                        if current_price <= entry_price * (1 - take_profit_pct/100):
                            take_profit_triggered = True
                            exit_price = current_price
                            break
                
                # Calculs finaux
                pip_change = (exit_price - entry_price) / (0.0001 if 'JPY' not in selected_pair else 0.01)
                if position_type == "Achat (Long)":
                    price_change_pct = ((exit_price - entry_price) / entry_price) * 100
                else:
                    price_change_pct = ((entry_price - exit_price) / entry_price) * 100
                
                leveraged_investment = investment_amount * leverage
                profit_loss = leveraged_investment * (price_change_pct / 100)
                roi = (profit_loss / investment_amount) * 100
                
                # Affichage des résultats
                st.markdown("### Résultats de la simulation")
                col_result1, col_result2, col_result3 = st.columns(3)
                with col_result1: st.metric("Prix d'entrée", f"{entry_price:.5f}", f"{entry_date}")
                with col_result2: st.metric("Prix de sortie", f"{exit_price:.5f}", f"{exit_date if not (stop_loss_triggered or take_profit_triggered) else 'Déclenché'}")
                with col_result3: st.metric("Variation en pips", f"{pip_change:.1f}", f"{price_change_pct:+.2f}%")
                
                profit_loss_class = "profit-loss-positive" if profit_loss >= 0 else "profit-loss-negative"
                profit_loss_symbol = "+" if profit_loss >= 0 else ""
                st.markdown(f"""
                <div class="{profit_loss_class}">
                    <h3>Gain/Perte: {profit_loss_symbol}€{profit_loss:.2f}</h3>
                    <p>ROI: {profit_loss_symbol}{roi:.2f}%</p>
                    <p>Investissement: €{investment_amount:.2f} (Levier: {leverage}x)</p>
                </div>
                """, unsafe_allow_html=True)
                
                if stop_loss_triggered: st.warning(f"⚠️ Stop Loss déclenché à {exit_price:.5f}")
                elif take_profit_triggered: st.success(f"✅ Take Profit déclenché à {exit_price:.5f}")

                # Graphique
                fig = go.Figure()
                # --- CORRECTION ICI ---
                fig.add_trace(go.Scatter(x=filtered_pair_data['Date'], y=filtered_pair_data['prix'], mode='lines', name='Prix', line=dict(color='#003399')))
                # --- CORRECTION ICI ---
                fig.add_trace(go.Scatter(x=[filtered_pair_data.iloc[0]['Date']], y=[entry_price], mode='markers', name='Entrée', marker=dict(color='green', size=10)))
                # --- CORRECTION ICI ---
                fig.add_trace(go.Scatter(x=[filtered_pair_data.iloc[-1]['Date'] if not (stop_loss_triggered or take_profit_triggered) else filtered_pair_data.iloc[min(i, len(filtered_pair_data)-1)]['Date']], y=[exit_price], mode='markers', name='Sortie', marker=dict(color='red', size=10)))
                
                if position_type == "Achat (Long)":
                    fig.add_hline(y=entry_price * (1 - stop_loss_pct/100), line_dash="dash", line_color="red", annotation_text="Stop Loss")
                    fig.add_hline(y=entry_price * (1 + take_profit_pct/100), line_dash="dash", line_color="green", annotation_text="Take Profit")
                else:
                    fig.add_hline(y=entry_price * (1 + stop_loss_pct/100), line_dash="dash", line_color="red", annotation_text="Stop Loss")
                    fig.add_hline(y=entry_price * (1 - take_profit_pct/100), line_dash="dash", line_color="green", annotation_text="Take Profit")
                
                fig.update_layout(title=f"Simulation - {selected_pair}", xaxis_title="Date", yaxis_title="Prix", height=500)
                st.plotly_chart(fig, width='stretch')
            else:
                st.error("Aucune donnée disponible pour la période sélectionnée.")

    def run(self):
        """Exécute le dashboard."""
        self.display_header()
        
        menu = st.sidebar.selectbox("Navigation", ["Vue d'ensemble", "Analyse des prix", "Simulateur de trading"])
        
        if menu == "Vue d'ensemble":
            self.display_currency_cards()
        elif menu == "Analyse des prix":
            self.create_price_overview()
        elif menu == "Simulateur de trading":
            self.create_trading_simulator()
        
        # Bouton de mise à jour manuel
        if st.sidebar.button("🔄 Mettre à jour les données", type="primary"):
            with st.spinner('Récupération des données...'):
                self.fetch_all_data()
                st.rerun()
        
        # Auto-refresh toutes les 60 secondes pour les données actuelles
        time.sleep(60)
        self.update_live_data()
        st.rerun()

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = YFinanceEuroForexDashboard()
    dashboard.run()