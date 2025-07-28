// Application State Management
class AppState {
    constructor() {
        this.isAuthenticated = false;
        this.credentials = null;
        this.chatHistory = [];
        this.currentModel = 'anthropic.claude-3-sonnet-20240620-v1:0';
        this.settings = {
            maxTokens: 4000,
            temperature: 0.7,
            topP: 0.9
        };
    }

    setAuthenticated(credentials) {
        this.isAuthenticated = true;
        this.credentials = credentials;
    }

    disconnect() {
        this.isAuthenticated = false;
        this.credentials = null;
        this.chatHistory = [];
    }

    addMessage(message) {
        this.chatHistory.push({
            ...message,
            timestamp: new Date().toISOString()
        });
    }

    clearHistory() {
        this.chatHistory = [];
    }

    getHistoryAsJSON() {
        return JSON.stringify(this.chatHistory, null, 2);
    }
}

// AWS Portal Client Simulation
class AWSPortalClient {
    constructor() {
        this.config = {
            proxy_host: "primary-proxy.gslb.intranet.barcapint.com",
            proxy_port: "8080",
            token_url: "https://awsportal.barcapint.com/v1/jwttoken",
            roles_url: "https://awsportal.barcapint.com/v1/creds-provider/roles?size=200",
            credentials_url: "https://awsportal.barcapint.com/v1/creds-provider/provide-credentials/"
        };
        this.token = null;
    }

    async authenticate(username, password, accountId, region) {
        // Simulate authentication delay
        await this.delay(2000);
        
        // Basic validation
        if (!username || !password || !accountId || !region) {
            throw new Error('All fields are required');
        }

        if (username.length < 3) {
            throw new Error('Invalid username format');
        }

        if (password.length < 6) {
            throw new Error('Password must be at least 6 characters');
        }

        if (!/^\d{12}$/.test(accountId)) {
            throw new Error('AWS Account ID must be 12 digits');
        }

        // Simulate successful authentication
        this.token = `jwt_token_${Date.now()}`;
        
        return {
            username,
            accountId,
            region,
            token: this.token,
            expires: new Date(Date.now() + 8 * 60 * 60 * 1000) // 8 hours
        };
    }

