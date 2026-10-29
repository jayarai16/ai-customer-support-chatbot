/**
 * AI Customer Support Chatbot - Frontend Script
 * Handles all user interactions and API communication
 */

// ==================== Configuration ====================
const API_BASE = 'http://localhost:8000';
const RECONNECT_DELAY = 3000;
let sessionId = null;
let messageCount = 0;
let isLoading = false;

// ==================== DOM Elements ====================
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const messagesContainer = document.getElementById('messagesContainer');
const typingIndicator = document.getElementById('typingIndicator');
const sessionIdDisplay = document.getElementById('sessionId');
const welcomeSection = document.getElementById('welcomeSection');

// Modal elements
const historyModal = document.getElementById('historyModal');
const infoModal = document.getElementById('infoModal');
const historyBtn = document.getElementById('historyBtn');
const clearBtn = document.getElementById('clearBtn');
const infoBtn = document.getElementById('infoBtn');
const closeHistoryBtn = document.getElementById('closeHistoryBtn');
const closeHistoryBtn2 = document.getElementById('closeHistoryBtn2');
const closeInfoBtn = document.getElementById('closeInfoBtn');
const closeInfoBtn2 = document.getElementById('closeInfoBtn2');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing chatbot...');
    
    // Create session
    await createSession();
    
    // Set up event listeners
    setupEventListeners();
    
    // Add suggestion button listeners
    setupSuggestions();
    
    // Load business info
    await loadBusinessInfo();
    
    console.log('Chatbot initialized');
});

