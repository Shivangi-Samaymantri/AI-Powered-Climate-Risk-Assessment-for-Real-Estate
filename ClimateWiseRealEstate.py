import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page config first
st.set_page_config(
    page_title="ClimateWise Real Estate",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional color palette
COLORS = {
    'navy': '#1a365d',
    'blue': '#2563eb',
    'indigo': '#4f46e5',
    'green': '#059669',
    'emerald': '#10b981',
    'red': '#dc2626',
    'orange': '#ea580c',
    'gray': '#4b5563',
    'lightgray': '#e5e7eb',
    'white': '#ffffff',
    'black': '#111827'
}

# Load data function - MOVED BEFORE ANY USE
@st.cache_data
def load_location_data():
    try:
        # Load your actual data
        df = pd.read_csv('filled_redfin_noaa_data.csv')
        # Ensure columns are properly named
        df['STATE'] = df['STATE'].str.upper().str.strip()
        df['CITY'] = df['CITY'].str.title().str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Function to get price analysis from actual data
def get_price_analysis(state, city):
    try:
        # Load your actual data
        df = pd.read_csv('filled_redfin_noaa_data.csv')
        location_data = df[(df['STATE'].str.upper() == state.upper()) & 
                          (df['CITY'].str.title() == city.title())].copy()
        
        if location_data.empty:
            return None
        
        # Take only the 10 most recent entries for this location
        location_data['PERIOD_BEGIN'] = pd.to_datetime(location_data['PERIOD_BEGIN'])
        location_data = location_data.sort_values('PERIOD_BEGIN', ascending=False).head(10)
        recent_data = location_data.iloc[0]
        
        # Current price
        current_price = recent_data['MEDIAN_SALE_PRICE']
        
        # Simple prediction based on historical data for this location
        if len(location_data) > 1:
            # Calculate average growth rate from available data
            price_changes = location_data['MEDIAN_SALE_PRICE'].pct_change().dropna()
            if not price_changes.empty:
                annual_growth_rate = price_changes.mean() * 12
            else:
                annual_growth_rate = 0.03  # Default 3% growth
        else:
            annual_growth_rate = 0.03  # Default 3% growth
        
        # Predict price for 12 months out
        predicted_price = current_price * (1 + annual_growth_rate)
        
        # Calculate percentage change
        price_change = ((predicted_price - current_price) / current_price) * 100
        
        return {
            'current_price': current_price,
            'predicted_price': predicted_price,
            'price_change': price_change,
            'data_date': recent_data['PERIOD_BEGIN']
        }
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

# Function to get weather risk assessment
def get_weather_risk(state, city):
    try:
        df = pd.read_csv('filled_redfin_noaa_data.csv')
        location_data = df[(df['STATE'].str.upper() == state.upper()) & 
                          (df['CITY'].str.title() == city.title())].copy()
        
        if location_data.empty:
            return None
        
        # Get the most recent weather data
        recent_data = location_data.iloc[-1]
        
        # Calculate weather risk score
        risk_factors = {
            'precipitation': recent_data.get('precipitation', 0),
            # With one of these options:
			'avg_temp': recent_data.get('avg_temp', 0),  # Average temperature
			'humidity': recent_data.get('humidity', 0),   # Humidity level
			'wind_speed': recent_data.get('wind_speed', 0), # Wind speed
			'pressure': recent_data.get('pressure', 0),    # Atmospheric pressure
            'natural_disaster_score': recent_data.get('natural_disaster_score', 0),
            'fema_disaster_count': recent_data.get('fema_disaster_count', 0),
            'avg_temp': recent_data.get('avg_temp', 0),
            'humidity': recent_data.get('humidity', 0),
            'wind_speed': recent_data.get('wind_speed', 0)
        }
        
        # Calculate overall risk score (0-100)
        precipitation_risk = min(risk_factors['precipitation'] / 1500 * 20, 20)
        humidity_risk = min(risk_factors['humidity'] / 100 * 30, 30)
        natural_disaster_risk = min(risk_factors['natural_disaster_score'] / 30 * 20, 20)
        fema_risk = min(risk_factors['fema_disaster_count'] / 50 * 15, 15)
        climate_risk = min(15 * (1 - (abs(risk_factors['avg_temp'] - 70) / 40)), 15)
        
        overall_risk = precipitation_risk + humidity_risk + natural_disaster_risk + fema_risk + climate_risk
        
        return {
            'precipitation': risk_factors['precipitation'],
            'natural_disaster_score': risk_factors['natural_disaster_score'],
            'fema_disaster_count': risk_factors['fema_disaster_count'],
            'avg_temp': risk_factors['avg_temp'],
            'humidity': risk_factors['humidity'],
            'wind_speed': risk_factors['wind_speed'],
            'overall_risk': overall_risk
        }
    except Exception as e:
        st.error(f"Error analyzing weather risk: {e}")
        return None

# Function to generate investment recommendation
def get_investment_recommendation(price_analysis, weather_risk):
    score = 0
    factors = {}
    
    # Price trend analysis
    if price_analysis['price_change'] > 5:
        score += 40
        factors['price_trend'] = "Excellent"
    elif price_analysis['price_change'] > 0:
        score += 20
        factors['price_trend'] = "Good"
    else:
        score -= 10
        factors['price_trend'] = "Declining"
    
    # Risk assessment
    if weather_risk['overall_risk'] < 20:
        score += 40
        factors['weather_risk'] = "Low"
    elif weather_risk['overall_risk'] < 40:
        score += 20
        factors['weather_risk'] = "Moderate"
    elif weather_risk['overall_risk'] < 60:
        score += 10
        factors['weather_risk'] = "High"
    else:
        score -= 20
        factors['weather_risk'] = "Very High"
    
    # Market conditions
    if price_analysis['current_price'] > 500000:
        score -= 5  # Premium markets may have limited growth
    
    # Normalize score to 0-100
    score = max(0, min(100, score))
    
    # Generate recommendation
    if score >= 70:
        recommendation = "Strong Buy"
        recommendation_color = COLORS['green']
        recommendation_details = "Excellent investment opportunity"
    elif score >= 50:
        recommendation = "Buy"
        recommendation_color = COLORS['emerald']
        recommendation_details = "Good investment potential"
    elif score >= 30:
        recommendation = "Hold/Wait"
        recommendation_color = COLORS['orange']
        recommendation_details = "Monitor market conditions"
    else:
        recommendation = "Don't Invest"
        recommendation_color = COLORS['red']
        recommendation_details = "High risk, consider alternatives"
    
    return {
        'score': score,
        'recommendation': recommendation,
        'recommendation_color': recommendation_color,
        'recommendation_details': recommendation_details,
        'factors': factors
    }

# Function to create professional price chart
def create_price_chart(current_price, predicted_price):
    current_date = datetime.now()
    future_dates = [current_date + timedelta(days=30*i) for i in range(13)]
    
    # Create realistic price progression
    price_progression = []
    for i in range(13):
        fluctuation = np.random.normal(0, 0.01)
        if i == 0:
            price_progression.append(current_price)
        elif i == 12:
            price_progression.append(predicted_price)
        else:
            linear_interpolation = current_price + (predicted_price - current_price) * (i / 12)
            price_progression.append(linear_interpolation * (1 + fluctuation))
    
    fig = go.Figure()
    
    # Main price trend line
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=price_progression,
        mode='lines+markers',
        name='Price Prediction',
        line=dict(color=COLORS['green'], width=3),
        marker=dict(size=8, color=COLORS['green']),
        fill='tozeroy',
        fillcolor='rgba(5, 150, 105, 0.1)'
    ))
    
    # Key points
    fig.add_trace(go.Scatter(
        x=[future_dates[0], future_dates[-1]],
        y=[current_price, predicted_price],
        mode='markers+text',
        name='Key Points',
        marker=dict(size=14, color=[COLORS['blue'], COLORS['red']], 
                   line=dict(width=2, color='white')),
        text=[f'Current: ${current_price:,.0f}', f'Predicted: ${predicted_price:,.0f}'],
        textposition='top center',
        textfont=dict(size=12, color='#374151', family="Arial"),
        showlegend=False
    ))
    
    fig.update_layout(
        title={
            'text': '12-Month Price Prediction',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'family': 'Arial', 'color': '#1a365d'}
        },
        xaxis_title='Date',
        yaxis_title='Price ($)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        height=400,
        yaxis_tickformat='$,.0f',
        xaxis=dict(
            showgrid=True,
            gridcolor='#e5e7eb',
            zerolinecolor='#e5e7eb'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e5e7eb',
            zerolinecolor='#e5e7eb'
        ),
        font=dict(
            family="Arial",
            size=12,
            color='#4b5563'
        ),
        margin=dict(l=60, r=20, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Main function to display price analysis
def display_price_analysis():
    analysis = get_price_analysis(
        st.session_state.selected_state, 
        st.session_state.selected_city
    )
    
    if analysis is None:
        st.error("Could not find data for the selected location.")
        return
    
    st.markdown("""
    <div class="price-chart-container">
        <h2 style="color: #1a365d; font-size: 1.875rem; font-weight: 700; margin-bottom: 1.5rem;">Price Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Display location details
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e5e7eb; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #2563eb;">
        <h3 style="color: #1a365d; margin-bottom: 0.5rem; font-size: 1.5rem; font-weight: 600;">Location: {st.session_state.selected_city}, {st.session_state.selected_state}</h3>
        <p style="color: #4b5563; margin: 0;">Data as of: {analysis['data_date'].strftime('%B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display current and predicted price
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="analysis-card" style="border-left: 4px solid {COLORS['blue']};">
            <h4>Current Price</h4>
            <h2 style="color: {COLORS['navy']};">${analysis['current_price']:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Determine color based on price change
        if analysis['price_change'] > 0:
            change_color = "#059669"  # Green for positive
            arrow_text = "↗"  # Up arrow
            change_text = f"{arrow_text} {analysis['price_change']:.1f}%"
        else:
            change_color = "#dc2626"  # Red for negative
            arrow_text = "↘"  # Down arrow  
            change_text = f"{arrow_text} {analysis['price_change']:.1f}%"
        
        st.markdown(f"""
        <div class="analysis-card" style="border-left: 4px solid {change_color};">
            <h4>Price Change (12 months)</h4>
            <h2 style="color: {change_color};">{change_text}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="analysis-card" style="border-left: 4px solid {COLORS['green']};">
            <h4>Predicted Price</h4>
            <h2 style="color: {COLORS['green']};">${analysis['predicted_price']:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Display price chart
    st.markdown('<div class="price-chart-container">', unsafe_allow_html=True)
    fig = create_price_chart(analysis['current_price'], analysis['predicted_price'])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get weather risk analysis
    weather_risk = get_weather_risk(st.session_state.selected_state, st.session_state.selected_city)
    
    if weather_risk:
        # Get investment recommendation
        recommendation = get_investment_recommendation(analysis, weather_risk)
        
        # Display investment recommendation
        st.markdown(f"""
        <div class="investment-recommendation" style="background: #f9fafb; border: 2px solid {recommendation['recommendation_color']}; 
             padding: 2rem; border-radius: 12px; margin-top: 2rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h2 style="color: {recommendation['recommendation_color']}; text-align: center; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">
                {recommendation['recommendation']}
            </h2>
            <p style="text-align: center; font-size: 1.25rem; color: #4b5563; margin-bottom: 1.5rem;">
                {recommendation['recommendation_details']}
            </p>
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="display: inline-block; background: {recommendation['recommendation_color']}; color: white; 
                     padding: 0.5rem 1.5rem; border-radius: 9999px; font-size: 1.125rem; font-weight: 600;">
                    Investment Score: {recommendation['score']}/100
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display risk factors
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="risk-card" style="background: white; border: 1px solid #e5e7eb; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
                <h3 style="color: {COLORS['blue']}; font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">Key Factors</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #4b5563;">Price Trend:</span>
                    <span style="font-weight: 600; color: {COLORS['green'] if recommendation['factors']['price_trend'] == 'Excellent' else COLORS['blue'] if recommendation['factors']['price_trend'] == 'Good' else COLORS['red']};">
                        {recommendation['factors']['price_trend']}
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #4b5563;">Weather Risk:</span>
                    <span style="font-weight: 600; color: {COLORS['green'] if recommendation['factors']['weather_risk'] == 'Low' else COLORS['orange'] if recommendation['factors']['weather_risk'] == 'Moderate' else COLORS['red']};">
                        {recommendation['factors']['weather_risk']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="risk-card" style="background: white; border: 1px solid #e5e7eb; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
                <h3 style="color: {COLORS['orange']}; font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">Weather Risk Details</h3>
                # With (example using humidity):
				<div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
    				<span style="color: #4b5563;">Humidity:</span>
    				<span style="font-weight: 600; color: {COLORS['red'] if weather_risk['humidity'] > 70 else COLORS['orange'] if weather_risk['humidity'] > 50 else COLORS['green']};">
       					{weather_risk['humidity']:.1f}%
    				</span>
				</div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #4b5563;">Natural Disaster Risk:</span>
                    <span style="font-weight: 600; color: {COLORS['red'] if weather_risk['natural_disaster_score'] > 20 else COLORS['orange'] if weather_risk['natural_disaster_score'] > 10 else COLORS['green']};">
                        {weather_risk['natural_disaster_score']:.1f}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Key insights
    st.markdown("""
    <div class="insight-box">
        <h3>Key Insights</h3>
        <div class="insight-text">
            <div class="icon-container icon-green" style="flex-shrink: 0;">📈</div>
            <p style="margin: 0; color: #4b5563; font-size: 1.125rem;">
                <strong>Strong Growth Expected</strong>: The market shows significant upward momentum with price appreciation driven by fundamental market factors.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Hide streamlit default elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Background for the main app */
    .stApp {
        background-color: #f9fafb;
    }
    
    /* Custom header with background image */
    .main-header {
        background-image: linear-gradient(to right, rgba(30, 58, 138, 0.9), rgba(5, 150, 105, 0.9)), 
                          url('https://images.unsplash.com/photo-1600585154340-be6161a56a0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
        padding: 4rem 2rem;
        border-radius: 12px;
        margin-bottom: 3rem;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
        letter-spacing: -0.025em;
    }
    
    .tagline {
        font-size: 1.5rem;
        color: #f3f4f6;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
        font-weight: 400;
    }
    
    /* Professional cards */
    .info-card {
        background: white;
        border-radius: 8px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border-top: 4px solid #2563eb;
    }
    
    .info-card h2 {
        color: #1a365d;
        font-size: 1.875rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .info-card p {
        text-align: center;
        color: #4b5563;
        font-size: 1.125rem;
        margin-bottom: 2rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    
    /* Process steps */
    .process-step {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #2563eb;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .process-step:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .process-step h3 {
        color: #1a365d;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .process-step p {
        color: #4b5563;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Selection card */
    .selection-card {
        background: white;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border-top: 4px solid #059669;
        margin-top: 3rem;
    }
    
    .selection-card h2 {
        color: #059669;
        font-size: 1.875rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .selection-card p {
        text-align: center;
        color: #4b5563;
        font-size: 1.125rem;
        margin-bottom: 2rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Professional button styling */
    .stButton > button {
        background-color: #059669;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.75rem 2rem;
        border: none;
        width: 100%;
        margin-top: 1rem;
        transition: all 0.2s ease;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background-color: #065f46;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:disabled {
        background-color: #9ca3af;
        cursor: not-allowed;
    }
    
    /* Professional select box styling */
    .stSelectbox label {
        font-weight: 600;
        color: #374151;
        font-size: 1rem;
    }
    
    div[data-baseweb="select"] > div {
        border-color: #e5e7eb;
        border-radius: 6px;
    }
    
    div[data-baseweb="select"]:hover > div {
        border-color: #2563eb;
    }
    
    /* Analysis card styling */
    .analysis-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .analysis-card h4 {
        color: #6b7280;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .analysis-card h2 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .price-chart-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    /* Professional footer */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        background-color: #1a365d;
        color: #e2e8f0;
        margin-top: 4rem;
        border-radius: 8px;
    }
    
    /* Icons styling */
    .icon-container {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 8px;
        margin-right: 1rem;
        font-size: 1.25rem;
        color: white;
    }
    
    .icon-blue { background-color: #2563eb; }
    .icon-green { background-color: #059669; }
    .icon-orange { background-color: #ea580c; }
    .icon-red { background-color: #dc2626; }
    
    /* Insights styling */
    .insight-box {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 2rem;
        border-left: 4px solid #2563eb;
    }
    
    .insight-box h3 {
        color: #1a365d;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .insight-text {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    
    /* News ticker */
    .news-ticker {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #1a365d;
        color: white;
        padding: 1rem;
        z-index: 1000;
        box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .news-ticker-content {
        animation: scroll-right 30s linear infinite;
        white-space: nowrap;
    }
    
    @keyframes scroll-right {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    /* Risk assessment styles */
    .investment-recommendation {
        animation: fadeInUp 0.5s ease-out;
    }
    
    .risk-card {
        transition: all 0.3s ease;
    }
    
    .risk-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# Main header with background image
st.markdown("""
<div class="main-header">
    <h1>ClimateWise Real Estate</h1>
    <p class="tagline">Data-Driven Investment Decisions for a Changing Climate</p>
</div>
""", unsafe_allow_html=True)

# How It Works section
st.markdown("""
<div class="info-card">
    <h2>How ClimateWise Works</h2>
    <p>Our platform combines advanced analytics with real-time data to provide comprehensive real estate investment insights in the context of climate change.</p>
</div>
""", unsafe_allow_html=True)

# Process steps
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="process-step">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div class="icon-container icon-blue">📊</div>
            <h3>Data Analysis</h3>
        </div>
        <p>We analyze FEMA disaster data, NOAA weather patterns, and Redfin market trends to understand local risk factors.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="process-step">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div class="icon-container icon-green">📈</div>
            <h3>Price Prediction</h3>
        </div>
        <p>Machine learning models predict property prices considering climate risk, market trends, and historical data.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="process-step">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div class="icon-container icon-orange">🛡️</div>
            <h3>Expert Insights</h3>
        </div>
        <p>AI-powered analysis provides personalized investment recommendations based on your selected location.</p>
    </div>
    """, unsafe_allow_html=True)

# Load data
df = load_location_data()

if df is not None:
    # Selection section
    st.markdown("""
    <div class="selection-card">
        <h2>Select Your Location</h2>
        <p>Choose a state and city to analyze property investment opportunities and discover climate-aware insights for your real estate decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        states = sorted(df['STATE'].dropna().unique().tolist())
        selected_state = st.selectbox(
            "Select State",
            options=["Select a state..."] + states,
            key="state_select"
        )
    
    with col2:
        if selected_state and selected_state != "Select a state...":
            cities = sorted(df[df['STATE'] == selected_state]['CITY'].dropna().unique().tolist())
            selected_city = st.selectbox(
                "Select City",
                options=["Select a city..."] + cities,
                key="city_select"
            )
        else:
            selected_city = st.selectbox(
                "Select City",
                options=["Select a state first..."],
                disabled=True,
                key="city_select"
            )
    
    # Generate Analysis button
    button_col = st.columns([1, 2, 1])[1]
    with button_col:
        generate_clicked = st.button(
            "Generate Investment Analysis",
            key="generate_btn",
            disabled=not (selected_state and selected_state != "Select a state..." and 
                         selected_city and selected_city != "Select a city..." and 
                         selected_city != "Select a state first...")
        )
        
        if generate_clicked:
            st.session_state.selected_state = selected_state
            st.session_state.selected_city = selected_city
            st.session_state.analysis_generated = True
    
    # Display price analysis when analysis is generated
    if 'analysis_generated' in st.session_state and st.session_state.analysis_generated:
        st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
        display_price_analysis()
else:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #fef2f2; border-radius: 8px; border: 1px solid #fca5a5; margin: 1rem 0;">
        <h3 style="color: #dc2626;">Data Loading Error</h3>
        <p style="color: #991b1b;">Could not load the necessary data. Please check if the dataset exists at the specified path.</p>
    </div>
    """, unsafe_allow_html=True)

# Professional footer
st.markdown("""
<div class="footer">
    © 2024 ClimateWise Real Estate - Making data-driven decisions for a sustainable future
</div>
""", unsafe_allow_html=True)

# News ticker for real estate updates
st.markdown("""
<div class="news-ticker">
    <div class="news-ticker-content">
        Latest Updates: Miami real estate market shows resilience • Hurricane-resistant properties in demand • Climate insurance costs rising in coastal areas • Green building incentives expand nationwide
    </div>
</div>
""", unsafe_allow_html=True)