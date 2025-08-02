
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import sqlite3
import io
from datetime import datetime
import re
from enhanced_aws_login import AWSPortalClient
import numpy as np
import tempfile
import os
import pickle
import uuid
from typing import Dict, List, Any, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Professional NLP to SQL Analytics Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Professional CSS Styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }

    /* Professional Header */
    .professional-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }

    .professional-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .professional-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }

    /* Stage Cards */
    .stage-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 5px 25px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
        transition: all 0.3s ease;
    }

    .stage-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 35px rgba(0,0,0,0.12);
    }

    .stage-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        font-weight: 600;
        font-size: 1.3rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    /* Progress Bar */
    .progress-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 0.3rem;
        margin: 1rem 0;
    }

    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 0.6rem;
        border-radius: 8px;
        transition: width 0.5s ease;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }

    .success-box {
        background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #2d5016;
        border-left: 5px solid #28a745;
    }

    .warning-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #856404;
        border-left: 5px solid #ffc107;
    }

    .error-box {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #721c24;
        border-left: 5px solid #dc3545;
    }

    /* File Upload Area */
    .file-upload-area {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
        transition: all 0.3s ease;
    }

    .file-upload-area:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #f0f2ff 0%, #e8ebff 100%);
    }

    /* Join Builder */
    .join-builder {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #667eea;
    }

    .join-condition {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    /* SQL Editor */
    .sql-editor {
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: #ecf0f1;
        border-radius: 10px;
        padding: 1.5rem;
        border: none;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }

    /* Data Preview */
    .data-preview {
        max-height: 400px;
        overflow-y: auto;
        border: 2px solid #e1e8ed;
        border-radius: 12px;
        padding: 1rem;
        background: white;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Navigation Pills */
    .nav-pill {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        margin: 0.3rem;
        text-align: center;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
    }

    .nav-pill:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .nav-pill.active {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    /* Custom Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }

    /* Chart Container */
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 25px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
    }

    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .status-success { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-error { background-color: #dc3545; }
    .status-info { background-color: #17a2b8; }
</style>
""", unsafe_allow_html=True)

# Enhanced Session State Management with Persistence
class SessionManager:
    def __init__(self):
        self.session_id = self._get_or_create_session_id()
        self.temp_dir = tempfile.mkdtemp(prefix=f"nlp_sql_{self.session_id}_")

    def _get_or_create_session_id(self):
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id

    def save_session_data(self, key: str, data: Any):
        """Save data to temporary storage"""
        try:
            file_path = os.path.join(self.temp_dir, f"{key}.pkl")
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            st.session_state[key] = data
        except Exception as e:
            st.error(f"Error saving session data: {str(e)}")

    def load_session_data(self, key: str, default=None):
        """Load data from temporary storage"""
        try:
            if key in st.session_state:
                return st.session_state[key]

            file_path = os.path.join(self.temp_dir, f"{key}.pkl")
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                st.session_state[key] = data
                return data
        except Exception as e:
            st.error(f"Error loading session data: {str(e)}")

        return default

    def save_uploaded_file(self, uploaded_file, filename: str):
        """Save uploaded file to temporary storage"""
        try:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        except Exception as e:
            st.error(f"Error saving uploaded file: {str(e)}")
            return None

# Initialize Session Manager
@st.cache_resource
def get_session_manager():
    return SessionManager()

# Enhanced initialization with persistence
def initialize_session_state():
    session_manager = get_session_manager()

    # Load or initialize session state variables
    default_values = {
        'authenticated': False,
        'aws_client': None,
        'bedrock_client': None,
        'uploaded_files': {},
        'uploaded_file_paths': {},
        'join_conditions': [],
        'sql_query': "",
        'query_result': None,
        'current_stage': 1,
        'visualization_settings': {
            'chart_types': ['bar', 'line', 'scatter', 'pie', 'histogram', 'box', 'heatmap'],
            'color_schemes': ['viridis', 'plasma', 'inferno', 'magma', 'plotly', 'rainbow'],
            'animation_enabled': True,
            'interactive_enabled': True
        },
        'query_history': [],
        'favorite_queries': [],
        'last_activity': datetime.now().isoformat()
    }

    for key, default_value in default_values.items():
        if key not in st.session_state:
            loaded_value = session_manager.load_session_data(key, default_value)
            st.session_state[key] = loaded_value

# Enhanced AWS Authentication
def authenticate_aws(username, password, account_id, region):
    try:
        with st.spinner("🔐 Authenticating with AWS..."):
            aws_client = AWSPortalClient(username=username, password=password)
            token = aws_client.gather_token()
            credentials = aws_client.gather_credentials(token, account_id)
            if credentials:
                bedrock_client = aws_client.create_client(credentials, 'bedrock-runtime', region)
                if bedrock_client:
                    st.session_state.aws_client = aws_client
                    st.session_state.bedrock_client = bedrock_client
                    st.session_state.authenticated = True

                    # Save authentication state
                    session_manager = get_session_manager()
                    session_manager.save_session_data('authenticated', True)

                    return True
            return False
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return False

# Enhanced SQL Generation
def generate_sql_with_bedrock(natural_language_query, table_schemas, join_conditions, bedrock_client):
    try:
        # Create a comprehensive prompt
        tables_info = ""
        for table_name, schema in table_schemas.items():
            tables_info += f"\nTable: {table_name}\n"
            tables_info += f"Schema: {schema}\n"

        joins_info = ""
        if join_conditions:
            joins_info = "\nJoin Conditions:\n"
            for i, join in enumerate(join_conditions):
                joins_info += f"{i+1}. {join['left_table']}.{join['left_column']} {join['join_type']} {join['right_table']}.{join['right_column']}\n"

        prompt = f"""
You are an expert SQL developer. Generate a precise SQL query based on the following information:

{tables_info}
{joins_info}

Natural Language Query: {natural_language_query}

Instructions:
1. Generate only valid SQL syntax
2. Use appropriate WHERE clauses, JOINs, GROUP BY, ORDER BY as needed
3. Follow the specified join conditions
4. Use table aliases for better readability
5. Return only the SQL query without explanation
6. Optimize for performance

SQL Query:
"""

        message = [{"role": "user", "content": [{"text": prompt}]}]
        model_id = 'anthropic.claude-3-sonnet-20240620-v1:0'

        response = bedrock_client.converse(modelId=model_id, messages=message)
        output_text = response['output']['message']
        sql_query = ''
        for content in output_text['content']:
            sql_query += content['text']

        # Clean up the SQL query
        sql_query = sql_query.strip()
        sql_query = re.sub(r'```sql', '', sql_query)
        sql_query = re.sub(r'```', '', sql_query)
        sql_query = sql_query.strip()

        # Save to query history
        if sql_query:
            query_entry = {
                'timestamp': datetime.now().isoformat(),
                'natural_query': natural_language_query,
                'sql_query': sql_query
            }
            if 'query_history' not in st.session_state:
                st.session_state.query_history = []
            st.session_state.query_history.append(query_entry)

            # Save to session
            session_manager = get_session_manager()
            session_manager.save_session_data('query_history', st.session_state.query_history)

        return sql_query
    except Exception as e:
        st.error(f"Error generating SQL: {str(e)}")
        return None

# Enhanced SQL Execution
def execute_sql_query(sql_query, dataframes_dict):
    try:
        conn = sqlite3.connect(':memory:')

        for table_name, df in dataframes_dict.items():
            df.to_sql(table_name, conn, index=False, if_exists='replace')

        result = pd.read_sql_query(sql_query, conn)
        conn.close()

        return result
    except Exception as e:
        st.error(f"Error executing SQL query: {str(e)}")
        return None

# Dynamic Advanced Visualization Engine
def create_dynamic_visualizations(data, query_description, user_preferences=None):
    """Create multiple dynamic and interactive visualizations"""
    if data is None or data.empty:
        return None

    charts = []
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = []

    # Detect datetime columns
    for col in data.columns:
        if pd.api.types.is_datetime64_any_dtype(data[col]) or 'date' in col.lower() or 'time' in col.lower():
            try:
                data[col] = pd.to_datetime(data[col])
                datetime_cols.append(col)
            except:
                pass

    # Get user preferences
    viz_settings = st.session_state.get('visualization_settings', {})
    color_scheme = viz_settings.get('color_schemes', ['plotly'])[0]

    # 1. Enhanced Bar Chart with animations
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        fig_bar = px.bar(
            data,
            x=categorical_cols[0],
            y=numeric_cols[0],
            title=f"📊 Interactive Bar Chart: {categorical_cols[0]} vs {numeric_cols[0]}",
            color=categorical_cols[0] if len(data) < 50 else None,
            color_discrete_sequence=px.colors.qualitative.Set3,
            hover_data=numeric_cols[:3] if len(numeric_cols) > 1 else None
        )

        fig_bar.update_layout(
            title_font_size=16,
            title_x=0.5,
            showlegend=len(data) < 20,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif")
        )

        fig_bar.update_traces(
            hovertemplate='<b>%{x}</b><br>%{y:,.0f}<extra></extra>',
            marker_line_width=1,
            marker_line_color='white'
        )

        charts.append(("📊 Interactive Bar Chart", fig_bar))

    # 2. Advanced Line Chart with multiple series
    if len(numeric_cols) >= 2:
        fig_line = go.Figure()

        for i, col in enumerate(numeric_cols[:3]):  # Limit to 3 series
            fig_line.add_trace(go.Scatter(
                x=data.index if not datetime_cols else data[datetime_cols[0]],
                y=data[col],
                mode='lines+markers',
                name=col,
                line=dict(width=3),
                marker=dict(size=6),
                hovertemplate=f'<b>{col}</b><br>Value: %{{y:,.2f}}<extra></extra>'
            ))

        fig_line.update_layout(
            title=f"📈 Multi-Series Line Chart",
            title_x=0.5,
            title_font_size=16,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        charts.append(("📈 Multi-Series Line Chart", fig_line))

    # 3. Enhanced Scatter Plot with regression line
    if len(numeric_cols) >= 2:
        fig_scatter = px.scatter(
            data,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=f"🔍 Advanced Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}",
            color=categorical_cols[0] if categorical_cols else None,
            size=numeric_cols[2] if len(numeric_cols) > 2 else None,
            hover_data=categorical_cols[:2] if categorical_cols else None,
            trendline="ols" if len(data) > 10 else None,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig_scatter.update_layout(
            title_x=0.5,
            title_font_size=16,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif")
        )

        charts.append(("🔍 Advanced Scatter Plot", fig_scatter))

    # 4. Interactive Pie Chart
    if len(categorical_cols) >= 1:
        value_counts = data[categorical_cols[0]].value_counts().head(10)
        fig_pie = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f"🥧 Interactive Pie Chart: {categorical_cols[0]} Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )

        fig_pie.update_layout(
            title_x=0.5,
            title_font_size=16,
            font=dict(family="Inter, sans-serif")
        )

        charts.append(("🥧 Interactive Pie Chart", fig_pie))

    # 5. Box Plot for distribution analysis
    if len(numeric_cols) >= 1:
        fig_box = px.box(
            data,
            y=numeric_cols[0],
            x=categorical_cols[0] if categorical_cols else None,
            title=f"📦 Distribution Analysis: {numeric_cols[0]}",
            color=categorical_cols[0] if categorical_cols else None,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig_box.update_layout(
            title_x=0.5,
            title_font_size=16,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif")
        )

        charts.append(("📦 Distribution Analysis", fig_box))

    # 6. Histogram with KDE
    if len(numeric_cols) >= 1:
        fig_hist = px.histogram(
            data,
            x=numeric_cols[0],
            title=f"📊 Histogram: {numeric_cols[0]} Distribution",
            nbins=30,
            marginal="box",
            color_discrete_sequence=['#667eea']
        )

        fig_hist.update_layout(
            title_x=0.5,
            title_font_size=16,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif")
        )

        charts.append(("📊 Histogram Analysis", fig_hist))

    # 7. Correlation Heatmap
    if len(numeric_cols) >= 2:
        corr_matrix = data[numeric_cols].corr()

        fig_heatmap = px.imshow(
            corr_matrix,
            title="🔥 Correlation Heatmap",
            color_continuous_scale="RdBu",
            aspect="auto",
            text_auto=True
        )

        fig_heatmap.update_layout(
            title_x=0.5,
            title_font_size=16,
            font=dict(family="Inter, sans-serif")
        )

        charts.append(("🔥 Correlation Heatmap", fig_heatmap))

    # 8. Time Series Chart (if datetime columns exist)
    if datetime_cols and len(numeric_cols) >= 1:
        fig_time = px.line(
            data,
            x=datetime_cols[0],
            y=numeric_cols[0],
            title=f"⏰ Time Series: {numeric_cols[0]} over {datetime_cols[0]}",
            markers=True
        )

        fig_time.update_layout(
            title_x=0.5,
            title_font_size=16,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif")
        )

        charts.append(("⏰ Time Series Analysis", fig_time))

    return charts

# Progress tracking
def display_progress_bar(current_stage):
    progress = (current_stage - 1) / 3 * 100

    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress}%"></div>
    </div>
    <p style="text-align: center; margin-top: 0.5rem; color: #666;">
        Stage {current_stage} of 4 - {progress:.0f}% Complete
    </p>
    """, unsafe_allow_html=True)

# Professional File Upload Interface
def display_professional_file_upload():
    st.markdown("""
    <div class="professional-header fade-in-up">
        <h1>📁 Data Upload Center</h1>
        <p>Upload and manage your CSV files with advanced preview capabilities</p>
    </div>
    """, unsafe_allow_html=True)

    display_progress_bar(1)

    # File upload section with enhanced UI
    with st.container():
        st.markdown('<div class="stage-card">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            uploaded_files = st.file_uploader(
                "🔄 Choose CSV files to upload",
                type=['csv'],
                accept_multiple_files=True,
                help="Upload multiple CSV files for analysis and joining. Supports large files up to 200MB each.",
                key="file_uploader_main"
            )

        if uploaded_files:
            session_manager = get_session_manager()
            st.session_state.uploaded_files = {}
            st.session_state.uploaded_file_paths = {}

            # Display upload summary
            st.markdown("### 📊 Upload Summary")

            total_size = sum([file.size for file in uploaded_files])
            total_rows = 0

            cols = st.columns(4)
            with cols[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(uploaded_files)}</div>
                    <div class="metric-label">Files Uploaded</div>
                </div>
                """, unsafe_allow_html=True)

            with cols[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_size / (1024*1024):.1f} MB</div>
                    <div class="metric-label">Total Size</div>
                </div>
                """, unsafe_allow_html=True)

            # Process each file
            for uploaded_file in uploaded_files:
                try:
                    df = pd.read_csv(uploaded_file)
                    table_name = uploaded_file.name.replace('.csv', '').replace(' ', '_').lower()

                    # Save file and data
                    st.session_state.uploaded_files[table_name] = df
                    file_path = session_manager.save_uploaded_file(uploaded_file, uploaded_file.name)
                    st.session_state.uploaded_file_paths[table_name] = file_path

                    total_rows += len(df)

                    # Enhanced file preview
                    with st.expander(f"📋 {uploaded_file.name} - {len(df):,} rows × {len(df.columns)} columns", expanded=False):

                        # File statistics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Rows", f"{len(df):,}")
                        with col2:
                            st.metric("Columns", len(df.columns))
                        with col3:
                            st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
                        with col4:
                            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                            st.metric("Missing %", f"{missing_pct:.1f}%")

                        # Data types and quality
                        tab1, tab2, tab3 = st.tabs(["🔍 Preview", "📋 Schema", "⚠️ Quality"])

                        with tab1:
                            st.markdown("**First 10 rows:**")
                            st.dataframe(df.head(10), use_container_width=True)

                            st.markdown("**Last 5 rows:**")
                            st.dataframe(df.tail(5), use_container_width=True)

                        with tab2:
                            schema_df = pd.DataFrame({
                                'Column': df.columns,
                                'Data Type': df.dtypes.astype(str),
                                'Non-Null Count': df.count(),
                                'Null Count': df.isnull().sum(),
                                'Null %': (df.isnull().sum() / len(df) * 100).round(2),
                                'Unique Values': df.nunique()
                            })
                            st.dataframe(schema_df, use_container_width=True)

                        with tab3:
                            # Data quality indicators
                            quality_issues = []

                            # Check for missing values
                            missing_cols = df.columns[df.isnull().any()].tolist()
                            if missing_cols:
                                quality_issues.append(f"Missing values in: {', '.join(missing_cols)}")

                            # Check for duplicate rows
                            if df.duplicated().any():
                                dup_count = df.duplicated().sum()
                                quality_issues.append(f"Duplicate rows: {dup_count}")

                            # Check for potential issues
                            numeric_cols = df.select_dtypes(include=[np.number]).columns
                            for col in numeric_cols:
                                if (df[col] < 0).any():
                                    quality_issues.append(f"Negative values in: {col}")

                            if quality_issues:
                                for issue in quality_issues:
                                    st.warning(f"⚠️ {issue}")
                            else:
                                st.success("✅ No major data quality issues detected")

                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")

            # Update total rows metric
            with cols[2]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_rows:,}</div>
                    <div class="metric-label">Total Rows</div>
                </div>
                """, unsafe_allow_html=True)

            with cols[3]:
                avg_cols = sum([len(df.columns) for df in st.session_state.uploaded_files.values()]) / len(st.session_state.uploaded_files)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_cols:.0f}</div>
                    <div class="metric-label">Avg Columns</div>
                </div>
                """, unsafe_allow_html=True)

            # Save session data
            session_manager.save_session_data('uploaded_files', st.session_state.uploaded_files)
            session_manager.save_session_data('uploaded_file_paths', st.session_state.uploaded_file_paths)

            if len(st.session_state.uploaded_files) >= 1:
                st.success(f"✅ Successfully processed {len(st.session_state.uploaded_files)} file(s)!")

                # Action buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("➡️ Continue to Join Configuration", key="continue_to_joins", type="primary"):
                        st.session_state.current_stage = 2
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    return len(st.session_state.uploaded_files) > 0

# Enhanced Join Builder with Visual Interface
def display_advanced_join_builder():
    st.markdown("""
    <div class="professional-header fade-in-up">
        <h1>🔗 Advanced Join Configuration</h1>
        <p>Create sophisticated relationships between your data tables</p>
    </div>
    """, unsafe_allow_html=True)

    display_progress_bar(2)

    if len(st.session_state.uploaded_files) < 2:
        st.info("ℹ️ You have uploaded only one file. You can proceed to SQL generation or upload more files for joining.")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⬅️ Back to Upload", key="back_to_upload"):
                st.session_state.current_stage = 1
                st.rerun()
        with col3:
            if st.button("➡️ Skip to SQL Generation", key="skip_to_sql", type="primary"):
                st.session_state.current_stage = 3
                st.rerun()

        return True

    with st.container():
        st.markdown('<div class="stage-card">', unsafe_allow_html=True)

        # Display available tables
        st.markdown("### 📊 Available Tables")

        table_cols = st.columns(len(st.session_state.uploaded_files))
        for i, (table_name, df) in enumerate(st.session_state.uploaded_files.items()):
            with table_cols[i]:
                st.markdown(f"""
                <div class="info-box">
                    <h4>📋 {table_name}</h4>
                    <p><strong>Rows:</strong> {len(df):,}</p>
                    <p><strong>Columns:</strong> {len(df.columns)}</p>
                    <p><strong>Key Columns:</strong> {', '.join(df.columns[:3])}</p>
                </div>
                """, unsafe_allow_html=True)

        # Current joins display
        if st.session_state.join_conditions:
            st.markdown("### 🔗 Current Join Conditions")

            for i, join in enumerate(st.session_state.join_conditions):
                st.markdown(f"""
                <div class="join-condition">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="status-indicator status-success"></span>
                            <strong>Join {i+1}:</strong> 
                            <code>{join["left_table"]}.{join["left_column"]}</code> 
                            <span style="color: #667eea; font-weight: bold;">{join["join_type"]}</span> 
                            <code>{join["right_table"]}.{join["right_column"]}</code>
                        </div>
                        <button onclick="removeJoin({i})" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">Remove</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Join builder interface
        st.markdown("### ➕ Add New Join")

        with st.container():
            st.markdown('<div class="join-builder">', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🎯 Left Table**")
                left_table = st.selectbox(
                    "Select left table:",
                    options=list(st.session_state.uploaded_files.keys()),
                    key="left_table_select",
                    help="Choose the first table for the join operation"
                )

                if left_table:
                    left_columns = list(st.session_state.uploaded_files[left_table].columns)
                    left_column = st.selectbox(
                        "Select left column:",
                        options=left_columns,
                        key="left_column_select",
                        help="Choose the column from the left table to join on"
                    )

                    # Show sample values
                    if left_column:
                        sample_values = st.session_state.uploaded_files[left_table][left_column].head(5).tolist()
                        st.info(f"Sample values: {', '.join(map(str, sample_values))}")

            with col2:
                st.markdown("**🎯 Right Table**")
                available_right_tables = [t for t in st.session_state.uploaded_files.keys() if t != left_table]
                right_table = st.selectbox(
                    "Select right table:",
                    options=available_right_tables,
                    key="right_table_select",
                    help="Choose the second table for the join operation"
                )

                if right_table:
                    right_columns = list(st.session_state.uploaded_files[right_table].columns)
                    right_column = st.selectbox(
                        "Select right column:",
                        options=right_columns,
                        key="right_column_select",
                        help="Choose the column from the right table to join on"
                    )

                    # Show sample values
                    if right_column:
                        sample_values = st.session_state.uploaded_files[right_table][right_column].head(5).tolist()
                        st.info(f"Sample values: {', '.join(map(str, sample_values))}")

            # Join type with explanations
            st.markdown("**🔄 Join Type**")
            join_type_options = {
                "INNER JOIN": "Returns only matching records from both tables",
                "LEFT JOIN": "Returns all records from left table, matched records from right",
                "RIGHT JOIN": "Returns all records from right table, matched records from left",
                "FULL OUTER JOIN": "Returns all records from both tables"
            }

            join_type = st.selectbox(
                "Select join type:",
                options=list(join_type_options.keys()),
                key="join_type_select",
                help="Choose how the tables should be joined"
            )

            st.info(f"ℹ️ {join_type_options[join_type]}")

            # Add join button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("➕ Add Join Condition", key="add_join_btn", type="primary"):
                    if left_table and right_table and left_column and right_column:
                        join_condition = {
                            "left_table": left_table,
                            "left_column": left_column,
                            "right_table": right_table,
                            "right_column": right_column,
                            "join_type": join_type
                        }
                        st.session_state.join_conditions.append(join_condition)

                        # Save to session
                        session_manager = get_session_manager()
                        session_manager.save_session_data('join_conditions', st.session_state.join_conditions)

                        st.success("✅ Join condition added successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Please select all required fields!")

            st.markdown('</div>', unsafe_allow_html=True)

        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⬅️ Back to Upload", key="back_to_upload_from_joins"):
                st.session_state.current_stage = 1
                st.rerun()

        with col2:
            if st.session_state.join_conditions and st.button("🗑️ Clear All Joins", key="clear_joins_btn"):
                st.session_state.join_conditions = []
                session_manager = get_session_manager()
                session_manager.save_session_data('join_conditions', [])
                st.success("✅ All join conditions cleared!")
                st.rerun()

        with col3:
            if st.button("➡️ Continue to SQL Generation", key="continue_to_sql", type="primary"):
                st.session_state.current_stage = 3
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    return True

# Professional SQL Generation Interface
def display_professional_sql_generation():
    st.markdown("""
    <div class="professional-header fade-in-up">
        <h1>⚡ Intelligent SQL Generation</h1>
        <p>Transform natural language into powerful SQL queries using AI</p>
    </div>
    """, unsafe_allow_html=True)

    display_progress_bar(3)

    with st.container():
        st.markdown('<div class="stage-card">', unsafe_allow_html=True)

        # Authentication check
        if not st.session_state.authenticated:
            st.error("🔐 Please authenticate with AWS Bedrock in the sidebar first!")
            st.markdown('</div>', unsafe_allow_html=True)
            return False

        # Query history sidebar
        if st.session_state.get('query_history', []):
            with st.expander("📚 Query History", expanded=False):
                for i, entry in enumerate(reversed(st.session_state.query_history[-10:])):  # Show last 10
                    timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M")
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                        <strong>{timestamp}</strong><br>
                        <em>{entry['natural_query'][:100]}...</em><br>
                        <code style="font-size: 0.8em;">{entry['sql_query'][:150]}...</code>
                    </div>
                    """, unsafe_allow_html=True)

        # Natural language input
        st.markdown("### 💬 Natural Language Query")

        # Quick examples
        example_queries = [
            "Show me the total sales by region",
            "Find customers with orders over $1000",
            "Calculate average rating by product category",
            "List top 10 products by revenue",
            "Show monthly trends for the last year"
        ]

        selected_example = st.selectbox(
            "💡 Quick Examples (optional):",
            options=[""] + example_queries,
            help="Select an example query or write your own below"
        )

        natural_query = st.text_area(
            "🗣️ Describe what you want to analyze:",
            value=selected_example,
            placeholder="e.g., Show me the total sales by region with product categories, including only orders from the last 6 months...",
            height=120,
            key="natural_query_input",
            help="Be specific about what you want to see, including any filters, grouping, or sorting requirements"
        )

        # Advanced options
        with st.expander("⚙️ Advanced Options", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.checkbox("Include data preview", value=True, key="include_preview")
                st.checkbox("Add comments to SQL", value=True, key="add_comments")
                st.checkbox("Optimize for performance", value=True, key="optimize_performance")

            with col2:
                st.selectbox("SQL Style", ["Standard", "Compact", "Verbose"], key="sql_style")
                st.number_input("Limit results to:", min_value=0, max_value=10000, value=1000, key="result_limit")

        # Generate SQL button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🤖 Generate SQL Query", key="generate_sql_btn", type="primary"):
                if natural_query.strip():
                    with st.spinner("🧠 AI is analyzing your request and generating SQL..."):
                        # Show progress
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)

                        # Prepare table schemas
                        table_schemas = {}
                        for table_name, df in st.session_state.uploaded_files.items():
                            schema = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])
                            table_schemas[table_name] = schema

                        # Generate SQL
                        sql_query = generate_sql_with_bedrock(
                            natural_query,
                            table_schemas,
                            st.session_state.join_conditions,
                            st.session_state.bedrock_client
                        )

                        if sql_query:
                            st.session_state.sql_query = sql_query
                            st.success("✅ SQL query generated successfully!")

                        progress_bar.empty()
                else:
                    st.error("❌ Please enter a natural language query!")

        # SQL Editor
        if st.session_state.sql_query:
            st.markdown("### ✏️ SQL Query Editor")
            st.info("💡 You can edit the generated SQL query below before execution")

            # SQL editor with syntax highlighting
            edited_sql = st.text_area(
                "📝 SQL Query:",
                value=st.session_state.sql_query,
                height=300,
                key="sql_editor",
                help="Edit the SQL query if needed. The query will be validated before execution."
            )

            # Update session state
            if edited_sql != st.session_state.sql_query:
                st.session_state.sql_query = edited_sql
                # Save to session
                session_manager = get_session_manager()
                session_manager.save_session_data('sql_query', edited_sql)

            # SQL Preview with syntax highlighting
            st.markdown("### 👀 SQL Preview")
            st.code(st.session_state.sql_query, language='sql')

            # Query analysis
            with st.expander("🔍 Query Analysis", expanded=False):
                query_lower = st.session_state.sql_query.lower()

                analysis_points = []
                if 'join' in query_lower:
                    join_count = query_lower.count('join')
                    analysis_points.append(f"✅ Uses {join_count} join(s)")

                if 'group by' in query_lower:
                    analysis_points.append("✅ Includes aggregation (GROUP BY)")

                if 'order by' in query_lower:
                    analysis_points.append("✅ Results will be sorted")

                if 'where' in query_lower:
                    analysis_points.append("✅ Includes filtering conditions")

                if 'limit' in query_lower:
                    analysis_points.append("✅ Results are limited")

                for point in analysis_points:
                    st.markdown(point)

            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("⬅️ Back to Joins", key="back_to_joins_from_sql"):
                    st.session_state.current_stage = 2
                    st.rerun()

            with col2:
                if st.button("🔄 Regenerate", key="regenerate_sql"):
                    st.session_state.sql_query = ""
                    st.rerun()

            with col3:
                if st.button("▶️ Execute Query", key="continue_to_results", type="primary"):
                    st.session_state.current_stage = 4
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    return bool(st.session_state.sql_query)

