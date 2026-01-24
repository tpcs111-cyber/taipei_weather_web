/**
 * 天氣小助手 - 聊天功能
 */

// 聊天狀態
const chatState = {
    isOpen: false,
    pendingDate: null,
    invalidDateCount: 0,
    invalidConfirmCount: 0,
    messages: []
};

// 初始化聊天功能
function initChat() {
    createChatUI();
    loadWelcomeMessage();
}

// 建立聊天 UI
function createChatUI() {
    // 聊天按鈕
    const chatBtn = document.createElement('div');
    chatBtn.id = 'chatBtn';
    chatBtn.innerHTML = '<img src="/static/w_chet.png" alt="天氣小助手"><span>天氣小幫手</span>';
    chatBtn.title = '天氣小助手';
    chatBtn.onclick = toggleChat;

    // 聊天視窗
    const chatWindow = document.createElement('div');
    chatWindow.id = 'chatWindow';
    chatWindow.innerHTML = `
        <div class="chat-header">
            <span>🤖 天氣小助手</span>
            <button class="chat-close" onclick="toggleChat()">&times;</button>
        </div>
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-input-area">
            <input type="text" id="chatInput" placeholder="輸入日期查詢天氣..." onkeypress="handleChatKeypress(event)">
            <button onclick="sendChatMessage()">發送</button>
        </div>
    `;

    document.body.appendChild(chatBtn);
    document.body.appendChild(chatWindow);

    // 加入樣式
    addChatStyles();
}

// 加入聊天樣式
function addChatStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* 聊天按鈕 */
        #chatBtn {
            position: fixed;
            bottom: 20px;
            right: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            background: none;
            border: none;
            cursor: pointer;
            transition: transform 0.3s;
            z-index: 1000;
        }

        #chatBtn img {
            width: 60px;
            height: 60px;
            object-fit: contain;
            border-radius: 50%;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        #chatBtn span {
            font-size: 14px;
            font-weight: 700;
            color: #fff;
            white-space: nowrap;
            -webkit-text-stroke: 1px #000;
            text-shadow:
                -1px -1px 0 #000,
                1px -1px 0 #000,
                -1px 1px 0 #000,
                1px 1px 0 #000,
                0 0 3px rgba(0, 0, 0, 0.5);
        }

        #chatBtn:hover {
            transform: scale(1.1);
        }

        #chatBtn:hover img {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }

        /* 聊天視窗 */
        #chatWindow {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 350px;
            height: 450px;
            max-height: 50vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 30px rgba(0, 0, 0, 0.2);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 1000;
        }

        #chatWindow.open {
            display: flex;
        }

        /* 聊天標題列 */
        .chat-header {
            background: linear-gradient(135deg, #4ECDC4 0%, #44a08d 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
        }

        .chat-close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            line-height: 1;
        }

        .chat-close:hover {
            opacity: 0.8;
        }

        /* 聊天訊息區域 */
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f8f9fa;
        }

        /* 訊息樣式 */
        .chat-message {
            margin-bottom: 12px;
            display: flex;
        }

        .chat-message.user {
            justify-content: flex-end;
        }

        .chat-message.assistant {
            justify-content: flex-start;
        }

        .chat-bubble {
            max-width: 85%;
            padding: 10px 14px;
            border-radius: 15px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .chat-message.user .chat-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 5px;
        }

        .chat-message.assistant .chat-bubble {
            background: white;
            color: #333;
            border-bottom-left-radius: 5px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* 輸入區域 */
        .chat-input-area {
            display: flex;
            padding: 12px;
            background: white;
            border-top: 1px solid #eee;
        }

        .chat-input-area input {
            flex: 1;
            padding: 10px 14px;
            border: 2px solid #e2e8f0;
            border-radius: 20px;
            outline: none;
            font-size: 14px;
        }

        .chat-input-area input:focus {
            border-color: #4ECDC4;
        }

        .chat-input-area button {
            margin-left: 8px;
            padding: 10px 18px;
            background: linear-gradient(135deg, #4ECDC4 0%, #44a08d 100%);
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }

        .chat-input-area button:hover {
            transform: scale(1.05);
        }

        /* 載入中動畫 */
        .chat-loading {
            display: flex;
            gap: 4px;
            padding: 10px 14px;
        }

        .chat-loading span {
            width: 8px;
            height: 8px;
            background: #4ECDC4;
            border-radius: 50%;
            animation: chatBounce 1.4s infinite ease-in-out;
        }

        .chat-loading span:nth-child(1) { animation-delay: -0.32s; }
        .chat-loading span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes chatBounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        /* 響應式 */
        @media (max-width: 480px) {
            #chatWindow {
                width: calc(100% - 20px);
                right: 10px;
                bottom: 80px;
                height: 60vh;
                max-height: 60vh;
            }

            #chatBtn {
                right: 15px;
                bottom: 15px;
            }
        }
    `;
    document.head.appendChild(style);
}

// 切換聊天視窗
function toggleChat() {
    chatState.isOpen = !chatState.isOpen;
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.classList.toggle('open', chatState.isOpen);

    if (chatState.isOpen) {
        document.getElementById('chatInput').focus();
    }
}

// 載入歡迎訊息
async function loadWelcomeMessage() {
    try {
        const response = await fetch('/api/chat/init');
        const data = await response.json();
        addMessage('assistant', data.message);
    } catch (error) {
        addMessage('assistant', '你好！我是天氣小助手 🌤️\n\n請問你想查詢哪一天的台北天氣？');
    }
}

// 新增訊息到聊天區域
function addMessage(role, content) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    messageDiv.innerHTML = `<div class="chat-bubble">${escapeHtml(content)}</div>`;
    messagesContainer.appendChild(messageDiv);

    // 滾動到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // 儲存訊息
    chatState.messages.push({ role, content });
}

// 顯示載入中
function showLoading() {
    const messagesContainer = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message assistant';
    loadingDiv.id = 'chatLoading';
    loadingDiv.innerHTML = `
        <div class="chat-loading">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 移除載入中
function hideLoading() {
    const loading = document.getElementById('chatLoading');
    if (loading) loading.remove();
}

// 處理 Enter 鍵
function handleChatKeypress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

// 發送聊天訊息
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // 顯示使用者訊息
    addMessage('user', message);
    input.value = '';

    // 顯示載入中
    showLoading();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                pending_date: chatState.pendingDate,
                invalid_date_count: chatState.invalidDateCount,
                invalid_confirm_count: chatState.invalidConfirmCount
            })
        });

        const data = await response.json();

        // 更新狀態
        chatState.pendingDate = data.pending_date;
        chatState.invalidDateCount = data.invalid_date_count;
        chatState.invalidConfirmCount = data.invalid_confirm_count;

        // 顯示回應
        hideLoading();
        addMessage('assistant', data.response);

    } catch (error) {
        hideLoading();
        addMessage('assistant', '抱歉，發生錯誤，請稍後再試。');
        console.error('Chat error:', error);
    }
}

// HTML 跳脫
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', initChat);
