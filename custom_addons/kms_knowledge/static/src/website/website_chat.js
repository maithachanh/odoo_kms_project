(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const trigger = document.getElementById('o_kms_website_chat_trigger');
        const chatWindow = document.getElementById('o_kms_website_chat_window');
        const closeBtn = document.getElementById('o_kms_website_chat_close');
        const minimizeBtn = document.getElementById('o_kms_website_chat_minimize');
        const inputField = document.getElementById('o_kms_website_chat_input');
        const sendBtn = document.getElementById('o_kms_website_chat_send');
        const chatBody = chatWindow ? chatWindow.querySelector('.o_kms_website_body') : null;
        const suggestionPills = chatWindow ? chatWindow.querySelectorAll('.o_kms_website_sug_pill') : [];

        if (!trigger || !chatWindow) return;

        // Toggle chat window
        trigger.addEventListener('click', function () {
            if (chatWindow.classList.contains('d-none')) {
                chatWindow.classList.remove('d-none');
                chatWindow.classList.add('d-flex');
                scrollToBottom();
            } else {
                chatWindow.classList.add('d-none');
                chatWindow.classList.remove('d-flex');
            }
        });

        // Close chat window
        closeBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            chatWindow.classList.add('d-none');
            chatWindow.classList.remove('d-flex');
        });

        // Minimize chat window
        minimizeBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            if (chatWindow.style.height === '48px') {
                chatWindow.style.height = '550px';
                minimizeBtn.querySelector('i').className = 'fa fa-minus';
            } else {
                chatWindow.style.height = '48px';
                minimizeBtn.querySelector('i').className = 'fa fa-window-maximize';
            }
        });

        // Scroll to bottom helper
        function scrollToBottom() {
            if (chatBody) {
                chatBody.scrollTop = chatBody.scrollHeight;
            }
        }

        // Send message to controller
        async function sendMessage(text) {
            if (!text || text.trim() === '') return;

            // Add user message to UI
            const userMsgHtml = `
                <div class="o_kms_website_msg_wrapper d-flex justify-content-end mb-3" style="animation: fadeIn 0.25s ease-out;">
                    <div class="o_kms_website_msg_bubble bg-primary text-white p-2.5 rounded-3 small user-msg" style="max-width: 85%; word-break: break-word; border-bottom-right-radius: 2px; background: linear-gradient(135deg, #6366f1, #4f46e5) !important; padding: 8px 12px;">
                        <div class="small" style="white-space: pre-wrap; line-height: 1.4;">${escapeHtml(text)}</div>
                    </div>
                </div>
            `;
            chatBody.insertAdjacentHTML('beforeend', userMsgHtml);
            inputField.value = '';
            scrollToBottom();

            // Add typing indicator
            const typingId = 'typing-' + Date.now();
            const typingHtml = `
                <div id="${typingId}" class="o_kms_website_msg_wrapper d-flex justify-content-start mb-3" style="animation: fadeIn 0.25s ease-out;">
                    <div class="o_kms_website_msg_bubble bg-light text-dark p-2.5 rounded-3 small assistant-msg" style="max-width: 85%; word-break: break-word; border-bottom-left-radius: 2px; background-color: #2a2b36 !important; color: #e2e8f0 !important; border: 1px solid rgba(255,255,255,0.04); padding: 8px 12px;">
                        <span class="o_kms_website_typing_dots small">AI is thinking<span>.</span><span>.</span><span>.</span></span>
                    </div>
                </div>
            `;
            chatBody.insertAdjacentHTML('beforeend', typingHtml);
            scrollToBottom();

            try {
                // Call Odoo JSON RPC controller
                const response = await fetch('/kms/ask_ai', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            query: text,
                        },
                    }),
                });

                const result = await response.json();
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();

                if (result && result.result && result.result.success) {
                    const data = result.result;
                    let sourcesText = '';
                    if (data.permission_denied) {
                        sourcesText = 'NO PERMISSION';
                    } else if (data.guardrail_triggered) {
                        sourcesText = '🚨 GUARDRAIL BLOCKED';
                    } else if (data.fallback_triggered) {
                        sourcesText = '⚠️ FALLBACK ACTIVATED';
                    } else if (data.sources && data.sources.length > 0) {
                        sourcesText = '📚 Sources: ' + data.sources.join(', ');
                    }

                    let sourcesHtml = '';
                    if (sourcesText) {
                        sourcesHtml = `
                            <div class="mt-1 text-muted" style="font-size: 0.75em; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 2px; color: #94a3b8;">
                                ${escapeHtml(sourcesText)}
                            </div>
                        `;
                    }

                    const aiMsgHtml = `
                        <div class="o_kms_website_msg_wrapper d-flex justify-content-start mb-3" style="animation: fadeIn 0.25s ease-out;">
                            <div class="o_kms_website_msg_bubble bg-light text-dark p-2.5 rounded-3 small assistant-msg" style="max-width: 85%; word-break: break-word; border-bottom-left-radius: 2px; background-color: #2a2b36 !important; color: #e2e8f0 !important; border: 1px solid rgba(255,255,255,0.04); padding: 8px 12px;">
                                <div class="small" style="white-space: pre-wrap; line-height: 1.4;">${escapeHtml(data.answer)}</div>
                                ${sourcesHtml}
                            </div>
                        </div>
                    `;
                    chatBody.insertAdjacentHTML('beforeend', aiMsgHtml);
                } else {
                    const errMsg = result && result.result ? result.result.error : 'Unknown backend error';
                    showErrorMsg('Error: ' + errMsg);
                }
            } catch (err) {
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();
                showErrorMsg('Cannot connect to server. Ensure RAG API server is running.');
            }
            scrollToBottom();
        }

        function showErrorMsg(msg) {
            const errHtml = `
                <div class="o_kms_website_msg_wrapper d-flex justify-content-start mb-3">
                    <div class="o_kms_website_msg_bubble bg-light text-dark p-2.5 rounded-3 small assistant-msg" style="max-width: 85%; word-break: break-word; border-bottom-left-radius: 2px; background-color: #2d1e1e !important; color: #ff8585 !important; border: 1px solid rgba(255,0,0,0.1); padding: 8px 12px;">
                        <div class="small">${escapeHtml(msg)}</div>
                    </div>
                </div>
            `;
            chatBody.insertAdjacentHTML('beforeend', errHtml);
        }

        function escapeHtml(text) {
            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        // Click on suggest pills
        suggestionPills.forEach(function (pill) {
            pill.addEventListener('click', function () {
                const query = pill.getAttribute('data-query');
                sendMessage(query);
            });
        });

        // Send by click send button
        sendBtn.addEventListener('click', function () {
            sendMessage(inputField.value);
        });

        // Send by press enter
        inputField.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage(inputField.value);
            }
        });
    });
})();
