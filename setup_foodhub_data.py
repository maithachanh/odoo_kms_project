# -*- coding: utf-8 -*-
import pandas as pd
import openpyxl

def main():
    print("Generating FoodHub Knowledge Base Excel files...")

    # 1. Generate kms_import_template.xlsx
    articles = [
        {
            "Title": "Poor Payment History Customer",
            "Content": "<h2>Poor Payment History Customer Handling</h2><p>Customers with a poor payment history or recurring invoice delays must be handled strictly on a cash-only or immediate digital payment basis. Delayed billing, credit agreements, or check payments are strictly prohibited for these accounts. Employees must politely inform the customer of this requirement and process payments immediately. In case of customer dispute or complaints, escalate the matter to the Sales Manager.</p>",
            "Tags": "Sales, Policy, Payment"
        },
        {
            "Title": "VIP Customer Privileges",
            "Content": "<h2>VIP Customer Privileges and Discounts</h2><p>VIP customers are entitled to priority reservation, dedicated seating, and a standard 10% discount on all dine-in orders. For VIP customer orders exceeding a total of $100, the Front-of-House (FOH) supervisor can approve an upgraded discount of 15%. This discount must be logged in the POS system under the VIP discount category.</p>",
            "Tags": "Sales, VIP, Discount"
        },
        {
            "Title": "POS Pricing Fixes",
            "Content": "<h2>POS Pricing Fixes Procedure</h2><p>In the event of a pricing error or incorrect display in the POS system during customer checkout, cashiers must stop the transaction immediately and notify the Front-of-House (FOH) Supervisor. The supervisor will investigate the discrepancy and use their manager override key to manually correct the price on the POS interface. Under no circumstances should cashiers process incorrect pricing or attempt to override transactions without supervisor approval.</p>",
            "Tags": "Sales, POS, Technical"
        },
        {
            "Title": "Recommended Time for Purchasing",
            "Content": "<h2>Recommended Time for Purchasing Inventory</h2><p>The recommended time for purchasing inventory is during the first week of every calendar month. Buying stock during this period allows FoodHub to secure bulk purchasing discounts from primary suppliers and ensures that all ingredients are received, checked, and shelved before the peak sales period mid-month.</p>",
            "Tags": "Purchase, Procurement, Inventory"
        },
        {
            "Title": "Avoid Purchasing at Unusually Low Prices",
            "Content": "<h2>Avoid Purchasing at Unusually Low Prices SOP</h2><p>Purchasing agents must avoid buying raw materials or inventory at unusually low prices. Suppliers offering items significantly below standard market rates often supply sub-standard quality ingredients, counterfeit goods, or products nearing their expiration dates. FoodHub maintains high food safety standards; all purchases below market price must be verified for origin and quality by the Quality Assurance (QA) team.</p>",
            "Tags": "Purchase, Supplier, Quality"
        },
        {
            "Title": "Preventing Missing or Incorrect Item Deliveries",
            "Content": "<h2>Preventing Missing or Incorrect Item Deliveries</h2><p>To prevent missing or incorrect items in deliveries, kitchen staff must perform a double-check of the packed food against the printed order ticket before sealing the package. Once verified, a colored safety seal must be applied to the bag. Delivery drivers are required to verify the delivery address and order ID on their mobile app upon arrival and during handoff to the customer.</p>",
            "Tags": "Helpdesk, Delivery, Kitchen"
        },
        {
            "Title": "Customer Complaint Handling",
            "Content": "<h2>Customer Complaint Handling Guidelines</h2><p>When handling customer complaints, employees must listen actively, maintain a professional and empathetic tone, apologize for the inconvenience, and offer an immediate resolution (such as a replacement item, a full refund, or a store credit voucher). If the customer remains dissatisfied or the complaint involves food safety issues, immediately escalate the case to the shift manager on duty.</p>",
            "Tags": "Front-of-House, Customer Service, SOP"
        },
        {
            "Title": "POS System Troubleshooting Guide",
            "Content": "<h2>POS System Troubleshooting Guide</h2><p>If the POS system is not responding or becomes frozen, follow these steps: first, verify that all power cables and network cables are securely connected. Second, perform a soft reboot by pressing and holding the power button for 5 seconds. If the system fails to restart or respond after rebooting, contact the IT Helpdesk immediately and switch to using the manual receipt book to record transactions.</p>",
            "Tags": "Technical, IT, Troubleshooting"
        }
    ]

    df_import = pd.DataFrame(articles)
    df_import.to_excel("kms_import_template.xlsx", index=False)
    print("Created kms_import_template.xlsx successfully.")

    # 2. Generate access_matrix.xlsx
    matrix_data = [
        {
            "Article Title": "Poor Payment History Customer",
            "Workspace Dimension": "sales",
            "Access Role": "public",
            "Target Synonym List (For Search Testing)": '["bad credit", "poor payment history", "delayed payment"]',
            "Description / Sample Content": "Handling rules for customers with poor credit history."
        },
        {
            "Article Title": "VIP Customer Privileges",
            "Workspace Dimension": "sales",
            "Access Role": "public",
            "Target Synonym List (For Search Testing)": '["vip discount", "vip privileges", "loyalty program"]',
            "Description / Sample Content": "VIP customer seating and discount rules."
        },
        {
            "Article Title": "POS Pricing Fixes",
            "Workspace Dimension": "sales",
            "Access Role": "public",
            "Target Synonym List (For Search Testing)": '["pos override", "pricing error", "incorrect price"]',
            "Description / Sample Content": "POS manual price override and error handling."
        },
        {
            "Article Title": "Recommended Time for Purchasing",
            "Workspace Dimension": "purchase",
            "Access Role": "public",
            "Target Synonym List (For Search Testing)": '["inventory purchase time", "procurement timing", "stock refill"]',
            "Description / Sample Content": "Best procurement window at start of month."
        },
        {
            "Article Title": "Avoid Purchasing at Unusually Low Prices",
            "Workspace Dimension": "purchase",
            "Access Role": "public",
            "Target Synonym List (For Search Testing)": '["cheap stock warning", "unusually low prices", "supplier check"]',
            "Description / Sample Content": "Quality risk management for cheap ingredients."
        },
        {
            "Article Title": "Preventing Missing or Incorrect Item Deliveries",
            "Workspace Dimension": "helpdesk",
            "Access Role": "public",
            "Target Synonym List (For Search Testing)": '["prevent delivery errors", "incorrect order", "missing items"]',
            "Description / Sample Content": "Verification checklists for order bags and drivers."
        },
        {
            "Article Title": "Customer Complaint Handling",
            "Workspace Dimension": "foh",
            "Access Role": "public",
            "Target Synonym List (For Search Testing)": '["customer complaints", "handling complaints", "refund rules"]',
            "Description / Sample Content": "Active listening, resolution, and escalation path."
        },
        {
            "Article Title": "POS System Troubleshooting Guide",
            "Workspace Dimension": "technical",
            "Access Role": "public",
            "Target Synonym List (For Search Testing)": '["pos frozen", "reboot cash register", "it support pos"]',
            "Description / Sample Content": "Check cables, soft reboot, switch to manual books."
        }
    ]

    df_matrix = pd.DataFrame(matrix_data)
    df_matrix.to_excel("access_matrix.xlsx", index=False)
    print("Created access_matrix.xlsx successfully.")

if __name__ == "__main__":
    main()
