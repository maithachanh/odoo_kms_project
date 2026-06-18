# -*- coding: utf-8 -*-
"""
FoodHub Knowledge Assistant - Automated Evaluation Runner
===========================================================
Executes the 10 Test Cases defined in the Evaluation Metrics.
Constructs the Evaluation Results Table and logs sources & answers.
"""

import sys
import os
import json

# Ensure stdout encodes UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from rag_engine import get_rag_response

# 10 Test Cases
TEST_CASES = [
    {
        "id": "TC-01",
        "category": "Sales",
        "question": "How should employees handle customers with poor payment history?",
        "expected_source": "Poor Payment History Customer"
    },
    {
        "id": "TC-02",
        "category": "Sales",
        "question": "What benefits are available for VIP customers?",
        "expected_source": "VIP Customer Privileges"
    },
    {
        "id": "TC-03",
        "category": "Sales",
        "question": "How can pricing errors be fixed in the POS system?",
        "expected_source": "POS Pricing Fixes"
    },
    {
        "id": "TC-04",
        "category": "Purchase",
        "question": "When is the recommended time for purchasing inventory?",
        "expected_source": "Recommended Time for Purchasing"
    },
    {
        "id": "TC-05",
        "category": "Purchase",
        "question": "Why should unusually low supplier prices be avoided?",
        "expected_source": "Avoid Purchasing at Unusually Low Prices"
    },
    {
        "id": "TC-06",
        "category": "Helpdesk",
        "question": "How can staff prevent missing or incorrect deliveries?",
        "expected_source": "Preventing Missing or Incorrect Item Deliveries"
    },
    {
        "id": "TC-07",
        "category": "Front-of-House",
        "question": "How should customer complaints be handled?",
        "expected_source": "Customer Complaint Handling"
    },
    {
        "id": "TC-08",
        "category": "Technical & System",
        "question": "What should I do if the POS system is not responding?",
        "expected_source": "POS System Troubleshooting Guide"
    },
    {
        "id": "TC-09",
        "category": "Out-of-Scope Validation",
        "question": "Who will win the next FIFA World Cup?",
        "expected_source": "None (Out-of-Scope)"
    },
    {
        "id": "TC-10",
        "category": "Missing Knowledge Validation",
        "question": "What is FoodHub's employee reimbursement policy?",
        "expected_source": "None (Missing Knowledge)"
    }
]

def evaluate(provider="ollama"):
    print("=" * 70)
    print(f"         EVALUATING FOODHUB KNOWLEDGE ASSISTANT (LLM: {provider.upper()})")
    print("=" * 70)
    
    results = []
    
    for tc in TEST_CASES:
        print(f"\n[{tc['id']}] Category: {tc['category']}")
        print(f"Query: \"{tc['question']}\"")
        
        # Call RAG engine
        res = get_rag_response(
            query_string=tc["question"],
            user_role="public",
            provider=provider
        )
        
        answer = res["answer"]
        sources = res.get("sources", [])
        
        print(f"Sources Cited: {sources}")
        print(f"Response:\n{answer}\n")
        print("-" * 50)
        
        # Evaluate Fallback & Source Compliance
        fallback_compliance = "Pass"
        notes = ""
        
        if tc["id"] == "TC-09":
            # Out of scope query should trigger Scenario 6
            if "unable to provide answers outside the scope" in answer or "designed to assist with FoodHub-related" in answer:
                fallback_compliance = "Pass"
            else:
                fallback_compliance = "Fail"
                notes = "Failed to trigger Out-of-Scope Scenario 6 refusal."
        elif tc["id"] == "TC-10":
            # Missing knowledge should trigger Scenario 1
            if "could not find sufficient information" in answer:
                fallback_compliance = "Pass"
            else:
                fallback_compliance = "Fail"
                notes = "Failed to trigger No Information Scenario 1 fallback."
        else:
            # Operational queries must cite the expected document
            if tc["expected_source"] in sources:
                fallback_compliance = "Pass"
            else:
                fallback_compliance = "Fail"
                notes = f"Failed to retrieve expected source: {tc['expected_source']}"
        
        # Score allocations for metrics
        if fallback_compliance == "Pass":
            accuracy = 5
            groundedness = 5
            completeness = 5
            satisfaction = 5
        else:
            accuracy = 1 if tc["id"] in ["TC-09", "TC-10"] else 3
            groundedness = 1
            completeness = 1
            satisfaction = 1
            
        results.append({
            "tc": tc["id"],
            "accuracy": accuracy,
            "groundedness": groundedness,
            "completeness": completeness,
            "fallback": fallback_compliance,
            "satisfaction": satisfaction,
            "notes": notes or "All criteria met."
        })

    # Render results table
    print("\n" + "=" * 70)
    print("                        EVALUATION RESULTS TABLE")
    print("=" * 70)
    
    print("| Test Case | Accuracy | Groundedness | Completeness | Fallback Compliance | User Satisfaction | Notes |")
    print("| --------- | -------- | ------------ | ------------ | ------------------- | ----------------- | ----- |")
    for r in results:
        print(f"| {r['tc']:<9} | {r['accuracy']:<8} | {r['groundedness']:<12} | {r['completeness']:<12} | {r['fallback']:<19} | {r['satisfaction']:<17} | {r['notes']} |")
    
    print("=" * 70)
    
    # Save markdown report
    report_file = "evaluation_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# FoodHub Knowledge Assistant - Evaluation Report\n\n")
        f.write("| Test Case | Accuracy | Groundedness | Completeness | Fallback Compliance | User Satisfaction | Notes |\n")
        f.write("| --------- | -------- | ------------ | ------------ | ------------------- | ----------------- | ----- |\n")
        for r in results:
            f.write(f"| {r['tc']} | {r['accuracy']} | {r['groundedness']} | {r['completeness']} | {r['fallback']} | {r['satisfaction']} | {r['notes']} |\n")
    print(f"\nSaved evaluation table to: {report_file}")

if __name__ == "__main__":
    provider = "ollama"
    if len(sys.argv) > 1:
        provider = sys.argv[1]
    evaluate(provider)
