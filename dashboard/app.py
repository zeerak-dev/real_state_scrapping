import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db_ops, db_manager, PropertyListing
from config.settings import Config

# Configure Streamlit page
st.set_page_config(
    page_title="Pakistan Real Estate Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .sidebar-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class DashboardApp:
    def __init__(self):
        self.config = Config()
        
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_property_data(_self):
        """Load property data from database"""
        try:
            session = db_manager.get_session()
            properties = session.query(PropertyListing).filter(
                PropertyListing.is_duplicate == False
            ).all()
            session.close()
            
            if not properties:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for prop in properties:
                data.append({
                    'id': prop.id,
                    'title': prop.title,
                    'city': prop.city,
                    'area': prop.area or 'Unknown',
                    'sector_block': prop.sector_block or '',
                    'price_pkr': prop.price_pkr,
                    'price_per_sqft': prop.price_per_sqft,
                    'property_type': prop.property_type or 'Other',
                    'bedrooms': prop.bedrooms,
                    'bathrooms': prop.bathrooms,
                    'area_size': prop.area_size,
                    'area_unit': prop.area_unit or '',
                    'agent_name': prop.agent_name or '',
                    'contact_phone': prop.contact_phone or '',
                    'source_website': prop.source_website,
                    'date_scraped': prop.date_scraped,
                    'data_quality_score': prop.data_quality_score or 0
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)
    def get_summary_stats(_self, df):
        """Calculate summary statistics"""
        if df.empty:
            return {}
        
        stats = {
            'total_properties': len(df),
            'total_cities': df['city'].nunique(),
            'avg_price': df['price_pkr'].mean() if 'price_pkr' in df.columns else 0,
            'median_price': df['price_pkr'].median() if 'price_pkr' in df.columns else 0,
            'price_properties': df['price_pkr'].notna().sum() if 'price_pkr' in df.columns else 0,
            'avg_area': df['area_size'].mean() if 'area_size' in df.columns else 0,
            'websites': df['source_website'].nunique() if 'source_website' in df.columns else 0
        }
        
        return stats
    
    def create_price_distribution_chart(self, df, city_filter=None):
        """Create price distribution chart"""
        if df.empty or 'price_pkr' not in df.columns:
            return go.Figure()
        
        filtered_df = df.copy()
        if city_filter and city_filter != 'All':
            filtered_df = filtered_df[filtered_df['city'] == city_filter]
        
        # Remove outliers for better visualization
        q1 = filtered_df['price_pkr'].quantile(0.25)
        q3 = filtered_df['price_pkr'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        plot_df = filtered_df[
            (filtered_df['price_pkr'] >= lower_bound) & 
            (filtered_df['price_pkr'] <= upper_bound) &
            (filtered_df['price_pkr'].notna())
        ]
        
        if plot_df.empty:
            return go.Figure()
        
        fig = px.histogram(
            plot_df, 
            x='price_pkr', 
            color='city',
            title='Price Distribution by City',
            labels={'price_pkr': 'Price (PKR)', 'count': 'Number of Properties'},
            nbins=30
        )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            xaxis_tickformat=',.0f'
        )
        
        return fig
    
    def create_city_comparison_chart(self, df):
        """Create city comparison chart"""
        if df.empty or 'city' not in df.columns:
            return go.Figure()
        
        city_stats = df.groupby('city').agg({
            'price_pkr': ['mean', 'median', 'count'],
            'area_size': 'mean'
        }).round(0)
        
        city_stats.columns = ['avg_price', 'median_price', 'property_count', 'avg_area']
        city_stats = city_stats.reset_index()
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Average Property Prices by City', 'Property Count by City'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Price chart
        fig.add_trace(
            go.Bar(
                x=city_stats['city'],
                y=city_stats['avg_price'],
                name='Avg Price',
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # Count chart
        fig.add_trace(
            go.Bar(
                x=city_stats['city'],
                y=city_stats['property_count'],
                name='Property Count',
                marker_color='lightcoral'
            ),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        fig.update_yaxes(tickformat=',.0f', row=1, col=1)
        
        return fig
    
    def create_top_areas_chart(self, df, limit=10):
        """Create top expensive areas chart"""
        if df.empty or not all(col in df.columns for col in ['area', 'city', 'price_pkr']):
            return go.Figure()
        
        # Calculate average price by area
        area_stats = df.groupby(['city', 'area']).agg({
            'price_pkr': ['mean', 'count']
        }).round(0)
        
        area_stats.columns = ['avg_price', 'property_count']
        area_stats = area_stats.reset_index()
        
        # Filter areas with at least 3 properties
        area_stats = area_stats[area_stats['property_count'] >= 3]
        area_stats = area_stats.nlargest(limit, 'avg_price')
        
        if area_stats.empty:
            return go.Figure()
        
        # Create area labels
        area_stats['area_label'] = area_stats['area'] + ', ' + area_stats['city']
        
        fig = px.bar(
            area_stats,
            x='avg_price',
            y='area_label',
            orientation='h',
            title=f'Top {limit} Most Expensive Areas',
            labels={'avg_price': 'Average Price (PKR)', 'area_label': 'Area'},
            color='avg_price',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            xaxis_tickformat=',.0f'
        )
        
        return fig
    
    def create_property_type_chart(self, df):
        """Create property type distribution chart"""
        if df.empty or 'property_type' not in df.columns:
            return go.Figure()
        
        type_counts = df['property_type'].value_counts()
        
        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title='Property Type Distribution'
        )
        
        fig.update_layout(height=400)
        return fig
    
    def render_dashboard(self):
        """Render the main dashboard"""
        st.markdown('<h1 class="main-header">🏠 Pakistan Real Estate Analytics</h1>', unsafe_allow_html=True)
        
        # Load data
        with st.spinner("Loading property data..."):
            df = self.load_property_data()
        
        if df.empty:
            st.warning("No data available. Please run the scraper first using: `python main.py scrape`")
            st.info("To get started:\n1. Install dependencies: `pip install -r requirements.txt`\n2. Setup database configuration in `.env`\n3. Initialize database: `python main.py init`\n4. Run scraper: `python main.py scrape`")
            return
        
        # Sidebar filters
        st.sidebar.header("🔍 Filters")
        
        cities = ['All'] + sorted(df['city'].unique().tolist())
        selected_city = st.sidebar.selectbox("Select City", cities)
        
        property_types = ['All'] + sorted(df['property_type'].unique().tolist())
        selected_type = st.sidebar.selectbox("Select Property Type", property_types)
        
        # Price range filter
        if 'price_pkr' in df.columns and df['price_pkr'].notna().sum() > 0:
            price_min = int(df['price_pkr'].min())
            price_max = int(df['price_pkr'].max())
            price_range = st.sidebar.slider(
                "Price Range (PKR)",
                min_value=price_min,
                max_value=price_max,
                value=(price_min, price_max),
                format="PKR %d"
            )
        
        # Apply filters
        filtered_df = df.copy()
        if selected_city != 'All':
            filtered_df = filtered_df[filtered_df['city'] == selected_city]
        if selected_type != 'All':
            filtered_df = filtered_df[filtered_df['property_type'] == selected_type]
        if 'price_range' in locals():
            filtered_df = filtered_df[
                (filtered_df['price_pkr'].between(price_range[0], price_range[1])) |
                (filtered_df['price_pkr'].isna())
            ]
        
        # Summary statistics
        stats = self.get_summary_stats(filtered_df)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Properties", 
                f"{stats.get('total_properties', 0):,}",
                delta=None
            )
        
        with col2:
            avg_price = stats.get('avg_price', 0)
            st.metric(
                "Average Price", 
                f"PKR {avg_price:,.0f}" if avg_price else "N/A",
                delta=None
            )
        
        with col3:
            st.metric(
                "Cities Covered", 
                stats.get('total_cities', 0),
                delta=None
            )
        
        with col4:
            st.metric(
                "Data Sources", 
                stats.get('websites', 0),
                delta=None
            )
        
        # Charts
        st.markdown("---")
        
        # Row 1: Price distribution and city comparison
        col1, col2 = st.columns(2)
        
        with col1:
            price_chart = self.create_price_distribution_chart(filtered_df, selected_city)
            st.plotly_chart(price_chart, use_container_width=True)
        
        with col2:
            city_chart = self.create_city_comparison_chart(filtered_df)
            st.plotly_chart(city_chart, use_container_width=True)
        
        # Row 2: Top areas and property types
        col1, col2 = st.columns(2)
        
        with col1:
            areas_chart = self.create_top_areas_chart(filtered_df)
            st.plotly_chart(areas_chart, use_container_width=True)
        
        with col2:
            type_chart = self.create_property_type_chart(filtered_df)
            st.plotly_chart(type_chart, use_container_width=True)
        
        # Property listings table
        st.markdown("---")
        st.subheader("📋 Property Listings")
        
        # Display controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_count = st.selectbox("Show properties", [50, 100, 200, 500], index=1)
        
        with col2:
            sort_by = st.selectbox("Sort by", ['date_scraped', 'price_pkr', 'area_size', 'data_quality_score'])
        
        with col3:
            sort_order = st.selectbox("Order", ['Descending', 'Ascending'])
        
        # Prepare display dataframe
        display_df = filtered_df.head(show_count).copy()
        
        if not display_df.empty:
            # Sort data
            ascending = sort_order == 'Ascending'
            if sort_by in display_df.columns:
                display_df = display_df.sort_values(sort_by, ascending=ascending)
            
            # Select columns for display
            display_columns = [
                'title', 'city', 'area', 'price_pkr', 'property_type', 
                'bedrooms', 'bathrooms', 'area_size', 'source_website'
            ]
            
            available_columns = [col for col in display_columns if col in display_df.columns]
            display_df = display_df[available_columns]
            
            # Format price column
            if 'price_pkr' in display_df.columns:
                display_df['price_pkr'] = display_df['price_pkr'].apply(
                    lambda x: f"PKR {x:,.0f}" if pd.notna(x) else "N/A"
                )
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
        
        # Sidebar info
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Data Info")
        st.sidebar.info(f"""
        **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        **Total Records**: {len(df):,}
        
        **Data Sources**: 
        - Zameen.com
        - Graana.com
        
        **Cities Covered**:
        {', '.join(sorted(df['city'].unique())) if not df.empty else 'None'}
        """)
        
        # Export functionality
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💾 Export Data")
        
        if st.sidebar.button("Export to CSV"):
            try:
                csv_data = filtered_df.to_csv(index=False)
                st.sidebar.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"properties_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.sidebar.success("CSV ready for download!")
            except Exception as e:
                st.sidebar.error(f"Export failed: {str(e)}")

def main():
    app = DashboardApp()
    app.render_dashboard()

if __name__ == "__main__":
    main()