    async getCredentials(accountId, region) {
        if (!this.token) {
            throw new Error('Not authenticated');
        }

        // Simulate API call delay
        await this.delay(1000);

        return {
            accessKeyId: `AKIA${Math.random().toString(36).substr(2, 16).toUpperCase()}`,
            secretAccessKey: Math.random().toString(36).substr(2, 40),
            sessionToken: Math.random().toString(36).substr(2, 200),
            region: region
        };
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Bedrock Client Simulation
class BedrockClient {
    constructor(credentials) {
        this.credentials = credentials;
        this.models = {
            'anthropic.claude-3-sonnet-20240620-v1:0': 'Claude 3 Sonnet',
            'anthropic.claude-3-haiku-20240620-v1:0': 'Claude 3 Haiku',
            'amazon.titan-text-express-v1': 'Titan Text Express'
        };
    }

    async invokeModel(modelId, prompt, settings) {
        // Simulate API call delay
        await this.delay(Math.random() * 3000 + 1000);

        // Simulate different responses based on model
        const responses = {
            'anthropic.claude-3-sonnet-20240620-v1:0': this.generateClaudeResponse(prompt),
            'anthropic.claude-3-haiku-20240620-v1:0': this.generateHaikuResponse(prompt),
            'amazon.titan-text-express-v1': this.generateTitanResponse(prompt)
        };

        const response = responses[modelId] || responses['anthropic.claude-3-sonnet-20240620-v1:0'];
        
        return {
            content: response,
            model: this.models[modelId],
            modelId: modelId,
            inputTokens: Math.floor(prompt.length / 4),
            outputTokens: Math.floor(response.length / 4),
            settings: settings
        };
    }

    generateClaudeResponse(prompt) {
        const responses = {
            'what is the capital of the uk': "The capital of the United Kingdom is London. London is not only the political capital but also the largest city in the UK, serving as the center of government, finance, and culture. It's home to important institutions like the Houses of Parliament, Buckingham Palace, and the Bank of England.",
            
            'explain machine learning': "Machine learning is a subset of artificial intelligence (AI) that enables computers to learn and make decisions from data without being explicitly programmed for every scenario. Think of it like teaching a computer to recognize patterns - just as you might learn to recognize spam emails by seeing many examples, machine learning algorithms can identify patterns in data and make predictions or decisions based on those patterns. Common applications include recommendation systems, image recognition, and natural language processing.",
            
            'python fibonacci': "Here's a Python function to calculate Fibonacci numbers:\n\n```python\ndef fibonacci(n):\n    \"\"\"Calculate the nth Fibonacci number.\"\"\"\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        a, b = 0, 1\n        for _ in range(2, n + 1):\n            a, b = b, a + b\n        return b\n\n# Example usage:\nprint(fibonacci(10))  # Output: 55\n```\n\nThis function uses an iterative approach which is efficient for larger numbers. The Fibonacci sequence starts with 0, 1, and each subsequent number is the sum of the two preceding ones.",
            
            'cloud computing benefits': "Cloud computing offers several key benefits:\n\n1. **Cost Efficiency**: Reduces capital expenditure on hardware and infrastructure\n2. **Scalability**: Easily scale resources up or down based on demand\n3. **Accessibility**: Access applications and data from anywhere with internet\n4. **Reliability**: Built-in redundancy and backup systems\n5. **Security**: Enterprise-grade security measures and compliance\n6. **Automatic Updates**: Software and security updates handled automatically\n7. **Collaboration**: Enhanced team collaboration with shared resources\n8. **Disaster Recovery**: Built-in backup and recovery capabilities\n\nThese advantages make cloud computing an attractive option for businesses of all sizes."
        };

        const key = prompt.toLowerCase();
        for (const [keyword, response] of Object.entries(responses)) {
            if (key.includes(keyword)) {
                return response;
            }
        }

        return `I understand you're asking about: "${prompt}"\n\nAs Claude 3 Sonnet, I'm designed to provide helpful, accurate, and thoughtful responses. While I don't have access to real-time information, I can help you with a wide range of topics including analysis, writing, coding, math, and creative tasks. Could you provide more specific details about what you'd like to know or accomplish?`;
    }

    generateHaikuResponse(prompt) {
        return `As Claude 3 Haiku, I provide quick and efficient responses. For your query: "${prompt}"\n\nI'm optimized for speed while maintaining quality. I can help with various tasks including summarization, basic analysis, and straightforward questions. What specific assistance do you need?`;
    }

    generateTitanResponse(prompt) {
        return `Amazon Titan Text Express responding to: "${prompt}"\n\nI'm designed to provide reliable text generation and analysis. I can assist with content creation, summarization, and text processing tasks. How can I help you today?`;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        this.container.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            toast.classList.add('slide-out');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }

    success(message) {
        this.show(message, 'success');
    }

    error(message) {
        this.show(message, 'error');
    }

    warning(message) {
        this.show(message, 'warning');
    }

    info(message) {
        this.show(message, 'info');
    }
}

// Main Application Class
class AWSBedrockApp {
    constructor() {
        this.state = new AppState();
        this.portalClient = new AWSPortalClient();
        this.bedrockClient = null;
        this.toast = new ToastManager();
        
        this.initializeElements();
        this.attachEventListeners();
        this.updateUI();
    }

    initializeElements() {
        // Authentication elements
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.accountIdInput = document.getElementById('account-id');
        this.regionSelect = document.getElementById('region');
        this.connectBtn = document.getElementById('connect-btn');
        this.connectionStatus = document.getElementById('connection-status');
        
        // Chat elements
        this.chatHistory = document.getElementById('chat-history');
        this.promptInput = document.getElementById('prompt-input');
        this.modelSelect = document.getElementById('model-select');
        this.sendBtn = document.getElementById('send-btn');
        
        // Settings elements
        this.maxTokensInput = document.getElementById('max-tokens');
        this.temperatureInput = document.getElementById('temperature');
        this.topPInput = document.getElementById('top-p');
        
        // Control elements
        this.clearChatBtn = document.getElementById('clear-chat-btn');
        this.downloadChatBtn = document.getElementById('download-chat-btn');
        this.disconnectBtn = document.getElementById('disconnect-btn');
        
        // Loading elements
        this.loadingOverlay = document.getElementById('loading-overlay');
    }

    attachEventListeners() {
        // Authentication
        this.connectBtn.addEventListener('click', () => this.handleConnect());
        this.disconnectBtn.addEventListener('click', () => this.handleDisconnect());
        
        // Chat
        this.sendBtn.addEventListener('click', () => this.handleSendMessage());
        this.promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                this.handleSendMessage();
            }
        });
        
