# Let's create an enhanced version of the nlp_sql_app.py with the requested features
# First, let's create a comprehensive enhanced application

enhanced_code = '''
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

# Page configuration
st.set_page_config(
    page_title="NLP to SQL Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .file-upload-area {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    .join-builder {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    .sql-editor {
        font-family: 'Courier New', monospace;
        background-color: #f8f8f8;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 10px;
    }
    .stage-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .data-preview {
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        background-color: #fafafa;
    }
    .join-condition {
        background-color: #e9ecef;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'aws_client' not in st.session_state:
        st.session_state.aws_client = None
    if 'bedrock_client' not in st.session_state:
        st.session_state.bedrock_client = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    if 'join_conditions' not in st.session_state:
        st.session_state.join_conditions = []
    if 'sql_query' not in st.session_state:
        st.session_state.sql_query = ""
    if 'query_result' not in st.session_state:
        st.session_state.query_result = None
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 1

# Function to authenticate AWS
def authenticate_aws(username, password, account_id, region):
    try:
        with st.spinner("Authenticating with AWS..."):
            aws_client = AWSPortalClient(username=username, password=password)
            token = aws_client.gather_token()
            credentials = aws_client.gather_credentials(token, account_id)
            if credentials:
                bedrock_client = aws_client.create_client(credentials, 'bedrock-runtime', region)
                if bedrock_client:
                    st.session_state.aws_client = aws_client
                    st.session_state.bedrock_client = bedrock_client
                    st.session_state.authenticated = True
                    return True
            return False
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return False

# Enhanced function to generate SQL using AWS Bedrock with join support
def generate_sql_with_bedrock(natural_language_query, table_schemas, join_conditions, bedrock_client):
    try:
        # Create a comprehensive prompt for SQL generation with multiple tables
        tables_info = ""
        for table_name, schema in table_schemas.items():
            tables_info += f"\\nTable: {table_name}\\n"
            tables_info += f"Schema: {schema}\\n"
        
        joins_info = ""
        if join_conditions:
            joins_info = "\\nJoin Conditions:\\n"
            for i, join in enumerate(join_conditions):
                joins_info += f"{i+1}. {join['left_table']}.{join['left_column']} {join['join_type']} {join['right_table']}.{join['right_column']}\\n"
        
        prompt = f"""
You are an expert SQL developer. Given the following table schemas, join conditions, and natural language query, generate a precise SQL query that answers the question.

{tables_info}
{joins_info}

Natural Language Query: {natural_language_query}

Instructions:
1. Generate only valid SQL syntax
2. Use appropriate WHERE clauses, JOINs, GROUP BY, ORDER BY as needed
3. Follow the specified join conditions
4. Use table aliases for better readability
5. Return only the SQL query without any explanation
6. Ensure the query is optimized and follows best practices

SQL Query:
"""
        
        # Prepare the message for Bedrock
        message = [{"role": "user", "content": [{"text": prompt}]}]
        model_id = 'anthropic.claude-3-sonnet-20240620-v1:0'
        
        # Call Bedrock
        response = bedrock_client.converse(modelId=model_id, messages=message)
        
        # Extract the SQL query
        output_text = response['output']['message']
        sql_query = ''
        for content in output_text['content']:
            sql_query += content['text']
        
        # Clean up the SQL query
        sql_query = sql_query.strip()
        sql_query = re.sub(r'```sql', '', sql_query)
        sql_query = re.sub(r'```', '', sql_query)
        sql_query = sql_query.strip()
        
        return sql_query
    except Exception as e:
        st.error(f"Error generating SQL: {str(e)}")
        return None

# Enhanced function to execute SQL query on multiple joined tables
def execute_sql_query(sql_query, dataframes_dict):
    try:
        # Create an in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        
        # Load all dataframes into SQLite
        for table_name, df in dataframes_dict.items():
            df.to_sql(table_name, conn, index=False, if_exists='replace')
        
        # Execute the SQL query
        result = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        return result
    except Exception as e:
        st.error(f"Error executing SQL query: {str(e)}")
        return None

# Enhanced function to create visualizations
def create_visualizations(data, query_description):
    """Create various charts based on the data"""
    if data is None or data.empty:
        return None
    
    charts = []
    
    # Determine chart types based on data
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Chart 1: Bar chart if we have categorical and numeric data
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        fig_bar = px.bar(
            data,
            x=categorical_cols[0],
            y=numeric_cols[0],
            title=f"Bar Chart: {categorical_cols[0]} vs {numeric_cols[0]}",
            color=categorical_cols[0] if len(data) < 50 else None
        )
        fig_bar.update_layout(showlegend=len(data) < 20)
        charts.append(("Bar Chart", fig_bar))
    
    # Chart 2: Line chart for time series or numeric progression
    if len(numeric_cols) >= 2:
        fig_line = px.line(
            data,
            x=data.columns[0],
            y=numeric_cols[0],
            title=f"Line Chart: {data.columns[0]} vs {numeric_cols[0]}"
        )
        charts.append(("Line Chart", fig_line))
    
    # Chart 3: Pie chart for categorical data with counts
    if len(categorical_cols) >= 1 and len(data) <= 20:
        value_counts = data[categorical_cols[0]].value_counts()
        fig_pie = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f"Distribution of {categorical_cols[0]}"
        )
        charts.append(("Pie Chart", fig_pie))
    
    # Chart 4: Scatter plot for two numeric variables
    if len(numeric_cols) >= 2:
        fig_scatter = px.scatter(
            data,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=f"Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}",
            color=categorical_cols[0] if categorical_cols else None
        )
        charts.append(("Scatter Plot", fig_scatter))
    
    return charts

# Function to display file upload interface
def display_file_upload():
    st.markdown('<div class="stage-header">📁 Stage 1: Upload Multiple Files</div>', unsafe_allow_html=True)
    
    # File upload section
    uploaded_files = st.file_uploader(
        "Choose CSV files",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload multiple CSV files that you want to analyze and join"
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = {}
        
        for uploaded_file in uploaded_files:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                table_name = uploaded_file.name.replace('.csv', '').replace(' ', '_').lower()
                st.session_state.uploaded_files[table_name] = df
                
                # Display file info
                with st.expander(f"📊 Preview: {uploaded_file.name}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", df.shape[0])
                    with col2:
                        st.metric("Columns", df.shape[1])
                    with col3:
                        st.metric("Size", f"{uploaded_file.size} bytes")
                    
                    st.subheader("Data Preview")
                    st.dataframe(df.head(10))
                    
                    st.subheader("Column Information")
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Data Type': df.dtypes,
                        'Non-Null Count': df.count(),
                        'Null Count': df.isnull().sum()
                    })
                    st.dataframe(col_info)
                    
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {str(e)}")
        
        if len(st.session_state.uploaded_files) > 1:
            st.success(f"✅ Successfully uploaded {len(st.session_state.uploaded_files)} files!")
            return True
        elif len(st.session_state.uploaded_files) == 1:
            st.info("ℹ️ Single file uploaded. You can proceed or upload more files for joining.")
            return True
    
    return False

# Function to display join builder interface
def display_join_builder():
    st.markdown('<div class="stage-header">🔗 Stage 2: Configure Joins</div>', unsafe_allow_html=True)
    
    if len(st.session_state.uploaded_files) < 2:
        st.info("ℹ️ Upload at least 2 files to configure joins, or proceed with single table analysis.")
        return True
    
    st.markdown("### Join Configuration")
    
    # Join builder interface
    with st.container():
        st.markdown('<div class="join-builder">', unsafe_allow_html=True)
        
        # Display current joins
        if st.session_state.join_conditions:
            st.subheader("Current Join Conditions:")
            for i, join in enumerate(st.session_state.join_conditions):
                st.markdown(f'''
                <div class="join-condition">
                    <strong>Join {i+1}:</strong> {join["left_table"]}.{join["left_column"]} 
                    <span style="color: #007bff;">{join["join_type"]}</span> 
                    {join["right_table"]}.{join["right_column"]}
                </div>
                ''', unsafe_allow_html=True)
        
        # Add new join
        st.subheader("Add New Join:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Left Table**")
            left_table = st.selectbox(
                "Select left table:",
                options=list(st.session_state.uploaded_files.keys()),
                key="left_table_select"
            )
            
            if left_table:
                left_columns = list(st.session_state.uploaded_files[left_table].columns)
                left_column = st.multiselect(
                    "Select left column(s):",
                    options=left_columns,
                    key="left_column_select"
                )
        
        with col2:
            st.markdown("**Right Table**")
            available_right_tables = [t for t in st.session_state.uploaded_files.keys() if t != left_table]
            right_table = st.selectbox(
                "Select right table:",
                options=available_right_tables,
                key="right_table_select"
            )
            
            if right_table:
                right_columns = list(st.session_state.uploaded_files[right_table].columns)
                right_column = st.multiselect(
                    "Select right column(s):",
                    options=right_columns,
                    key="right_column_select"
                )
        
        # Join type selection
        join_type = st.selectbox(
            "Select join type:",
            options=["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"],
            key="join_type_select"
        )
        
        # Add join button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("➕ Add Join", key="add_join_btn"):
                if left_table and right_table and left_column and right_column:
                    if len(left_column) == len(right_column):
                        for i in range(len(left_column)):
                            join_condition = {
                                "left_table": left_table,
                                "left_column": left_column[i],
                                "right_table": right_table,
                                "right_column": right_column[i],
                                "join_type": join_type
                            }
                            st.session_state.join_conditions.append(join_condition)
                        st.success("✅ Join condition(s) added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Number of left and right columns must match!")
                else:
                    st.error("❌ Please select all required fields!")
        
        # Clear joins button
        if st.session_state.join_conditions:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Clear All Joins", key="clear_joins_btn"):
                    st.session_state.join_conditions = []
                    st.success("✅ All join conditions cleared!")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return True

# Function to display SQL generation and editing
def display_sql_generation():
    st.markdown('<div class="stage-header">⚡ Stage 3: Generate & Edit SQL Query</div>', unsafe_allow_html=True)
    
    # Natural language query input
    st.subheader("Natural Language Query")
    natural_query = st.text_area(
        "Describe what you want to analyze:",
        placeholder="e.g., Show me the total sales by region with product categories...",
        height=100,
        key="natural_query_input"
    )
    
    # Generate SQL button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🤖 Generate SQL", key="generate_sql_btn", type="primary"):
            if natural_query and st.session_state.bedrock_client:
                with st.spinner("Generating SQL query..."):
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
            elif not natural_query:
                st.error("❌ Please enter a natural language query!")
            elif not st.session_state.bedrock_client:
                st.error("❌ Please authenticate with AWS Bedrock first!")
    
    # SQL Editor
    st.subheader("SQL Query Editor")
    st.markdown("Edit the generated SQL query if needed:")
    
    edited_sql = st.text_area(
        "SQL Query:",
        value=st.session_state.sql_query,
        height=200,
        key="sql_editor",
        help="You can edit the generated SQL query here"
    )
    
    # Update session state if SQL is edited
    if edited_sql != st.session_state.sql_query:
        st.session_state.sql_query = edited_sql
    
    # Display SQL preview with syntax highlighting
    if st.session_state.sql_query:
        st.subheader("SQL Query Preview")
        st.code(st.session_state.sql_query, language='sql')
    
    return bool(st.session_state.sql_query)

# Function to display results
def display_results():
    st.markdown('<div class="stage-header">📊 Stage 4: Execute Query & View Results</div>', unsafe_allow_html=True)
    
    if not st.session_state.sql_query:
        st.warning("⚠️ Please generate or enter a SQL query first!")
        return
    
    # Execute query button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("▶️ Execute Query", key="execute_query_btn", type="primary"):
            with st.spinner("Executing SQL query..."):
                result = execute_sql_query(st.session_state.sql_query, st.session_state.uploaded_files)
                
                if result is not None:
                    st.session_state.query_result = result
                    st.success("✅ Query executed successfully!")
    
    # Display results
    if st.session_state.query_result is not None:
        result_data = st.session_state.query_result
        
        # Results tabs
        tab1, tab2, tab3 = st.tabs(["📋 Table View", "📊 Visualizations", "📈 Summary Stats"])
        
        with tab1:
            st.subheader("Query Results")
            st.info(f"📊 Results: {len(result_data)} rows × {len(result_data.columns)} columns")
            
            # Display results table
            st.dataframe(result_data, use_container_width=True)
            
            # Download results
            csv_data = result_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_data,
                file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with tab2:
            st.subheader("Data Visualizations")
            
            # Generate charts
            charts = create_visualizations(result_data, "Query Results")
            
            if charts:
                for chart_name, chart_fig in charts:
                    st.plotly_chart(chart_fig, use_container_width=True)
            else:
                st.info("📊 No suitable visualizations available for this data.")
        
        with tab3:
            st.subheader("Summary Statistics")
            
            # Numeric columns summary
            numeric_data = result_data.select_dtypes(include=[np.number])
            if not numeric_data.empty:
                st.markdown("**Numeric Columns Summary:**")
                st.dataframe(numeric_data.describe())
            
            # Categorical columns summary
            categorical_data = result_data.select_dtypes(include=['object', 'category'])
            if not categorical_data.empty:
                st.markdown("**Categorical Columns Summary:**")
                for col in categorical_data.columns:
                    st.markdown(f"**{col}:**")
                    value_counts = categorical_data[col].value_counts()
                    st.dataframe(value_counts.head(10))

# Main sidebar for navigation and authentication
def display_sidebar():
    with st.sidebar:
        st.markdown("## 🔐 Authentication")
        
        if not st.session_state.authenticated:
            st.markdown("### AWS Bedrock Configuration")
            username = st.text_input("Username", key="aws_username")
            password = st.text_input("Password", type="password", key="aws_password")
            account_id = st.text_input("Account ID", key="aws_account_id")
            region = st.selectbox("Region", 
                                options=["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                                key="aws_region")
            
            if st.button("🔑 Authenticate", key="auth_btn"):
                if authenticate_aws(username, password, account_id, region):
                    st.success("✅ Authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Authentication failed!")
        else:
            st.success("✅ Authenticated with AWS Bedrock")
            if st.button("🚪 Logout", key="logout_btn"):
                st.session_state.authenticated = False
                st.session_state.aws_client = None
                st.session_state.bedrock_client = None
                st.rerun()
        
        st.markdown("---")
        
        # Navigation
        st.markdown("## 🧭 Navigation")
        stage = st.radio(
            "Select Stage:",
            options=[
                "1️⃣ Upload Files",
                "2️⃣ Configure Joins", 
                "3️⃣ Generate SQL",
                "4️⃣ View Results"
            ],
            key="stage_selector"
        )
        
        st.session_state.current_stage = int(stage[0])
        
        st.markdown("---")
        
        # Help section
        st.markdown("## ❓ Help")
        with st.expander("📖 How to use"):
            st.markdown("""
            **Step 1: Upload Files**
            - Upload multiple CSV files
            - Preview data structure
            
            **Step 2: Configure Joins**
            - Set up relationships between tables
            - Choose join types (INNER, LEFT, RIGHT, FULL)
            - Support for multiple column joins
            
            **Step 3: Generate SQL**
            - Describe your analysis in natural language
            - AI generates SQL query
            - Edit query as needed
            
            **Step 4: View Results**
            - Execute query and view results
            - Interactive visualizations
            - Download results
            """)

# Main application function
def main():
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Enhanced NLP to SQL Analytics Platform</h1>', unsafe_allow_html=True)
    
    # Sidebar
    display_sidebar()
    
    # Main content based on current stage
    if st.session_state.current_stage == 1:
        display_file_upload()
    elif st.session_state.current_stage == 2:
        if st.session_state.uploaded_files:
            display_join_builder()
        else:
            st.warning("⚠️ Please upload files first!")
    elif st.session_state.current_stage == 3:
        if st.session_state.uploaded_files:
            display_sql_generation()
        else:
            st.warning("⚠️ Please upload files first!")
    elif st.session_state.current_stage == 4:
        if st.session_state.uploaded_files:
            display_results()
        else:
            st.warning("⚠️ Please upload files first!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Enhanced NLP to SQL Analytics Platform | Powered by AWS Bedrock & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
'''

# Save the enhanced code to a file
with open("enhanced_nlp_sql_app.py", "w") as f:
    f.write(enhanced_code)

print("Enhanced NLP SQL App created successfully!")
print("\nKey enhancements added:")
print("1. ✅ Multiple file upload support")
print("2. ✅ Advanced join builder with multiple join types")
print("3. ✅ Multi-column join support")
print("4. ✅ Stage-based workflow (4 stages)")
print("5. ✅ SQL query editor with syntax highlighting")
print("6. ✅ Enhanced UI with custom CSS")
print("7. ✅ Tabbed results view (Table, Visualizations, Summary)")
print("8. ✅ Interactive navigation sidebar")
print("9. ✅ File preview and data profiling")
print("10. ✅ Download results functionality")