import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { AskAiChatbot } from "@kms_knowledge/chatbot/ask_ai_chatbot";

export class AskAiSystray extends Component {
    static template = "kms_knowledge.AskAiSystray";
    static components = { AskAiChatbot };
    
    setup() {
        this.state = useState({
            isOpen: false,
        });
    }
    
    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
    }
}

registry.category("systray").add("kms_knowledge.AskAiSystray", {
    Component: AskAiSystray,
}, { sequence: 25 });