        // Settings
        this.modelSelect.addEventListener('change', (e) => {
            this.state.currentModel = e.target.value;
        });
        
        this.maxTokensInput.addEventListener('change', (e) => {
            this.state.settings.maxTokens = parseInt(e.target.value);
        });
        
        this.temperatureInput.addEventListener('change', (e) => {
            this.state.settings.temperature = parseFloat(e.target.value);
        });
        
        this.topPInput.addEventListener('change', (e) => {
            this.state.settings.topP = parseFloat(e.target.value);
        });
        
        // Session management
        this.clearChatBtn.addEventListener('click', () => this.handleClearChat());
        this.downloadChatBtn.addEventListener('click', () => this.handleDownloadChat());
        
        // Enter key for authentication
        [this.usernameInput, this.passwordInput, this.accountIdInput].forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.handleConnect();
                }
            });
        });

        // Attach sample prompt listeners after DOM is ready
        this.attachSamplePromptListeners();
    }

    attachSamplePromptListeners() {
        // Use event delegation since sample prompts might be recreated
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('sample-prompt-btn')) {
                this.promptInput.value = e.target.textContent;
                if (this.state.isAuthenticated) {
                    this.promptInput.focus();
                }
            }
        });
    }

    async handleConnect() {
        const username = this.usernameInput.value.trim();
        const password = this.passwordInput.value.trim();
        const accountId = this.accountIdInput.value.trim();
        const region = this.regionSelect.value;

        if (!username || !password || !accountId) {
            this.toast.error('Please fill in all required fields');
            return;
        }

        this.setLoadingState(true, 'Connecting to AWS Portal...');
        this.updateConnectionStatus('connecting', 'Connecting...');

        try {
            // Authenticate with AWS Portal
            const credentials = await this.portalClient.authenticate(username, password, accountId, region);
            
            // Get AWS credentials
            const awsCredentials = await this.portalClient.getCredentials(accountId, region);
            
            // Create Bedrock client
            this.bedrockClient = new BedrockClient(awsCredentials);
            
            // Update state
            this.state.setAuthenticated({
                ...credentials,
                awsCredentials
            });
            
            this.updateConnectionStatus('connected', 'Connected');
            this.updateUI();
            this.toast.success(`Successfully connected to AWS account ${accountId}`);
            
            // Clear password for security
            this.passwordInput.value = '';
            
        } catch (error) {
            this.updateConnectionStatus('error', 'Connection Failed');
            this.toast.error(`Connection failed: ${error.message}`);
        } finally {
            this.setLoadingState(false);
        }
    }

    handleDisconnect() {
        this.state.disconnect();
        this.bedrockClient = null;
        this.updateConnectionStatus('info', 'Disconnected');
        this.updateUI();
        this.clearChatHistory();
        this.toast.info('Disconnected from AWS Portal');
        
        // Clear all input fields
        this.usernameInput.value = '';
        this.passwordInput.value = '';
        this.accountIdInput.value = '';
        this.promptInput.value = '';
    }

    async handleSendMessage() {
        const prompt = this.promptInput.value.trim();
        if (!prompt) {
            this.toast.error('Please enter a prompt');
            return;
        }

        if (!this.state.isAuthenticated) {
            this.toast.error('Please authenticate first');
            return;
        }

        // Add user message
        this.addMessageToChat({
            role: 'user',
            content: prompt,
            model: this.state.currentModel
        });

        // Clear input and show loading
        this.promptInput.value = '';
        this.setSendButtonLoading(true);

        try {
            // Call Bedrock API
            const response = await this.bedrockClient.invokeModel(
                this.state.currentModel,
                prompt,
                this.state.settings
            );

            // Add assistant response
            this.addMessageToChat({
                role: 'assistant',
                content: response.content,
                model: response.model,
                modelId: response.modelId,
                inputTokens: response.inputTokens,
                outputTokens: response.outputTokens
            });

        } catch (error) {
            this.toast.error(`Failed to get response: ${error.message}`);
            this.addMessageToChat({
                role: 'error',
                content: `Error: ${error.message}`,
                model: 'System'
            });
        } finally {
            this.setSendButtonLoading(false);
        }
    }

    addMessageToChat(message) {
        this.state.addMessage(message);
        
        // Remove welcome message if it exists
        const welcomeMessage = this.chatHistory.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${message.role}`;
        
        const header = document.createElement('div');
        header.className = 'message-header';
        
        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${message.role}`;
        avatar.textContent = message.role === 'user' ? 'U' : 'AI';
        
        const senderName = document.createElement('span');
        senderName.textContent = message.role === 'user' ? 'You' : (message.model || 'Assistant');
        
        header.appendChild(avatar);
        header.appendChild(senderName);
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = this.formatMessageContent(message.content);
        
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        meta.textContent = `${message.model || 'Unknown'} • ${new Date().toLocaleTimeString()}`;
        
        if (message.inputTokens && message.outputTokens) {
            meta.textContent += ` • ${message.inputTokens} in, ${message.outputTokens} out tokens`;
        }
        
        messageElement.appendChild(header);
        messageElement.appendChild(content);
        messageElement.appendChild(meta);
        
        this.chatHistory.appendChild(messageElement);
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
    }

    formatMessageContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/```(\w+)?\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    handleClearChat() {
        if (this.state.chatHistory.length === 0) {
            this.toast.info('Chat history is already empty');
            return;
        }
        
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.state.clearHistory();
            this.clearChatHistory();
            this.toast.info('Chat history cleared');
        }
    }

    clearChatHistory() {
        this.chatHistory.innerHTML = `
            <div class="welcome-message card">
                <div class="card__body">
                    <h3>Welcome to AWS Bedrock Chat</h3>
                    <p>Please authenticate using the sidebar to start chatting with AI models.</p>
                    <div class="sample-prompts">
                        <h4>Sample Prompts:</h4>
                        <div class="prompt-suggestions">
                            <button class="sample-prompt-btn">What is the capital of the UK?</button>
                            <button class="sample-prompt-btn">Explain machine learning in simple terms</button>
                            <button class="sample-prompt-btn">Write a Python function to calculate fibonacci numbers</button>
                            <button class="sample-prompt-btn">What are the benefits of cloud computing?</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    handleDownloadChat() {
        if (this.state.chatHistory.length === 0) {
            this.toast.info('No chat history to download');
            return;
        }
        
        const data = this.state.getHistoryAsJSON();
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `aws-bedrock-chat-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.toast.success('Chat history downloaded');
    }

    updateUI() {
        const isAuthenticated = this.state.isAuthenticated;
        
        // Enable/disable form elements
        this.promptInput.disabled = !isAuthenticated;
        this.modelSelect.disabled = !isAuthenticated;
        this.sendBtn.disabled = !isAuthenticated;
        this.maxTokensInput.disabled = !isAuthenticated;
        this.temperatureInput.disabled = !isAuthenticated;
        this.topPInput.disabled = !isAuthenticated;
        
        // Enable/disable control buttons
        this.clearChatBtn.disabled = !isAuthenticated;
        this.downloadChatBtn.disabled = !isAuthenticated;
        this.disconnectBtn.disabled = !isAuthenticated;
        this.connectBtn.disabled = isAuthenticated;
        
        // Update input states
        this.usernameInput.disabled = isAuthenticated;
        this.passwordInput.disabled = isAuthenticated;
        this.accountIdInput.disabled = isAuthenticated;
        this.regionSelect.disabled = isAuthenticated;

        // Update placeholder text based on authentication status
        if (isAuthenticated) {
            this.promptInput.placeholder = 'Enter your prompt here...';
        } else {
            this.promptInput.placeholder = 'Please authenticate first to start chatting...';
        }
    }

    updateConnectionStatus(type, text) {
        const statusElement = this.connectionStatus.querySelector('.status');
        statusElement.className = `status status--${type}`;
        statusElement.textContent = text;
    }

    setLoadingState(loading, message = 'Loading...') {
        if (loading) {
            this.loadingOverlay.classList.remove('hidden');
            this.loadingOverlay.querySelector('p').textContent = message;
        } else {
            this.loadingOverlay.classList.add('hidden');
        }
    }

    setSendButtonLoading(loading) {
        const btnText = this.sendBtn.querySelector('.btn-text');
        const spinner = this.sendBtn.querySelector('.loading-spinner');
        
        if (loading) {
            btnText.textContent = 'Sending...';
            spinner.classList.remove('hidden');
            this.sendBtn.disabled = true;
        } else {
            btnText.textContent = 'Send Prompt';
            spinner.classList.add('hidden');
            this.sendBtn.disabled = !this.state.isAuthenticated;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AWSBedrockApp();
});