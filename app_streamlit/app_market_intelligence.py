#!/usr/bin/env python3
"""
V2 Market Intelligence Dashboard
Visualizes tourism market data for Mallorca.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.v2_pipeline.market_db import MarketIntelligenceDB


st.set_page_config(
    page_title="Optimus Price — Market Intelligence",
    page_icon="🏨",
    layout="wide",
)

# Initialize database
@st.cache_resource
def load_db():
    return MarketIntelligenceDB()

db = load_db()

# Header
st.title("🏨 Market Intelligence Dashboard")
st.markdown("**Mallorca Tourism Market** — Datos de INE, Google Trends y Airbnb")

# Sidebar filters
st.sidebar.header("Filtros")

# Get available data
stats = db.get_stats()
st.sidebar.metric("Registros totales", sum(stats.values()))
for table, count in stats.items():
    st.sidebar.metric(table, count)

# Region filter
region = st.sidebar.selectbox(
    "Región",
    ["mallorca", "baleares"],
    format_func=lambda x: "Mallorca" if x == "mallorca" else "Baleares",
)

# Segment filter
segment = st.sidebar.selectbox(
    "Segmento",
    ["playa_costa", "palma_urbano", "alcudia_family", "magaluf_party", "interior_rural", "luxury_villas"],
    format_func=lambda x: x.replace("_", " ").title(),
)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Index", "📈 Seasonality", "🔍 Demand Signals", "🏠 Airbnb Prices"])

# Tab 1: Market Index
with tab1:
    st.header("Market Index — Precio Medio por Mes")
    
    index_data = db.query_market_index(region=region, segment=segment, limit=200)
    
    if index_data:
        df_index = pd.DataFrame(index_data)
        df_index['index_date'] = pd.to_datetime(df_index['index_date'])
        df_index = df_index.sort_values('index_date')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                df_index,
                x='index_date',
                y='avg_price',
                title='Precio Medio (EUR/noche)',
                labels={'index_date': 'Fecha', 'avg_price': 'Precio Medio (EUR)'},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                df_index,
                x='index_date',
                y='price_index',
                title='Índice de Precios (base 100)',
                labels={'index_date': 'Fecha', 'price_index': 'Índice'},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.subheader("Estadísticas")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            latest_price = df_index['avg_price'].iloc[-1]
            st.metric("Precio Actual", f"€{latest_price:.0f}")
        
        with col2:
            if len(df_index) > 12:
                yoy_change = (df_index['avg_price'].iloc[-1] / df_index['avg_price'].iloc[-13] - 1) * 100
                st.metric("Cambio Anual", f"{yoy_change:+.1f}%")
        
        with col3:
            st.metric("Mínimo", f"€{df_index['avg_price'].min():.0f}")
        
        with col4:
            st.metric("Máximo", f"€{df_index['avg_price'].max():.0f}")
    else:
        st.info("No hay datos de market index disponibles para esta región/segmento.")

# Tab 2: Seasonality
with tab2:
    st.header("Seasonality Index — Factor Estacional")
    
    seasonality = db.query_seasonality(region=region, segment=segment)
    
    if seasonality:
        df_season = pd.DataFrame(seasonality)
        month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        df_season['month_name'] = df_season['month'].apply(lambda x: month_names[x-1])
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df_season,
                x='month_name',
                y='seasonality_factor',
                title='Factor Estacional (1.0 = Promedio)',
                labels={'month_name': 'Mes', 'seasonality_factor': 'Factor'},
                color='seasonality_factor',
                color_continuous_scale='RdYlGn',
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df_season,
                x='month_name',
                y='avg_occupancy',
                title='Ocupación Promedio Histórica',
                labels={'month_name': 'Mes', 'avg_occupancy': 'Ocupación'},
                color='avg_occupancy',
                color_continuous_scale='Blues',
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Season summary
        st.subheader("Resumen de Temporadas")
        col1, col2, col3, col4 = st.columns(4)
        
        peak_month = df_season.loc[df_season['seasonality_factor'].idxmax()]
        low_month = df_season.loc[df_season['seasonality_factor'].idxmin()]
        
        with col1:
            st.metric("Mes Peak", peak_month['month_name'], f"{peak_month['seasonality_factor']:.2f}x")
        
        with col2:
            st.metric("Mes Bajo", low_month['month_name'], f"{low_month['seasonality_factor']:.2f}x")
        
        with col3:
            st.metric("Ocupación Peak", f"{peak_month['avg_occupancy']*100:.0f}%")
        
        with col4:
            st.metric("Ocupación Baja", f"{low_month['avg_occupancy']*100:.0f}%")
    else:
        st.info("No hay datos de estacionalidad disponibles.")

# Tab 3: Demand Signals
with tab3:
    st.header("Demand Signals — Señales de Demanda")
    
    # Google Trends data
    with db._conn() as conn:
        rows = conn.execute("""
            SELECT signal_date, search_volume_index, source_metric
            FROM demand_signals
            WHERE source = 'google_trends' AND region = ?
            ORDER BY signal_date
        """, (region,)).fetchall()
        gt_data = [dict(r) for r in rows]
    
    if gt_data:
        df_gt = pd.DataFrame(gt_data)
        df_gt['signal_date'] = pd.to_datetime(df_gt['signal_date'])
        df_gt = df_gt.sort_values('signal_date')
        
        # Pivot for multi-line chart
        df_pivot = df_gt.pivot_table(
            index='signal_date',
            columns='source_metric',
            values='search_volume_index',
            aggfunc='first',
        )
        
        fig = px.line(
            df_pivot.reset_index(),
            x='signal_date',
            y=df_pivot.columns.tolist(),
            title='Google Trends — Volumen de Búsqueda',
            labels={'signal_date': 'Fecha', 'value': 'Índice de Búsqueda'},
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Average by query
        st.subheader("Promedio por Query")
        avg_by_query = df_gt.groupby('source_metric')['search_volume_index'].mean().sort_values(ascending=False)
        
        fig = px.bar(
            x=avg_by_query.index,
            y=avg_by_query.values,
            title='Volumen Promedio por Query',
            labels={'x': 'Query', 'y': 'Índice Promedio'},
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de Google Trends disponibles.")

# Tab 4: Airbnb Prices
with tab4:
    st.header("Airbnb Prices — Precios por Segmento")
    
    # Load Airbnb data
    airbnb_file = Path("data/v2_market/raw/airbnb/airbnb_mallorca_prices.csv")
    if airbnb_file.exists():
        df_airbnb = pd.read_csv(airbnb_file)
        
        # Filter by segment if selected
        if segment:
            df_segment = df_airbnb[df_airbnb['segment'] == segment]
        else:
            df_segment = df_airbnb
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.box(
                df_segment,
                x='segment',
                y='price_per_night',
                title='Distribución de Precios por Segmento',
                labels={'segment': 'Segmento', 'price_per_night': 'Precio (EUR/noche)'},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                df_segment,
                x='bedrooms',
                y='price_per_night',
                color='segment',
                title='Precio vs Habitaciones',
                labels={'bedrooms': 'Habitaciones', 'price_per_night': 'Precio (EUR/noche)'},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistics by segment
        st.subheader("Estadísticas por Segmento")
        stats_by_segment = df_airbnb.groupby('segment').agg({
            'price_per_night': ['mean', 'median', 'min', 'max', 'count'],
            'review_scores_rating': 'mean',
        }).round(0)
        
        st.dataframe(stats_by_segment)
    else:
        st.info("No hay datos de Airbnb disponibles. Ejecuta `scripts/generate_tourism_data.py` primero.")

# Footer
st.markdown("---")
st.markdown("**Optimus Price** — Market Intelligence Dashboard v2.0")
st.markdown(f"Base de datos: `{db.db_path}`")
