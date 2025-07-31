import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import sqlite3
import sqlalchemy
import io
from datetime import datetime
import re
from enhanced_aws_login import AWSPortalClient
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Enhanced NLP-to-SQL Analytics Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for modern UI
st.markdown("""
<style>
    /* Main theme and layout */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Cards and containers */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    
    .success-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    
    .error-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* DataFrames */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Join section */
    .join-section {
        background: linear-gradient(135deg, #e3ffe7 0%, #d9e7ff 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #b3d9ff;
        margin: 1rem 0;
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    session_vars = {
        'authenticated': False,
        'aws_client': None,
        'bedrock_client': None,
        'uploaded_files': {},
        'current_data': None,
        'sql_query': "",
        'query_result': None,
        'join_performed': False
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

# AWS Authentication Function
def authenticate_aws(username, password, account_id, region):
    """Authenticate with AWS and create Bedrock client"""
    try:
        with st.spinner("🔐 Authenticating with AWS Portal..."):
            aws_client = AWSPortalClient(username=username, password=password)
            token = aws_client.gather_token()
            credentials = aws_client.gather_credentials(token, account_id)
            bedrock_client = aws_client.create_client(credentials, "bedrock-runtime", region)
            
            st.session_state.authenticated = True
            st.session_state.aws_client = aws_client
            st.session_state.bedrock_client = bedrock_client
            
            return True, "✅ Successfully authenticated with AWS!"
    except Exception as e:
        return False, f"❌ Authentication failed: {str(e)}"

# File Processing Functions
def load_file(file_obj):
    """Load file based on its extension"""
    try:
        if file_obj.name.lower().endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_obj)
        elif file_obj.name.lower().endswith('.csv'):
            return pd.read_csv(file_obj)
        else:
            st.error(f"Unsupported file format: {file_obj.name}")
            return None
    except Exception as e:
        st.error(f"Error loading {file_obj.name}: {str(e)}")
        return None

def process_uploaded_files(uploaded_files):
    """Process multiple uploaded files"""
    processed_files = {}
    
    for file_obj in uploaded_files:
        df = load_file(file_obj)
        if df is not None:
            processed_files[file_obj.name] = df
            st.success(f"✅ Successfully loaded **{file_obj.name}** ({df.shape[0]} rows × {df.shape[1]} columns)")
    
    return processed_files

# Join Functions
def perform_join(left_df, right_df, left_key, right_key, join_type, left_name, right_name):
    """Perform join operation between two DataFrames"""
    try:
        # Handle different column names
        if left_key != right_key:
            joined_df = pd.merge(
                left_df, right_df,
                left_on=left_key, right_on=right_key,
                how=join_type,
                suffixes=(f'_{left_name}', f'_{right_name}')
            )
        else:
            joined_df = pd.merge(
                left_df, right_df,
                on=left_key,
                how=join_type,
                suffixes=(f'_{left_name}', f'_{right_name}')
            )
        
        return joined_df, None
    except Exception as e:
        return None, str(e)

# SQL Generation and Execution
def generate_sql_from_nl(question, table_schema, bedrock_client):
    """Generate SQL from natural language using Bedrock"""
    try:
        # Create system prompt with schema information
        system_prompt = f"""
        You are an expert SQL assistant. Generate SQL queries based on natural language questions.
        
        Table Schema: {table_schema}
        Table Name: data_table
        
        Rules:
        1. Always use SQLite syntax
        2. Use "data_table" as the table name
        3. Return only the SQL query, no explanations
        4. Ensure the query is syntactically correct
        5. Use appropriate aggregate functions when needed
        """
        
        messages = [
            {
                "role": "user", 
                "content": [{"text": f"{system_prompt}\n\nQuestion: {question}"}]
            }
        ]
        
        response = bedrock_client.converse(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            messages=messages
        )
        
        sql_query = response['output']['message']['content'][0]['text'].strip()
        
        # Clean up the response to extract just the SQL
        if '```
            sql_query = sql_query.split('```sql')[1].split('```
        elif '```' in sql_query:
            sql_query = sql_query.split('```
            
        return sql_query
        
    except Exception as e:
        st.error(f"Error generating SQL: {str(e)}")
        return None

def execute_sql_query(sql_query, df):
    """Execute SQL query on DataFrame"""
    try:
        # Create SQLite engine
        engine = sqlalchemy.create_engine('sqlite:///:memory:')
        
        # Write DataFrame to SQL
        df.to_sql('data_table', engine, if_exists='replace', index=False)
        
        # Execute query
        result = pd.read_sql_query(sql_query, engine)
        
        return result, None
        
    except Exception as e:
        return None, str(e)

# Visualization Functions
def create_visualization(df, chart_type="auto"):
    """Create visualizations based on data"""
    try:
        if df.empty:
            st.warning("No data to visualize")
            return
            
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Scatter plot for numeric data
            fig = px.scatter(
                df, 
                x=numeric_cols, 
                y=numeric_cols,
                title=f"{numeric_cols} vs {numeric_cols}",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            # Bar chart for mixed data
            fig = px.bar(
                df.head(20), 
                x=categorical_cols, 
                y=numeric_cols,
                title=f"{numeric_cols} by {categorical_cols}",
                template="plotly_white"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
        elif len(numeric_cols) >= 1:
            # Histogram for single numeric column
            fig = px.histogram(
                df, 
                x=numeric_cols,
                title=f"Distribution of {numeric_cols}",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")

# Main Application
def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Enhanced NLP-to-SQL Analytics Platform</h1>
        <p>Upload multiple files, join them intelligently, and query with natural language</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - AWS Authentication
    with st.sidebar:
        st.markdown("### 🔐 AWS Authentication")
        
        if not st.session_state.authenticated:
            with st.form("auth_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                account_id = st.text_input("AWS Account ID")
                region = st.selectbox("AWS Region", 
                    ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"])
                
                submitted = st.form_submit_button("🚀 Authenticate")
                
                if submitted:
                    if username and password and account_id:
                        success, message = authenticate_aws(username, password, account_id, region)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all fields")
        else:
            st.success("✅ AWS Authenticated")
            if st.button("🚪 Logout"):
                for key in ['authenticated', 'aws_client', 'bedrock_client']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📁 File Upload", "🔗 Data Joining", "🤖 NL Query", "📊 Visualization"])
    
    # Tab 1: File Upload
    with tab1:
        st.markdown("### 📁 Upload Your Data Files")
        
        uploaded_files = st.file_uploader(
            "Choose Excel or CSV files",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="You can upload multiple files. Supported formats: CSV, Excel (.xlsx, .xls)"
        )
        
        if uploaded_files:
            with st.spinner("📊 Processing uploaded files..."):
                processed_files = process_uploaded_files(uploaded_files)
                st.session_state.uploaded_files = processed_files
            
            # Display file information
            st.markdown("### 📋 Uploaded Files Summary")
            
            cols = st.columns(len(processed_files))
            for idx, (filename, df) in enumerate(processed_files.items()):
                with cols[idx % len(cols)]:
                    st.markdown(f"""
                    <div class="custom-card">
                        <h4>📄 {filename}</h4>
                        <div class="metric-value">{df.shape:,}</div>
                        <div class="metric-label">Rows</div>
                        <div class="metric-value">{df.shape:,}</div>
                        <div class="metric-label">Columns</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show preview of each file
            for filename, df in processed_files.items():
                with st.expander(f"🔍 Preview: {filename}"):
                    st.dataframe(df.head(), use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Column Types:**")
                        st.write(df.dtypes)
                    with col2:
                        st.markdown("**Missing Values:**")
                        st.write(df.isnull().sum())
    
    # Tab 2: Data Joining
    with tab2:
        if not st.session_state.uploaded_files:
            st.info("📁 Please upload files first in the File Upload tab")
        elif len(st.session_state.uploaded_files) == 1:
            st.info("📊 Only one file uploaded. Joining requires multiple files.")
            # Set current data to the single file
            filename, df = list(st.session_state.uploaded_files.items())
            st.session_state.current_data = df
            st.markdown(f"**Current dataset: {filename}**")
            st.dataframe(df.head(), use_container_width=True)
        else:
            st.markdown("""
            <div class="join-section">
                <h3>🔗 Join Multiple Datasets</h3>
                <p>Configure how to join your uploaded files based on common columns</p>
            </div>
            """, unsafe_allow_html=True)
            
            file_names = list(st.session_state.uploaded_files.keys())
            
            # Join configuration
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Select Tables to Join")
                left_table = st.selectbox("Left Table", file_names, key="left_table")
                right_table = st.selectbox(
                    "Right Table", 
                    [f for f in file_names if f != left_table], 
                    key="right_table"
                )
            
            with col2:
                st.markdown("#### ⚙️ Join Configuration")
                join_type = st.selectbox(
                    "Join Type",
                    ["inner", "left", "right", "outer"],
                    help="Select how to combine the tables"
                )
            
            if left_table and right_table:
                left_df = st.session_state.uploaded_files[left_table]
                right_df = st.session_state.uploaded_files[right_table]
                
                # Column selection for join
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Join Key from {left_table}:**")
                    left_key = st.selectbox(
                        f"Column from {left_table}",
                        left_df.columns.tolist(),
                        key="left_key"
                    )
                    
                with col2:
                    st.markdown(f"**Join Key from {right_table}:**")
                    right_key = st.selectbox(
                        f"Column from {right_table}",
                        right_df.columns.tolist(),
                        key="right_key"
                    )
                
                # Preview join keys
                if left_key and right_key:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Sample values from {left_table}.{left_key}:**")
                        st.write(left_df[left_key].head().tolist())
                        
                    with col2:
                        st.markdown(f"**Sample values from {right_table}.{right_key}:**")
                        st.write(right_df[right_key].head().tolist())
                
                # Perform join
                if st.button("🔗 Perform Join", type="primary"):
                    with st.spinner("🔄 Joining datasets..."):
                        joined_df, error = perform_join(
                            left_df, right_df, left_key, right_key, 
                            join_type, left_table, right_table
                        )
                        
                        if error:
                            st.error(f"❌ Join failed: {error}")
                        else:
                            st.session_state.current_data = joined_df
                            st.session_state.join_performed = True
                            
                            st.markdown("""
                            <div class="success-card">
                                <h4>✅ Join Successful!</h4>
                                <p>Your datasets have been successfully joined.</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show join results
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Original Rows", f"{len(left_df):,}")
                            with col2:
                                st.metric("Joined Rows", f"{len(joined_df):,}")
                            with col3:
                                st.metric("Total Columns", f"{len(joined_df.columns):,}")
                            
                            st.markdown("### 📊 Joined Dataset Preview")
                            st.dataframe(joined_df.head(10), use_container_width=True)
                            
                            # Download option
                            csv = joined_df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Joined Data",
                                csv,
                                "joined_data.csv",
                                "text/csv"
                            )
    
    # Tab 3: NL Query
    with tab3:
        if not st.session_state.authenticated:
            st.warning("🔐 Please authenticate with AWS first")
        elif st.session_state.current_data is None and not st.session_state.uploaded_files:
            st.info("📁 Please upload and prepare your data first")
        else:
            # Determine current dataset
            if st.session_state.current_data is not None:
                current_df = st.session_state.current_data
                data_source = "Joined Data" if st.session_state.join_performed else "Single File"
            else:
                # Use the first (and only) uploaded file
                filename, current_df = list(st.session_state.uploaded_files.items())
                data_source = filename
                st.session_state.current_data = current_df
            
            st.markdown(f"""
            ### 🤖 Natural Language Query Interface
            **Current Dataset:** {data_source} ({current_df.shape:,} rows × {current_df.shape:,} columns)
            """)
            
            # Show current data schema
            with st.expander("📋 View Data Schema"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Columns:**")
                    for col in current_df.columns:
                        st.write(f"-  {col} ({current_df[col].dtype})")
                with col2:
                    st.markdown("**Sample Data:**")
                    st.dataframe(current_df.head(3))
            
            # Query interface
            st.markdown("### 💬 Ask a Question About Your Data")
            
            # Example questions
            with st.expander("💡 Example Questions"):
                st.markdown("""
                - What is the average value by category?
                - Show me the top 10 records by sales
                - How many unique customers are there?
                - What is the trend over time?
                - Which product has the highest revenue?
                """)
            
            # Query input
            user_question = st.text_area(
                "Enter your question in plain English:",
                height=100,
                placeholder="e.g., What are the top 5 products by sales?"
            )
            
            col1, col2 = st.columns()
            with col1:
                query_button = st.button("🚀 Generate SQL", type="primary")
            
            if query_button and user_question:
                with st.spinner("🧠 Generating SQL query..."):
                    # Prepare schema information
                    schema_info = {
                        'columns': list(current_df.columns),
                        'dtypes': dict(current_df.dtypes.astype(str)),
                        'sample_data': current_df.head(3).to_dict('records')
                    }
                    
                    sql_query = generate_sql_from_nl(
                        user_question, 
                        schema_info, 
                        st.session_state.bedrock_client
                    )
                    
                    if sql_query:
                        st.session_state.sql_query = sql_query
                        
                        # Display generated SQL
                        st.markdown("### 📝 Generated SQL Query")
                        st.code(sql_query, language="sql")
                        
                        # Execute query
                        with st.spinner("⚡ Executing query..."):
                            result_df, error = execute_sql_query(sql_query, current_df)
                            
                            if error:
                                st.error(f"❌ Query execution failed: {error}")
                            else:
                                st.session_state.query_result = result_df
                                
                                st.markdown("### 📊 Query Results")
                                
                                if len(result_df) == 0:
                                    st.info("Query returned no results")
                                else:
                                    # Show metrics
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Rows Returned", f"{len(result_df):,}")
                                    with col2:
                                        st.metric("Columns", f"{len(result_df.columns):,}")
                                    with col3:
                                        if len(result_df) < len(current_df):
                                            percentage = (len(result_df) / len(current_df)) * 100
                                            st.metric("% of Total Data", f"{percentage:.1f}%")
                                    
                                    # Display results
                                    st.dataframe(result_df, use_container_width=True)
                                    
                                    # Download results
                                    csv = result_df.to_csv(index=False)
                                    st.download_button(
                                        "📥 Download Results",
                                        csv,
                                        f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        "text/csv"
                                    )
    
    # Tab 4: Visualization
    with tab4:
        if st.session_state.query_result is not None:
            st.markdown("### 📊 Query Results Visualization")
            create_visualization(st.session_state.query_result)
            
            # Additional chart options
            st.markdown("### 🎨 Custom Visualization")
            
            numeric_cols = st.session_state.query_result.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = st.session_state.query_result.select_dtypes(include=['object']).columns.tolist()
            
            if numeric_cols or categorical_cols:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    chart_type = st.selectbox(
                        "Chart Type",
                        ["bar", "line", "scatter", "histogram", "box"]
                    )
                
                with col2:
                    x_col = st.selectbox(
                        "X-axis",
                        categorical_cols + numeric_cols if categorical_cols else numeric_cols
                    )
                
                with col3:
                    y_col = st.selectbox(
                        "Y-axis",
                        numeric_cols if numeric_cols else categorical_cols
                    )
                
                if st.button("🎨 Create Visualization"):
                    try:
                        df_viz = st.session_state.query_result
                        
                        if chart_type == "bar" and x_col and y_col:
                            fig = px.bar(df_viz, x=x_col, y=y_col, template="plotly_white")
                        elif chart_type == "line" and x_col and y_col:
                            fig = px.line(df_viz, x=x_col, y=y_col, template="plotly_white")
                        elif chart_type == "scatter" and x_col and y_col:
                            fig = px.scatter(df_viz, x=x_col, y=y_col, template="plotly_white")
                        elif chart_type == "histogram" and x_col:
                            fig = px.histogram(df_viz, x=x_col, template="plotly_white")
                        elif chart_type == "box" and x_col and y_col:
                            fig = px.box(df_viz, x=x_col, y=y_col, template="plotly_white")
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error creating visualization: {str(e)}")
            
        elif st.session_state.current_data is not None:
            st.markdown("### 📊 Data Overview Visualization")
            create_visualization(st.session_state.current_data)
            
        else:
            st.info("📊 Upload data and run queries to see visualizations")
    
    # Footer
    st.markdown("""
    ---
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Enhanced NLP-to-SQL Analytics Platform | Built with Streamlit & AWS Bedrock</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
