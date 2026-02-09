#!/usr/bin/env python3
"""
GLP-1 Formulary Intelligence App
Built with Streamlit

Run with: streamlit run app_streamlit.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from extract_glp1_coverage import GLP1CoverageExtractor

# Page config
st.set_page_config(
    page_title="GLP-1 Formulary Intelligence",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        padding-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .product-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">💊 GLP-1 Formulary Intelligence Platform</p>', unsafe_allow_html=True)
st.markdown("**Automated Medicare Part D Coverage Analysis**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📁 Data Input")
    
    data_source = st.radio(
        "Choose data source:",
        ["Use Demo Data (848 plans)", "Upload CMS Files"]
    )
    
    if data_source == "Upload CMS Files":
        st.info("📤 Upload the three required CMS files:")
        
        plan_file = st.file_uploader("Plan Information (.txt)", type=['txt'])
        formulary_file = st.file_uploader("Basic Drugs Formulary (.txt)", type=['txt'])
        cost_file = st.file_uploader("Beneficiary Cost (.txt)", type=['txt'])
        
        if st.button("🚀 Extract Coverage Data"):
            if plan_file and formulary_file and cost_file:
                with st.spinner("Extracting coverage data..."):
                    # Save uploaded files
                    temp_dir = Path("temp_upload")
                    temp_dir.mkdir(exist_ok=True)
                    
                    (temp_dir / "plan_information.txt").write_bytes(plan_file.read())
                    (temp_dir / "basic_drugs_formulary.txt").write_bytes(formulary_file.read())
                    (temp_dir / "beneficiary_cost.txt").write_bytes(cost_file.read())
                    
                    # Run extraction
                    extractor = GLP1CoverageExtractor(temp_dir)
                    coverage_list = extractor.extract_coverage()
                    
                    # Store in session state
                    st.session_state['coverage_data'] = coverage_list
                    st.session_state['data_loaded'] = True
                    st.success("✅ Extraction complete!")
            else:
                st.error("Please upload all three files")
    else:
        # Use demo data
        demo_path = Path("sample_data")
        if demo_path.exists():
            if st.button("📊 Load Demo Data"):
                with st.spinner("Loading demo data..."):
                    extractor = GLP1CoverageExtractor(demo_path)
                    coverage_list = extractor.extract_coverage()
                    st.session_state['coverage_data'] = coverage_list
                    st.session_state['data_loaded'] = True
                    st.success("✅ Demo data loaded!")
        else:
            st.warning("Demo data not found. Please upload CMS files.")

# Main content
if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
    
    # Convert to DataFrame
    df = pd.DataFrame([vars(c) for c in st.session_state['coverage_data']])
    
    # Overview metrics
    st.header("📊 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Plans",
            f"{df['plan_id'].nunique():,}",
            help="Unique Medicare Part D plans analyzed"
        )
    
    with col2:
        st.metric(
            "Coverage Records",
            f"{len(df):,}",
            help="Total plan-product combinations"
        )
    
    with col3:
        avg_score = df['access_score'].mean()
        st.metric(
            "Avg Access Score",
            f"{avg_score:.1f}/100",
            help="Higher = better access"
        )
    
    with col4:
        pa_rate = (df['prior_auth'].sum() / len(df)) * 100
        st.metric(
            "PA Rate",
            f"{pa_rate:.1f}%",
            help="% of coverage requiring prior authorization"
        )
    
    st.markdown("---")
    
    # Product comparison
    st.header("🏆 Product Comparison")
    
    product_stats = df.groupby('product_name').agg({
        'plan_id': 'count',
        'access_score': 'mean',
        'prior_auth': lambda x: (x.sum() / len(x)) * 100,
        'step_therapy': lambda x: (x.sum() / len(x)) * 100,
    }).round(1)
    
    product_stats.columns = ['Plans Covering', 'Avg Access Score', 'PA Rate (%)', 'ST Rate (%)']
    product_stats = product_stats.sort_values('Avg Access Score', ascending=False)
    
    # Access score chart
    fig_access = px.bar(
        product_stats.reset_index(),
        x='product_name',
        y='Avg Access Score',
        color='Avg Access Score',
        color_continuous_scale='RdYlGn',
        title='Average Access Score by Product',
        labels={'product_name': 'Product', 'Avg Access Score': 'Access Score (0-100)'}
    )
    fig_access.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_access, use_container_width=True)
    
    # Product stats table
    st.dataframe(product_stats, use_container_width=True)
    
    st.markdown("---")
    
    # Administrative friction
    st.header("🚧 Administrative Friction Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PA rates by product
        pa_data = df.groupby('product_name')['prior_auth'].apply(
            lambda x: (x.sum() / len(x)) * 100
        ).reset_index()
        pa_data.columns = ['Product', 'PA Rate (%)']
        
        fig_pa = px.bar(
            pa_data,
            x='Product',
            y='PA Rate (%)',
            color='PA Rate (%)',
            color_continuous_scale='Reds',
            title='Prior Authorization Rates'
        )
        fig_pa.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_pa, use_container_width=True)
    
    with col2:
        # ST rates by product
        st_data = df.groupby('product_name')['step_therapy'].apply(
            lambda x: (x.sum() / len(x)) * 100
        ).reset_index()
        st_data.columns = ['Product', 'ST Rate (%)']
        
        fig_st = px.bar(
            st_data,
            x='Product',
            y='ST Rate (%)',
            color='ST Rate (%)',
            color_continuous_scale='Oranges',
            title='Step Therapy Rates'
        )
        fig_st.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_st, use_container_width=True)
    
    st.markdown("---")
    
    # Tier distribution
    st.header("📊 Tier Distribution")
    
    tier_dist = df.groupby(['product_name', 'tier']).size().reset_index(name='count')
    
    fig_tier = px.bar(
        tier_dist,
        x='product_name',
        y='count',
        color='tier',
        title='Tier Distribution by Product',
        labels={'product_name': 'Product', 'count': 'Number of Plans'},
        barmode='stack'
    )
    fig_tier.update_layout(height=400)
    st.plotly_chart(fig_tier, use_container_width=True)
    
    st.markdown("---")
    
    # Organization analysis
    st.header("🏢 Top Organizations")
    
    org_stats = df.groupby('organization_name').agg({
        'plan_id': 'count',
        'access_score': 'mean',
        'prior_auth': lambda x: (x.sum() / len(x)) * 100,
    }).round(1)
    
    org_stats.columns = ['Coverage Records', 'Avg Access Score', 'PA Rate (%)']
    org_stats = org_stats.sort_values('Coverage Records', ascending=False).head(10)
    
    st.dataframe(org_stats, use_container_width=True)
    
    st.markdown("---")
    
    # Plan lookup
    st.header("🔍 Plan Lookup Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_org = st.selectbox(
            "Select Organization:",
            options=['All'] + sorted(df['organization_name'].unique().tolist())
        )
    
    with col2:
        selected_product = st.selectbox(
            "Select Product:",
            options=['All'] + sorted(df['product_name'].unique().tolist())
        )
    
    # Filter data
    filtered_df = df.copy()
    if selected_org != 'All':
        filtered_df = filtered_df[filtered_df['organization_name'] == selected_org]
    if selected_product != 'All':
        filtered_df = filtered_df[filtered_df['product_name'] == selected_product]
    
    # Display results
    st.write(f"**Showing {len(filtered_df)} plans**")
    
    display_cols = [
        'plan_name', 'product_name', 'tier', 
        'prior_auth', 'step_therapy', 'quantity_limit',
        'retail_preferred_cost', 'access_score'
    ]
    
    st.dataframe(
        filtered_df[display_cols].sort_values('access_score', ascending=False),
        use_container_width=True,
        height=400
    )
    
    st.markdown("---")
    
    # Export options
    st.header("💾 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv_data,
            file_name="glp1_coverage_analysis.csv",
            mime="text/csv"
        )
    
    with col2:
        summary_stats = {
            'total_records': len(df),
            'unique_plans': df['plan_id'].nunique(),
            'avg_access_score': float(df['access_score'].mean()),
            'pa_rate': float((df['prior_auth'].sum() / len(df)) * 100),
            'st_rate': float((df['step_therapy'].sum() / len(df)) * 100),
        }
        
        import json
        json_data = json.dumps(summary_stats, indent=2)
        
        st.download_button(
            label="📥 Download Summary (JSON)",
            data=json_data,
            file_name="summary_stats.json",
            mime="application/json"
        )
    
    with col3:
        # Excel export (requires openpyxl)
        st.info("💡 Excel export: Install openpyxl first")

else:
    # Welcome screen
    st.info("👈 **Get started:** Load demo data or upload CMS files from the sidebar")
    
    st.markdown("""
    ### What This App Does
    
    - ✅ **Extracts** formulary coverage from Medicare Part D data
    - ✅ **Analyzes** access patterns for GLP-1 drugs
    - ✅ **Visualizes** PA rates, tier placement, and access scores
    - ✅ **Exports** results for further analysis
    
    ### Data Sources
    
    - **Demo Data**: Pre-loaded 848 Medicare Part D plans
    - **Upload CMS Files**: Use your own January 2026 (or any month) data
    
    ### Products Analyzed
    
    - **Wegovy** (semaglutide, obesity)
    - **Ozempic** (semaglutide, diabetes)
    - **Zepbound** (tirzepatide, obesity)
    - **Mounjaro** (tirzepatide, diabetes)
    """)

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Data source: CMS Medicare Part D Public Use Files")
