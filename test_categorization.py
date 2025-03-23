#!/usr/bin/env python3
"""
Test script for the AI categorization functionality
"""

import argparse
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our categorization function
from ai_categorizer import categorize_forum_question

# Sample test questions
TEST_QUESTIONS = [
    {
        "title": "Adaptive Form not submitting properly",
        "content": "I created an adaptive form but the submit button doesn't work. I've checked the JavaScript and it looks fine.",
        "topics": ["adaptive-forms", "javascript"]
    },
    {
        "title": "How to make forms accessible for screen readers?",
        "content": "I need to ensure my forms work with screen readers. What are the accessibility guidelines I should follow for AEM Forms?",
        "topics": ["accessibility", "adaptive-forms"]
    },
    {
        "title": "XDP to Adaptive Form conversion issues",
        "content": "When I try to convert my XDP form to an Adaptive Form, some fields are not appearing correctly. How can I fix this?",
        "topics": ["xdp", "conversion", "adaptive-forms"]
    },
    {
        "title": "Using React SDK with Adaptive Forms",
        "content": "I want to use the Forms React SDK to create a headless form experience. How do I get started?",
        "topics": ["headless", "react", "sdk"]
    },
    {
        "title": "How to generate PDF output from Adaptive Form?",
        "content": "I need to generate a PDF document of record from my adaptive form submission. What's the best approach?",
        "topics": ["document-of-record", "pdf"]
    }
]

def test_categorization():
    """Test the categorization function with sample questions"""
    print("Testing AI Categorization with formsgenailib\n")
    
    results = []
    
    # Check if credentials are set
    client_id = os.environ.get("ADOBE_FIREFALL_CLIENT_ID")
    client_secret = os.environ.get("ADOBE_FIREFALL_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("WARNING: Adobe Firefall credentials not found in .env file")
        print("The test will attempt to use the fallback categorization\n")
    
    for i, question in enumerate(TEST_QUESTIONS):
        print(f"Test {i+1}: {question['title']}")
        
        # Call our categorization function
        category, confidence, explanation = categorize_forum_question(
            question["title"],
            question["content"],
            question.get("topics")
        )
        
        # Store the results
        results.append({
            "question": question,
            "category": category,
            "confidence": confidence,
            "explanation": explanation
        })
        
        # Print the results
        print(f"  Category: {category}")
        print(f"  Confidence: {confidence}%")
        print(f"  Explanation: {explanation}")
        print("-" * 50)
    
    # Summary
    print("\nSummary of Results:")
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    for cat, count in categories.items():
        print(f"  {cat}: {count} questions")
    
    # Save results to file
    with open("categorization_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nDetailed results saved to categorization_results.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test AI categorization")
    args = parser.parse_args()
    
    test_categorization() 