# AWS Bedrock Streamlit Application Setup Guide

## Overview
This guide will help you set up and run the AWS Bedrock LLM Chat Application using Streamlit. The application provides a secure interface to interact with AWS Bedrock LLM models through corporate AWS portal authentication.

## Prerequisites

### 1. Python Environment
- Python 3.8 or higher
- pip package manager

### 2. Required Python Packages
Create a `requirements.txt` file with the following dependencies:

```
streamlit>=1.28.0
boto3>=1.34.0
botocore>=1.34.0
urllib3>=1.26.0
```

### 3. AWS Access
- Valid corporate AWS portal credentials
- Access to AWS Bedrock service
- Appropriate IAM permissions for Bedrock model access

## Installation Steps

### Step 1: Set up Python Environment
```bash
# Create a virtual environment (recommended)
python -m venv streamlit-aws-env

# Activate the virtual environment
# On Windows:
streamlit-aws-env\Scripts\activate
# On macOS/Linux:
source streamlit-aws-env/bin/activate
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Step 3: Download Application Files
1. Save the main application as `streamlit-aws-bedrock.py`
2. Ensure the file has proper permissions to execute

### Step 4: Configure AWS Bedrock Model Access
1. Log into your AWS Management Console
2. Navigate to Amazon Bedrock service
3. Go to "Model Access" section
4. Request access to the following models:
   - Anthropic Claude 3 Sonnet
   - Anthropic Claude 3 Haiku
   - Amazon Titan Text Express (optional)

## Running the Application

### Method 1: Command Line
```bash
streamlit run streamlit-aws-bedrock.py
```

### Method 2: With Custom Port
```bash
streamlit run streamlit-aws-bedrock.py --server.port 8501
```

### Method 3: For External Access
```bash
streamlit run streamlit-aws-bedrock.py --server.address 0.0.0.0
```

## Application Features

### 🔐 Authentication
- Secure AWS portal login through sidebar
- Corporate proxy support
- Session management
- Automatic credential refresh

### 💬 Chat Interface
- Interactive conversation with AI models
- Real-time responses
- Chat history preservation
- Message formatting

### ⚙️ Configuration Options
- Multiple Bedrock models
- API method selection (Converse vs Invoke)
- Adjustable parameters (temperature, tokens, top-p)
- Region selection

### 📊 Data Management
- Chat history download (JSON format)
- Session persistence
- Clear conversation option
- Secure credential handling

## Security Considerations

### 🔒 Credential Security
- Passwords are masked in input fields
- Credentials stored only in session state
- No persistent storage of sensitive data
- Automatic cleanup on disconnect

### 🛡️ Network Security
- HTTPS connections to AWS services
- Corporate proxy authentication
- Encrypted data transmission
- Session-based authentication

### 🚨 Best Practices
- Use strong passwords
- Regularly rotate credentials
- Monitor AWS usage
- Log out when finished

## Troubleshooting

### Common Issues

#### 1. Authentication Failures
**Error:** "Incorrect username or password"
**Solution:**
- Verify corporate credentials
- Check username format (usually x01234567)
- Ensure password is correct
- Check network connectivity

#### 2. Connection Errors
**Error:** "Connection Error, check internet connection"
**Solution:**
- Verify corporate network access
- Check proxy settings
- Ensure firewall allows connections
- Try different network if possible

#### 3. Account Access Issues
**Error:** "Account not found in your accessible accounts"
**Solution:**
- Verify AWS account ID is correct (12 digits)
- Check account permissions
- Contact AWS administrator
- Ensure account is active

#### 4. Model Access Denied
**Error:** "Access denied to model"
**Solution:**
- Request model access in AWS Bedrock console
- Wait for approval (can take time)
- Check IAM permissions
- Try different model

#### 5. Streamlit Issues
**Error:** Various Streamlit-related errors
**Solution:**
- Update Streamlit: `pip install --upgrade streamlit`
- Clear browser cache
- Restart the application
- Check Python version compatibility

### 🔧 Debug Mode
To enable debug logging, add this environment variable:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run streamlit-aws-bedrock.py
```

### 📋 Log Files
Streamlit logs can be found at:
- Windows: `%APPDATA%\streamlit\logs\`
- macOS/Linux: `~/.streamlit/logs/`

## Advanced Configuration

### Environment Variables
You can set these environment variables for additional configuration:

```bash
# AWS Configuration
export AWS_DEFAULT_REGION=us-east-1
export AWS_BEDROCK_ENDPOINT_URL=https://bedrock-runtime.us-east-1.amazonaws.com

# Streamlit Configuration
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=localhost
```

### Custom Styling
The application includes custom CSS styling. You can modify the styles in the `st.markdown()` section of the code to customize:
- Colors and themes
- Layout and spacing
- Font styles
- Component appearance

### Model Configuration
To add new models, update the model selection list in the settings expander:
```python
model_id = st.selectbox(
    "Model",
    [
        "anthropic.claude-3-sonnet-20240620-v1:0",
        "anthropic.claude-3-haiku-20240620-v1:0", 
        "amazon.titan-text-express-v1",
        "your-new-model-id"  # Add new models here
    ],
    index=0
)
```

## Deployment Options

### 1. Local Development
- Run on localhost for development and testing
- Perfect for individual use
- Easy debugging and modification

### 2. Streamlit Community Cloud
- Free hosting option
- GitHub integration
- Public or private deployment
- Automatic updates

### 3. Corporate Server
- Deploy on internal corporate servers
- Enhanced security and control
- Integration with corporate systems
- Scalable for team use

### 4. Cloud Platforms
- AWS EC2 with security groups
- Docker containerization
- Load balancing for multiple users
- Integration with corporate identity providers

## Maintenance

### Regular Updates
- Keep dependencies up to date
- Monitor AWS service updates
- Update model IDs as needed
- Review security patches

### Monitoring
- Monitor AWS usage and costs
- Track application performance
- Review authentication logs
- Monitor user feedback

## Support and Contact

For technical support:
1. Check this documentation first
2. Review AWS Bedrock documentation
3. Consult Streamlit documentation
4. Contact your IT support team

## License and Compliance
Ensure compliance with:
- Corporate security policies
- AWS terms of service
- Data privacy regulations
- Industry-specific requirements

---

**Note:** This application is designed for corporate use with appropriate security measures. Always follow your organization's security guidelines and policies when deploying and using this application.