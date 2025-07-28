# Let me first analyze the provided code to understand the structure and create a Streamlit app

# Reading the structure from the provided files
aws_login_content = """
# Opening a Session & Creating a Client using Boto3

import boto3 # boto3 - AWS Package containing API Calls to AWS
from botocore.config import Config as botoConfig # botocore - AWS Packages contains advanced boto3 features
from datetime import datetime # datetime - To allow conversion between dates, timestamps and strings
import urllib3 # urllib3 - To connect to the AWS Portal API through HTTP Requests
import getpass # To hide password input on screen
import json # To export as JSON and parse HTTP Requests
from botocore.exceptions import ClientError

class AWSPortalClient:
    def __init__(self, username: str, password: str):
        self.proxy_host = 'primary-proxy.gslb.intranet.barcapint.com'
        self.proxy_port = '8080'
        self.username = username
        self.password = password
        self.http = urllib3.PoolManager()
        self.proxies = {'https': f'https://{self.username}:{self.password}@{self.proxy_host}:{self.proxy_port}'}

    def gather_token(self):
        tokenUrl = "https://awsportal.barcapint.com/v1/jwttoken"
        tokenBody = json.dumps({"username": self.username, "password": self.password})
        tokenResponse = self.http.request("POST", tokenUrl, body=tokenBody)
        if tokenResponse.status != 200:
            raise Exception("Incorrect username or password")
        return json.loads(tokenResponse.data.decode("utf-8"))["token"]

    def gather_credentials(self, token, accountId):
        # Implementation details...
        pass

    def create_client(self, credentials, service, region):
        # Implementation details...
        pass
"""

main_content = """
from aws_login import AWSPortalClient
import getpass
import json

username = 'x01468415'
password = getpass.getpass('Enter your password: ')
prompt = 'What is the capital of the UK'
region = 'us-east-1'
accountId = '908364080861'
service = 'bedrock-runtime'

aws_client = AWSPortalClient(username=username, password=password)
token = aws_client.gather_token()
credentials = aws_client.gather_credentials(token, accountId)
bedrock_runtime_client = aws_client.create_client(credentials, service, region)

message = [{"role": "user", "content": [{"text": prompt}]}]
model_id = 'anthropic.claude-3-sonnet-20240620-v1:0'
response = bedrock_runtime_client.converse(modelId=model_id, messages=message)
"""

print("Code analysis complete. Now I'll create the Streamlit application.")