// ==================== Session Management ====================
async function createSession() {
    try {
        const response = await fetch(`${API_BASE}/session/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        if (!response.ok) throw new Error('Failed to create session');
        
        const data = await response.json();
        sessionId = data.session_id;
        sessionIdDisplay.textContent = sessionId.substring(0, 8) + '...';
        
        console.log('Session created:', sessionId);
    } catch (error) {
        console.error('Error creating session:', error);
        showToast('Failed to create session', 'error');
    }
}

// ==================== Event Listeners ====================
function setupEventListeners() {
    // Chat form submission
    chatForm.addEventListener('submit', handleSendMessage);
    
    // Modal controls
    historyBtn.addEventListener('click', openHistoryModal);
    clearBtn.addEventListener('click', clearChat);
    infoBtn.addEventListener('click', openInfoModal);
    
    closeHistoryBtn.addEventListener('click', closeHistoryModal);
    closeHistoryBtn2.addEventListener('click', closeHistoryModal);
    closeInfoBtn.addEventListener('click', closeInfoModal);
    closeInfoBtn2.addEventListener('click', closeInfoModal);
    clearHistoryBtn.addEventListener('click', clearConversationHistory);
    
    // Close modals on background click
    historyModal.addEventListener('click', (e) => {
        if (e.target === historyModal) closeHistoryModal();
    });
    infoModal.addEventListener('click', (e) => {
        if (e.target === infoModal) closeInfoModal();
    });
}

function setupSuggestions() {
    const suggestionButtons = document.querySelectorAll('.suggestion-btn');
    suggestionButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const question = e.currentTarget.getAttribute('data-question');
            messageInput.value = question;
            messageInput.focus();
        });
    });
}

// ==================== Message Handling ====================
async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message || isLoading) return;
    
    // Clear input
    messageInput.value = '';
    messageInput.focus();
    
    // Hide welcome section
    if (welcomeSection.style.display !== 'none') {
        welcomeSection.style.display = 'none';
    }
    
    // Add user message
    addMessage(message, 'user');
    
    // Show typing indicator
    showTypingIndicator();
    isLoading = true;
    
    try {
        // Send message to API
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                include_history: true
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add assistant response
        addMessage(data.response, 'assistant', {
            confidence: data.confidence,
            sources: data.sources,
            messageCount: data.message_count
        });
        
        messageCount = data.message_count;
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant', {
            isError: true
        });
        showToast('Failed to send message', 'error');
    } finally {
        isLoading = false;
    }
}

function addMessage(content, role, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = avatar;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = content;
    contentDiv.appendChild(textDiv);
    
    // Add metadata for assistant messages
    if (role === 'assistant' && !metadata.isError) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        
        if (metadata.confidence !== undefined) {
            const confidencePercent = Math.round(metadata.confidence * 100);
            const confidenceSpan = document.createElement('span');
            confidenceSpan.className = 'confidence-badge';
            confidenceSpan.textContent = `Confidence: ${confidencePercent}%`;
            metaDiv.appendChild(confidenceSpan);
        }
        
        if (metadata.sources && metadata.sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources-list';
            
            metadata.sources.forEach(source => {
                const sourceTag = document.createElement('span');
                sourceTag.className = 'source-tag';
                sourceTag.textContent = source.source || 'Source';
                sourcesDiv.appendChild(sourceTag);
            });
            
            contentDiv.appendChild(sourcesDiv);
        }
        
        contentDiv.appendChild(metaDiv);
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    scrollToBottom();
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

function scrollToBottom() {
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 0);
}

// ==================== History Management ====================
async function openHistoryModal() {
    historyModal.style.display = 'flex';
    
    try {
        const response = await fetch(`${API_BASE}/history/${sessionId}?limit=20`);
        if (!response.ok) throw new Error('Failed to load history');
        
        const data = await response.json();
        const historyContent = document.getElementById('historyContent');
        
        if (!data.conversations || data.conversations.length === 0) {
            historyContent.innerHTML = '<div class="empty-state"><p>No conversations yet</p></div>';
            return;
        }
        
        historyContent.innerHTML = '';
        data.conversations.forEach((conv) => {
            const item = document.createElement('div');
            item.className = 'history-item';
            
            const userDiv = document.createElement('div');
            userDiv.className = 'history-item-user';
            userDiv.textContent = '👤 You';
            
            const userTextDiv = document.createElement('div');
            userTextDiv.className = 'history-item-text';
            userTextDiv.textContent = conv.user_message;
            
            const botDiv = document.createElement('div');
            botDiv.className = 'history-item-user';
            botDiv.textContent = '🤖 Assistant';
            botDiv.style.marginTop = '8px';
            
            const botTextDiv = document.createElement('div');
            botTextDiv.className = 'history-item-text';
            botTextDiv.textContent = conv.assistant_response.substring(0, 150) + '...';
            
            const timeDiv = document.createElement('div');
            timeDiv.className = 'history-item-time';
            const date = new Date(conv.timestamp);
            timeDiv.textContent = date.toLocaleString();
            
            item.appendChild(userDiv);
            item.appendChild(userTextDiv);
            item.appendChild(botDiv);
            item.appendChild(botTextDiv);
            item.appendChild(timeDiv);
            
            historyContent.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading history:', error);
        document.getElementById('historyContent').innerHTML = 
            '<div class="empty-state"><p>Failed to load history</p></div>';
    }
}

function closeHistoryModal() {
    historyModal.style.display = 'none';
}

async function clearConversationHistory() {
    if (!confirm('Are you sure you want to clear the conversation history?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/history/clear/${sessionId}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Failed to clear history');
        
        showToast('Conversation history cleared', 'success');
        closeHistoryModal();
    } catch (error) {
        console.error('Error clearing history:', error);
        showToast('Failed to clear history', 'error');
    }
}

function clearChat() {
    if (!confirm('Are you sure you want to clear the chat?')) return;
    
    messagesContainer.innerHTML = '';
    welcomeSection.style.display = 'flex';
    messageCount = 0;
    
    showToast('Chat cleared', 'info');
}

// ==================== Info Modal ====================
async function openInfoModal() {
    infoModal.style.display = 'flex';
    
    try {
        const response = await fetch(`${API_BASE}/info`);
        if (!response.ok) throw new Error('Failed to load info');
        
        const data = await response.json();
        const infoContent = document.getElementById('infoContent');
        
        infoContent.innerHTML = `
            <h3>${data.name}</h3>
            <p>${data.description}</p>
            <p><strong>Founded:</strong> ${data.founded}</p>
            <p><strong>Headquarters:</strong> ${data.headquarters}</p>
            <p><strong>Website:</strong> <a href="${data.website}" target="_blank">${data.website}</a></p>
            
            <h3 style="margin-top: 16px;">Support</h3>
            <p><strong>Email:</strong> ${data.email || 'N/A'}</p>
            <p><strong>Phone:</strong> ${data.phone || 'N/A'}</p>
            <p><strong>Hours:</strong> ${data.business_hours || 'N/A'}</p>
        `;
    } catch (error) {
        console.error('Error loading info:', error);
        document.getElementById('infoContent').innerHTML = 
            '<div class="empty-state"><p>Failed to load information</p></div>';
    }
}

function closeInfoModal() {
    infoModal.style.display = 'none';
}

// ==================== Business Info Loading ====================
async function loadBusinessInfo() {
    // Pre-load business info for quick access
    try {
        const response = await fetch(`${API_BASE}/info`);
        if (response.ok) {
            const data = await response.json();
            console.log('Business info loaded:', data.name);
        }
    } catch (error) {
        console.warn('Could not preload business info:', error);
    }
}

// ==================== Toast Notifications ====================
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-message">${message}</span>`;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ==================== Error Handling ====================
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});

// ==================== Connection Status ====================
async function checkConnectionStatus() {
    try {
        const response = await fetch(`${API_BASE}/health`, {
            method: 'GET',
            timeout: 5000
        });
        return response.ok;
    } catch (error) {
        console.warn('Connection check failed:', error);
        return false;
    }
}

// Check connection on load and periodically
checkConnectionStatus().then(status => {
    if (!status) {
        showToast('Unable to connect to server. Please check your connection.', 'error');
    }
});

// Periodic health check
setInterval(checkConnectionStatus, 30000);

console.log('Chatbot script loaded successfully');
