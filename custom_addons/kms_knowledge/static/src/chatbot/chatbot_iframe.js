import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class ChatbotIframe extends Component {
    static template = "kms_knowledge.ChatbotIframe";
}

registry.category("actions").add("kms_knowledge.ChatbotIframe", ChatbotIframe);