# Professional Results Display with Advanced Visualizations
def display_professional_results():
    st.markdown("""
    <div class="professional-header fade-in-up">
        <h1>📊 Analytics Dashboard</h1>
        <p>Execute queries and explore your data with interactive visualizations</p>
    </div>
    """, unsafe_allow_html=True)

    display_progress_bar(4)

    if not st.session_state.sql_query:
        st.warning("⚠️ Please generate or enter a SQL query first!")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("⬅️ Back to SQL Generation", key="back_to_sql_from_results"):
                st.session_state.current_stage = 3
                st.rerun()
        return

    with st.container():
        st.markdown('<div class="stage-card">', unsafe_allow_html=True)

        # Query execution section
        st.markdown("### ⚡ Query Execution")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("▶️ Execute SQL Query", key="execute_query_btn", type="primary", use_container_width=True):
                with st.spinner("🔄 Executing query and preparing visualizations..."):
                    # Execute query
                    result = execute_sql_query(st.session_state.sql_query, st.session_state.uploaded_files)

                    if result is not None and not result.empty:
                        st.session_state.query_result = result

                        # Save to session
                        session_manager = get_session_manager()
                        session_manager.save_session_data('query_result', result)

                        st.success(f"✅ Query executed successfully! Retrieved {len(result):,} rows")
                    else:
                        st.error("❌ Query execution failed or returned no results")

        # Display current query
        with st.expander("📝 Current Query", expanded=False):
            st.code(st.session_state.sql_query, language='sql')

        # Results display
        if st.session_state.query_result is not None:
            result_data = st.session_state.query_result

            # Results summary
            st.markdown("### 📈 Results Overview")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(result_data):,}</div>
                    <div class="metric-label">Total Rows</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(result_data.columns)}</div>
                    <div class="metric-label">Columns</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                memory_usage = result_data.memory_usage(deep=True).sum() / (1024*1024)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{memory_usage:.1f} MB</div>
                    <div class="metric-label">Memory Usage</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                completeness = ((result_data.count().sum()) / (len(result_data) * len(result_data.columns))) * 100
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{completeness:.1f}%</div>
                    <div class="metric-label">Data Completeness</div>
                </div>
                """, unsafe_allow_html=True)

            # Enhanced Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Data Table", 
                "📊 Dynamic Visualizations", 
                "📈 Statistical Summary", 
                "🔍 Data Quality",
                "📥 Export Options"
            ])

            with tab1:
                st.markdown("### 📋 Query Results Table")

                # Table controls
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    search_term = st.text_input("🔍 Search in results:", key="search_results")
                with col2:
                    rows_to_show = st.selectbox("Rows to display:", [10, 25, 50, 100, "All"], index=1)
                with col3:
                    sort_column = st.selectbox("Sort by:", options=[""] + list(result_data.columns))

                # Filter data based on search
                display_data = result_data.copy()
                if search_term:
                    mask = display_data.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                    display_data = display_data[mask]

                # Sort data
                if sort_column:
                    display_data = display_data.sort_values(by=sort_column)

                # Limit rows
                if rows_to_show != "All":
                    display_data = display_data.head(int(rows_to_show))

                # Display table with enhanced formatting
                st.dataframe(
                    display_data,
                    use_container_width=True,
                    height=400
                )

                # Pagination info
                if len(display_data) < len(result_data):
                    st.info(f"Showing {len(display_data):,} of {len(result_data):,} rows")

            with tab2:
                st.markdown("### 📊 Dynamic Interactive Visualizations")

                # Visualization controls
                col1, col2 = st.columns([1, 1])
                with col1:
                    auto_generate = st.checkbox("🔄 Auto-generate visualizations", value=True)
                with col2:
                    show_advanced = st.checkbox("⚙️ Show advanced options", value=False)

                if show_advanced:
                    with st.expander("🎨 Visualization Settings", expanded=False):
                        viz_settings = st.session_state.get('visualization_settings', {})

                        col1, col2 = st.columns(2)
                        with col1:
                            color_scheme = st.selectbox(
                                "Color Scheme:",
                                options=['plotly', 'viridis', 'plasma', 'inferno', 'rainbow'],
                                index=0
                            )
                        with col2:
                            chart_height = st.slider("Chart Height:", 300, 800, 500)

                        animations = st.checkbox("Enable animations", value=True)
                        interactive = st.checkbox("Enable interactivity", value=True)

                        # Update settings
                        viz_settings.update({
                            'color_scheme': color_scheme,
                            'chart_height': chart_height,
                            'animations': animations,
                            'interactive': interactive
                        })
                        st.session_state.visualization_settings = viz_settings

                if auto_generate:
                    # Generate dynamic visualizations
                    charts = create_dynamic_visualizations(result_data, "Query Results")

                    if charts:
                        # Display charts in a grid
                        chart_cols = st.columns(2)

                        for i, (chart_name, chart_fig) in enumerate(charts):
                            with chart_cols[i % 2]:
                                st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
                                st.markdown(f"#### {chart_name}")
                                st.plotly_chart(chart_fig, use_container_width=True, key=f"chart_{i}")
                                st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("📊 No suitable visualizations available for this data structure.")

                        # Manual chart builder
                        st.markdown("#### 🛠️ Manual Chart Builder")
                        chart_type = st.selectbox("Chart Type:", ['bar', 'line', 'scatter', 'pie'])

                        numeric_cols = result_data.select_dtypes(include=[np.number]).columns.tolist()
                        categorical_cols = result_data.select_dtypes(include=['object', 'category']).columns.tolist()

                        if chart_type in ['bar', 'line', 'scatter'] and numeric_cols and categorical_cols:
                            x_col = st.selectbox("X-axis:", categorical_cols + numeric_cols)
                            y_col = st.selectbox("Y-axis:", numeric_cols)

                            if st.button("Generate Chart"):
                                if chart_type == 'bar':
                                    fig = px.bar(result_data, x=x_col, y=y_col)
                                elif chart_type == 'line':
                                    fig = px.line(result_data, x=x_col, y=y_col)
                                elif chart_type == 'scatter':
                                    fig = px.scatter(result_data, x=x_col, y=y_col)

                                st.plotly_chart(fig, use_container_width=True)

            with tab3:
                st.markdown("### 📈 Statistical Analysis")

                # Numeric statistics
                numeric_data = result_data.select_dtypes(include=[np.number])
                if not numeric_data.empty:
                    st.markdown("#### 🔢 Numeric Columns Summary")

                    stats_df = numeric_data.describe()
                    st.dataframe(stats_df.round(2), use_container_width=True)

                    # Distribution plots
                    if len(numeric_data.columns) > 0:
                        selected_col = st.selectbox("Analyze distribution for:", numeric_data.columns)

                        col1, col2 = st.columns(2)
                        with col1:
                            # Histogram
                            fig_hist = px.histogram(
                                result_data, 
                                x=selected_col, 
                                title=f"Distribution of {selected_col}",
                                marginal="box"
                            )
                            st.plotly_chart(fig_hist, use_container_width=True)

                        with col2:
                            # Box plot
                            fig_box = px.box(
                                result_data, 
                                y=selected_col, 
                                title=f"Box Plot of {selected_col}"
                            )
                            st.plotly_chart(fig_box, use_container_width=True)

                # Categorical statistics
                categorical_data = result_data.select_dtypes(include=['object', 'category'])
                if not categorical_data.empty:
                    st.markdown("#### 📊 Categorical Columns Summary")

                    for col in categorical_data.columns[:5]:  # Limit to first 5
                        st.markdown(f"**{col}:**")
                        value_counts = categorical_data[col].value_counts().head(10)

                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.dataframe(value_counts, use_container_width=True)
                        with col2:
                            # Pie chart for categorical
                            if len(value_counts) <= 10:
                                fig_pie = px.pie(
                                    values=value_counts.values,
                                    names=value_counts.index,
                                    title=f"{col} Distribution"
                                )
                                st.plotly_chart(fig_pie, use_container_width=True)

            with tab4:
                st.markdown("### 🔍 Data Quality Assessment")

                # Missing values analysis
                missing_data = result_data.isnull().sum()
                missing_pct = (missing_data / len(result_data)) * 100

                if missing_data.sum() > 0:
                    st.markdown("#### ⚠️ Missing Values")
                    missing_df = pd.DataFrame({
                        'Column': missing_data.index,
                        'Missing Count': missing_data.values,
                        'Missing %': missing_pct.values
                    })
                    missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)

                    st.dataframe(missing_df, use_container_width=True)

                    # Visualization of missing data
                    if len(missing_df) > 0:
                        fig_missing = px.bar(
                            missing_df, 
                            x='Column', 
                            y='Missing %',
                            title="Missing Data by Column"
                        )
                        st.plotly_chart(fig_missing, use_container_width=True)
                else:
                    st.success("✅ No missing values detected in the results!")

                # Duplicate analysis
                duplicates = result_data.duplicated().sum()
                if duplicates > 0:
                    st.warning(f"⚠️ Found {duplicates} duplicate rows in the results")
                else:
                    st.success("✅ No duplicate rows found!")

                # Data types info
                st.markdown("#### 📋 Data Types Information")
                dtypes_df = pd.DataFrame({
                    'Column': result_data.columns,
                    'Data Type': result_data.dtypes,
                    'Unique Values': result_data.nunique(),
                    'Sample Value': [str(result_data[col].iloc[0]) if len(result_data) > 0 else 'N/A' for col in result_data.columns]
                })
                st.dataframe(dtypes_df, use_container_width=True)

            with tab5:
                st.markdown("### 📥 Export and Download Options")

                # Export formats
                col1, col2, col3 = st.columns(3)

                with col1:
                    # CSV Export
                    csv_data = result_data.to_csv(index=False)
                    st.download_button(
                        label="📄 Download as CSV",
                        data=csv_data,
                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_csv",
                        use_container_width=True
                    )

                with col2:
                    # Excel Export
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        result_data.to_excel(writer, sheet_name='Query_Results', index=False)

                        # Add summary sheet if numeric data exists
                        numeric_data = result_data.select_dtypes(include=[np.number])
                        if not numeric_data.empty:
                            numeric_data.describe().to_excel(writer, sheet_name='Summary_Statistics')

                    st.download_button(
                        label="📊 Download as Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel",
                        use_container_width=True
                    )

                with col3:
                    # JSON Export
                    json_data = result_data.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📋 Download as JSON",
                        data=json_data,
                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_json",
                        use_container_width=True
                    )

                # Advanced export options
                with st.expander("⚙️ Advanced Export Options", expanded=False):
                    export_rows = st.number_input(
                        "Limit export to rows:", 
                        min_value=1, 
                        max_value=len(result_data), 
                        value=min(1000, len(result_data))
                    )

                    selected_columns = st.multiselect(
                        "Select columns to export:",
                        options=result_data.columns.tolist(),
                        default=result_data.columns.tolist()
                    )

                    if st.button("📦 Generate Custom Export"):
                        export_data = result_data[selected_columns].head(export_rows)
                        custom_csv = export_data.to_csv(index=False)

                        st.download_button(
                            label="📥 Download Custom CSV",
                            data=custom_csv,
                            file_name=f"custom_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⬅️ Back to SQL", key="back_to_sql_final"):
                st.session_state.current_stage = 3
                st.rerun()

        with col2:
            if st.button("🔄 New Analysis", key="restart_analysis"):
                # Clear all data for new analysis
                keys_to_clear = ['uploaded_files', 'join_conditions', 'sql_query', 'query_result']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_stage = 1
                st.rerun()

        with col3:
            if st.button("💾 Save Session", key="save_session"):
                session_manager = get_session_manager()
                session_data = {
                    'timestamp': datetime.now().isoformat(),
                    'uploaded_files': list(st.session_state.uploaded_files.keys()),
                    'join_conditions': st.session_state.join_conditions,
                    'sql_query': st.session_state.sql_query,
                    'result_count': len(st.session_state.query_result) if st.session_state.query_result is not None else 0
                }
                session_manager.save_session_data('session_summary', session_data)
                st.success("✅ Session saved successfully!")

        st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Sidebar with Professional Design
def display_professional_sidebar():
    with st.sidebar:
        # Sidebar header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;">
            <h2 style="margin: 0; font-size: 1.5rem;">🚀 Control Panel</h2>
        </div>
        """, unsafe_allow_html=True)

        # Authentication Section
        st.markdown("### 🔐 AWS Authentication")

        if not st.session_state.authenticated:
            with st.expander("🔑 Connect to AWS Bedrock", expanded=True):
                st.markdown("Configure your AWS credentials to enable AI-powered SQL generation.")

                username = st.text_input("👤 Username", key="aws_username")
                password = st.text_input("🔒 Password", type="password", key="aws_password")
                account_id = st.text_input("🏢 Account ID", key="aws_account_id")
                region = st.selectbox(
                    "🌍 Region", 
                    options=["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                    key="aws_region"
                )

                if st.button("🔓 Authenticate", key="auth_btn", use_container_width=True):
                    if authenticate_aws(username, password, account_id, region):
                        st.success("✅ Connected successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Authentication failed!")
        else:
            st.success("✅ Connected to AWS Bedrock")
            if st.button("🚪 Disconnect", key="logout_btn", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.aws_client = None
                st.session_state.bedrock_client = None
                st.rerun()

        st.markdown("---")

        # Navigation Section
        st.markdown("### 🧭 Navigation")

        stage_options = [
            "1️⃣ Upload Files",
            "2️⃣ Configure Joins", 
            "3️⃣ Generate SQL",
            "4️⃣ View Results"
        ]

        # Custom radio buttons with status indicators
        current_stage = st.session_state.current_stage

        for i, option in enumerate(stage_options, 1):
            if i == current_stage:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 0.8rem; border-radius: 8px; margin: 0.3rem 0;">
                    <span class="status-indicator status-info"></span>{option}
                </div>
                """, unsafe_allow_html=True)
            elif i < current_stage:
                if st.button(f"✅ {option}", key=f"nav_{i}", use_container_width=True):
                    st.session_state.current_stage = i
                    st.rerun()
            else:
                st.markdown(f"""
                <div style="background: #f8f9fa; color: #666; padding: 0.8rem; border-radius: 8px; margin: 0.3rem 0;">
                    <span class="status-indicator" style="background-color: #ccc;"></span>{option}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Session Information
        st.markdown("### 📊 Session Info")

        if st.session_state.uploaded_files:
            st.metric("📁 Files", len(st.session_state.uploaded_files))

        if st.session_state.join_conditions:
            st.metric("🔗 Joins", len(st.session_state.join_conditions))

        if st.session_state.query_result is not None:
            st.metric("📋 Result Rows", len(st.session_state.query_result))

        if st.session_state.get('query_history'):
            st.metric("📚 Query History", len(st.session_state.query_history))

        st.markdown("---")

        # Help Section
        st.markdown("### ❓ Quick Help")

        with st.expander("📖 User Guide"):
            st.markdown("""
            **🚀 Getting Started:**
            1. **Upload Files**: Add your CSV data files
            2. **Configure Joins**: Link related tables
            3. **Generate SQL**: Use natural language queries
            4. **View Results**: Analyze with interactive charts

            **💡 Tips:**
            - Use descriptive queries for better SQL generation
            - Check data quality before analysis
            - Export results in multiple formats
            - Save your session for later use
            """)

        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common Issues:**
            - **Authentication Failed**: Check AWS credentials
            - **No Visualizations**: Ensure data has numeric/categorical columns
            - **Query Errors**: Verify table relationships and column names
            - **Slow Performance**: Limit result rows or optimize joins
            """)

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p>🚀 Professional NLP to SQL Platform</p>
            <p>Powered by AWS Bedrock & Streamlit</p>
        </div>
        """, unsafe_allow_html=True)

# Main Application Function
def main():
    # Initialize session state
    initialize_session_state()

    # Update last activity
    st.session_state.last_activity = datetime.now().isoformat()

    # Display sidebar
    display_professional_sidebar()

    # Main content area
    if st.session_state.current_stage == 1:
        display_professional_file_upload()
    elif st.session_state.current_stage == 2:
        if st.session_state.uploaded_files:
            display_advanced_join_builder()
        else:
            st.warning("⚠️ Please upload files first!")
            if st.button("📁 Go to Upload", key="goto_upload_from_empty"):
                st.session_state.current_stage = 1
                st.rerun()
    elif st.session_state.current_stage == 3:
        if st.session_state.uploaded_files:
            display_professional_sql_generation()
        else:
            st.warning("⚠️ Please upload files first!")
            if st.button("📁 Go to Upload", key="goto_upload_from_sql"):
                st.session_state.current_stage = 1
                st.rerun()
    elif st.session_state.current_stage == 4:
        if st.session_state.uploaded_files:
            display_professional_results()
        else:
            st.warning("⚠️ Please upload files first!")
            if st.button("📁 Go to Upload", key="goto_upload_from_results"):
                st.session_state.current_stage = 1
                st.rerun()

    # Professional Footer
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 2rem; border-radius: 15px; text-align: center; margin-top: 2rem;">
        <h3 style="margin: 0;">🚀 Professional NLP to SQL Analytics Platform</h3>
        <p style="margin: 0.5rem 0; opacity: 0.9;">
            Transform natural language into powerful SQL queries with AI-driven insights
        </p>
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">
            Powered by AWS Bedrock, Streamlit & Advanced Analytics | 
            Session ID: {st.session_state.get('session_id', 'N/A')[:8]}...
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
