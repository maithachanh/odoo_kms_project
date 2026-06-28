import { Component, useState, useRef, onPatched } from "@odoo/owl";

export class AskAiChatbot extends Component {
    static template = "kms_knowledge.AskAiChatbot";
    static props = {
        onClose: Function,
    };

    setup() {
        this.chatBodyRef = useRef("chatBody");
        
        this.state = useState({
            isMinimized: false,
            inputValue: "",
            isTyping: false,
            messages: [
                {
                    id: 1,
                    role: "assistant",
                    content: "Hello, what can I help you with?",
                    sources: "",
                }
            ],
            suggestions: [
                "Summarize what the last tickets complain about",
                "Bar chart of top-selling products",
                "Which project costs us the most?"
            ]
        });

        onPatched(() => {
            this.scrollToBottom();
        });
    }

    scrollToBottom() {
        if (this.chatBodyRef.el) {
            this.chatBodyRef.el.scrollTop = this.chatBodyRef.el.scrollHeight;
        }
    }

    async sendMessage(text) {
        if (!text || text.trim() === "") return;
        
        const userMsg = {
            id: Date.now(),
            role: "user",
            content: text,
        };
        this.state.messages.push(userMsg);
        this.state.inputValue = "";
        this.state.isTyping = true;

        try {
            // Standard JSON-RPC call using fetch to ensure compatibility across all lifecycle phases
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
            
            if (result && result.result && result.result.success) {
                const responseData = result.result;
                let sourcesText = "";
                if (responseData.permission_denied) {
                    sourcesText = "NO PERMISSION";
                } else if (responseData.guardrail_triggered) {
                    sourcesText = "🚨 GUARDRAIL BLOCKED";
                } else if (responseData.fallback_triggered) {
                    sourcesText = "⚠️ FALLBACK ACTIVATED";
                } else if (responseData.sources && responseData.sources.length > 0) {
                    sourcesText = "📚 Sources: " + responseData.sources.join(", ");
                }

                this.state.messages.push({
                    id: Date.now() + 1,
                    role: "assistant",
                    content: responseData.answer,
                    sources: sourcesText,
                });
            } else {
                const errMsg = result && result.result ? result.result.error : "Unknown backend error";
                this.state.messages.push({
                    id: Date.now() + 1,
                    role: "assistant",
                    content: "Error: " + errMsg,
                    isError: true,
                });
            }
        } catch (err) {
            this.state.messages.push({
                id: Date.now() + 1,
                role: "assistant",
                content: "Cannot connect to server. Ensure RAG API server is running on the host machine.",
                isError: true,
            });
        } finally {
            this.state.isTyping = false;
        }
    }

    onKeyPress(ev) {
        if (ev.key === "Enter") {
            this.sendMessage(this.state.inputValue);
        }
    }

    toggleMinimize() {
        this.state.isMinimized = !this.state.isMinimized;
    }
}
