// Chatbot WebSocket connection
let chatSocket = null;

// Toggle chatbot widget
function toggleChatbot() {
    const widget = document.getElementById('chatbot-widget');
    const toggle = document.getElementById('chatbot-toggle');
    
    if (widget.style.display === 'none') {
        widget.style.display = 'block';
        toggle.style.display = 'none';
        widget.classList.add('fade-in');
        connectWebSocket();
    } else {
        widget.style.display = 'none';
        toggle.style.display = 'block';
        disconnectWebSocket();
    }
}

// Connect to WebSocket
function connectWebSocket() {
    if (chatSocket === null) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = protocol + '//' + window.location.host + '/ws/chat/';
        
        console.log('Attempting to connect to WebSocket at:', wsUrl);
        
        chatSocket = new WebSocket(wsUrl);
        
        chatSocket.onopen = function(e) {
            console.log('WebSocket connected successfully');
            addSystemMessage('Kết nối thành công với trợ lý ảo');
        };
        
        chatSocket.onmessage = function(e) {
            console.log('WebSocket message received:', e.data);
            const data = JSON.parse(e.data);
            addMessage(data.message, data.type);
        };
        
        chatSocket.onclose = function(e) {
            console.log('WebSocket disconnected', e);
            chatSocket = null;
            
            if (e.code !== 1000) {
                addSystemMessage('Kết nối bị ngắt. Đang thử kết nối lại...');
                setTimeout(connectWebSocket, 3000);
            }
        };
        
        chatSocket.onerror = function(e) {
            console.error('WebSocket error:', e);
            addSystemMessage('Có lỗi xảy ra trong quá trình kết nối');
        };
    }
}

// Disconnect WebSocket
function disconnectWebSocket() {
    if (chatSocket !== null) {
        chatSocket.close();
        chatSocket = null;
    }
}

// Send message
function sendMessage(event) {
    event.preventDefault();
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (message && chatSocket) {
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        
        messageInput.value = '';
    }
}

// Add message to chat
function addMessage(message, type) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', type, 'fade-in');
    messageElement.textContent = message;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Add system message
function addSystemMessage(message) {
    addMessage(message, 'bot');
}

// Handle page visibility change
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        disconnectWebSocket();
    } else {
        const widget = document.getElementById('chatbot-widget');
        if (widget.style.display !== 'none') {
            connectWebSocket();
        }
    }
});

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 