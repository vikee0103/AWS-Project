# AWS Bedrock LLM Chat Application using Streamlit
# This application provides a secure interface to interact with AWS Bedrock LLM models
# through corporate AWS portal authentication

import streamlit as st
import boto3
from botocore.config import Config as botoConfig
from botocore.exceptions import ClientError
import urllib3
import json
import time
from datetime import datetime
import hashlib
import hmac

# Configure page
st.set_page_config(
    page_title="AWS Bedrock LLM Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f4e79 0%, #2a5aa0 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .status-connected {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    
    .status-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    
    .chat-message-user {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .chat-message-assistant {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }
    
    .sidebar .stSelectbox > label {
        font-weight: bold;
        color: #1f4e79;
    }
    
    .sidebar .stTextInput > label {
        font-weight: bold;
        color: #1f4e79;
    }
</style>
""", unsafe_allow_html=True)

# Custom Exceptions
class AWSPortalLoginError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class AWSAccountIdError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

# AWS Portal Client Class
class AWSPortalClient:
    """
    Handles AWS Portal authentication and credential management
    """
    def __init__(self, username: str, password: str):
        self.proxy_host = 'primary-proxy.gslb.intranet.barcapint.com'
        self.proxy_port = '8080'
        self.username = username
        self.password = password
        self.http = urllib3.PoolManager()
        self.proxies = {'https': f'https://{self.username}:{self.password}@{self.proxy_host}:{self.proxy_port}'}

    def gather_token(self):
        """
        Contacts the AWS portal and exchanges credentials for a session token
        """
        tokenUrl = "https://awsportal.barcapint.com/v1/jwttoken"
        tokenBody = json.dumps({"username": self.username, "password": self.password})
        
        try:
            tokenResponse = self.http.request("POST", tokenUrl, body=tokenBody)
            if tokenResponse.status != 200:
                raise AWSPortalLoginError("Incorrect username or password")
            return json.loads(tokenResponse.data.decode("utf-8"))["token"]
        except Exception as e:
            raise AWSPortalLoginError(f"Authentication failed: {str(e)}")

    def list_accounts(self, token):
        """
        Gets all the AWS account IDs the user has access to
        """
        rolesUrl = "https://awsportal.barcapint.com/v1/creds-provider/roles?size=200"
        rolesHeaders = {"authorization": "Bearer " + token}
        
        try:
            rolesResponse = self.http.request("GET", rolesUrl, headers=rolesHeaders)
            rolesList = json.loads(rolesResponse.data.decode('utf-8'))["items"]
            return [item["account_id"] for item in rolesList]
        except Exception as e:
            raise Exception(f"Failed to list accounts: {str(e)}")

    def gather_credentials(self, token, accountId):
        """
        Given a valid token and an AWS account ID, fetch the temporary AWS credentials
        """
        try:
            rolesUrl = "https://awsportal.barcapint.com/v1/creds-provider/roles?size=200"
            rolesHeaders = {"authorization": "Bearer " + token}
            rolesResponse = self.http.request("GET", rolesUrl, headers=rolesHeaders)
            rolesList = json.loads(rolesResponse.data.decode('utf-8'))["items"]

            roleArn = None
            for item in rolesList:
                if item["account_id"] == accountId:
                    roleArn = item["role_arn"]
                    break
            
            if not roleArn:
                raise AWSAccountIdError("Account not found in your accessible accounts")

            credentialsUrl = f'https://awsportal.barcapint.com/v1/creds-provider/provide-credentials/{roleArn}'
            credentialsHeaders = {"authorization": "Bearer " + token}
            credentialsResponse = self.http.request("GET", credentialsUrl, headers=credentialsHeaders)
            
            return json.loads(credentialsResponse.data.decode('utf-8'))["Credentials"]
            
        except AWSAccountIdError:
            raise
        except Exception as e:
            raise Exception(f"Failed to gather credentials: {str(e)}")

    def create_client(self, credentials, service, region):
        """
        Create a boto3 client using the gathered credentials
        """
        try:
            session = boto3.Session(
                region_name=region,
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_access_key_id=credentials["AccessKeyId"],
                aws_session_token=credentials["SessionToken"]
            )
            client = session.client(service, config=botoConfig(proxies=self.proxies))
            return client
        except Exception as e:
            raise Exception(f"Failed to create AWS client: {str(e)}")

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'aws_client' not in st.session_state:
        st.session_state.aws_client = None
    if 'bedrock_client' not in st.session_state:
        st.session_state.bedrock_client = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'credentials' not in st.session_state:
        st.session_state.credentials = None
    if 'token' not in st.session_state:
        st.session_state.token = None

# Authentication functions
def authenticate_user(username, password, account_id, region):
    """Authenticate user with AWS Portal"""
    try:
        with st.spinner("Authenticating with AWS Portal..."):
            aws_client = AWSPortalClient(username, password)
            token = aws_client.gather_token()
            credentials = aws_client.gather_credentials(token, account_id)
            bedrock_client = aws_client.create_client(credentials, 'bedrock-runtime', region)
            
            # Store in session state
            st.session_state.authenticated = True
            st.session_state.aws_client = aws_client
            st.session_state.bedrock_client = bedrock_client
            st.session_state.credentials = credentials
            st.session_state.token = token
            st.session_state.current_account = account_id
            st.session_state.current_region = region
            
            return True, "Successfully connected to AWS!"
    
    except AWSPortalLoginError as e:
        return False, f"Authentication failed: {e.message}"
    except AWSAccountIdError as e:
        return False, f"Account error: {e.message}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def disconnect_user():
    """Disconnect user and clear session"""
    st.session_state.authenticated = False
    st.session_state.aws_client = None
    st.session_state.bedrock_client = None
    st.session_state.credentials = None
    st.session_state.token = None
    st.session_state.chat_history = []
    if 'current_account' in st.session_state:
        del st.session_state.current_account
    if 'current_region' in st.session_state:
        del st.session_state.current_region

# Bedrock functions
def call_bedrock_converse(prompt, model_id, max_tokens=4000):
    """Call AWS Bedrock using the Converse API"""
    try:
        message = [{"role": "user", "content": [{"text": prompt}]}]
        
        response = st.session_state.bedrock_client.converse(
            modelId=model_id,
            messages=message,
            inferenceConfig={
                'maxTokens': max_tokens,
                'temperature': st.session_state.get('temperature', 0.7),
                'topP': st.session_state.get('top_p', 0.9)
            }
        )
        
        output_text = response['output']['message']
        full_text = ''
        for content in output_text['content']:
            full_text += content['text']
            
        return True, full_text
        
    except Exception as e:
        return False, f"Bedrock API call failed: {str(e)}"

def call_bedrock_invoke(prompt, model_id, max_tokens=4000):
    """Call AWS Bedrock using the Invoke Model API"""
    try:
        message = [{"role": "user", "content": prompt}]
        body = json.dumps({
            "messages": message,
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": st.session_state.get('temperature', 0.7),
            "top_p": st.session_state.get('top_p', 0.9)
        })
        
        response = st.session_state.bedrock_client.invoke_model(
            modelId=model_id,
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        
        response_content = json.loads(response['body'].read().decode("utf-8"))
        output_text = [item['text'] for item in response_content.get('content', []) if item.get('type') == 'text']
        full_text = '\n'.join(output_text)
        
        return True, full_text
        
    except Exception as e:
        return False, f"Bedrock API call failed: {str(e)}"

# UI Functions
def render_sidebar():
    """Render the authentication sidebar"""
    with st.sidebar:
        st.markdown("### 🔐 AWS Portal Authentication")
        
        if st.session_state.authenticated:
            st.markdown('<div class="status-connected">✅ Connected to AWS</div>', unsafe_allow_html=True)
            st.markdown(f"**Account:** {st.session_state.current_account}")
            st.markdown(f"**Region:** {st.session_state.current_region}")
            
            if st.button("🔓 Disconnect", type="secondary", use_container_width=True):
                disconnect_user()
                st.rerun()
        else:
            st.markdown('<div class="status-disconnected">❌ Not Connected</div>', unsafe_allow_html=True)
            
            with st.form("auth_form"):
                st.markdown("#### Enter your credentials:")
                username = st.text_input("👤 Windows Username", placeholder="e.g., x01234567")
                password = st.text_input("🔒 Password", type="password")
                account_id = st.text_input("🏢 AWS Account ID", placeholder="12-digit account ID")
                
                region = st.selectbox(
                    "🌍 AWS Region",
                    ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                    index=0
                )
                
                submit = st.form_submit_button("🔗 Connect to AWS", type="primary", use_container_width=True)
                
                if submit:
                    if not all([username, password, account_id]):
                        st.error("Please fill in all fields")
                    else:
                        success, message = authenticate_user(username, password, account_id, region)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

def render_main_interface():
    """Render the main chat interface"""
    st.markdown('<div class="main-header"><h1>🤖 AWS Bedrock LLM Chat Application</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        st.info("👈 Please authenticate with AWS Portal in the sidebar to begin chatting.")
        
        st.markdown("### 📋 About This Application")
        st.markdown("""
        This application provides a secure interface to interact with AWS Bedrock LLM models through your corporate AWS portal authentication.
        
        **Features:**
        - 🔐 Secure AWS Portal authentication
        - 💬 Interactive chat interface
        - 🤖 Support for multiple Bedrock models
        - 📊 Chat history management
        - ⚙️ Configurable model parameters
        - 📥 Download chat history
        """)
        
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. Enter your Windows credentials in the sidebar
        2. Provide your AWS Account ID
        3. Select your preferred region
        4. Click "Connect to AWS"
        5. Start chatting with the AI assistant!
        """)
        
        return
    
    # Model selection and settings
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💬 Chat with AI Assistant")
    
    with col2:
        with st.expander("⚙️ Settings"):
            model_id = st.selectbox(
                "Model",
                [
                    "anthropic.claude-3-sonnet-20240620-v1:0",
                    "anthropic.claude-3-haiku-20240620-v1:0",
                    "amazon.titan-text-express-v1"
                ],
                index=0
            )
            
            api_method = st.selectbox(
                "API Method",
                ["Converse API", "Invoke Model API"],
                index=0
            )
            
            max_tokens = st.slider("Max Tokens", 100, 8000, 4000)
            st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
            st.session_state.top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.1)
    
    # Chat history display
    st.markdown("### 📝 Chat History")
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message-user"><strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-assistant"><strong>AI Assistant:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([6, 1, 1])
        
        with col1:
            prompt = st.text_area(
                "Enter your message:",
                placeholder="Ask me anything...",
                height=100,
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.form_submit_button("📨 Send", type="primary", use_container_width=True)
        
        with col3:
            sample_prompts = [
                "What is the capital of the UK?",
                "Explain machine learning",
                "Write a Python function",
                "Benefits of cloud computing"
            ]
            
            if st.form_submit_button("🎲 Random", use_container_width=True):
                import random
                prompt = random.choice(sample_prompts)
                st.rerun()
    
    if send_button and prompt:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Call Bedrock API
        with st.spinner("🤔 AI is thinking..."):
            if api_method == "Converse API":
                success, response = call_bedrock_converse(prompt, model_id, max_tokens)
            else:
                success, response = call_bedrock_invoke(prompt, model_id, max_tokens)
        
        if success:
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            st.success("Response received!")
        else:
            st.error(response)
        
        st.rerun()
    
    # Chat management buttons
    if st.session_state.chat_history:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🗑️ Clear History", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            chat_json = json.dumps(st.session_state.chat_history, indent=2)
            st.download_button(
                "📥 Download Chat",
                data=chat_json,
                file_name=f"aws_bedrock_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def main():
    """Main application function"""
    initialize_session_state()
    render_sidebar()
    render_main_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("🔒 **Security Note:** This application securely handles your AWS credentials and does not store them permanently.")

if __name__ == "__main__":
    main()