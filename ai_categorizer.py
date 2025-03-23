#!/usr/bin/env python3
"""AI-based categorization for AEM Forms forum questions using formsgenailib"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='[%(asctime)s] %(levelname)-8s %(message)s',
                   datefmt='%H:%M:%S')

def categorize_forum_question(title, content, topics=None):
    """
    Categorize an AEM Forms forum question using formsgenailib
    
    Args:
        title: Question title
        content: Question content/body text
        topics: List of forum topic tags (optional)
        
    Returns:
        tuple: (category, confidence, explanation)
    """
    try:
        # Import FirefallClient from formsgenailib
        from formsgenailib.core import ServiceCredentials
        from formsgenailib.core.firefall import FirefallClient, FirefallModels
        
        # Format topics for inclusion in prompt
        topics_text = ", ".join(topics) if topics and isinstance(topics, list) else "None"
        
        # Truncate content if too long
        content_truncated = content[:1500] if content else ""
        
        # Create the messages for chat completion
        system_message = {
            "role": "system",
            "content": """You are an expert in Adobe Experience Manager Forms who specializes in categorizing forum questions.
            Your task is to analyze each question and identify the most appropriate category."""
        }
        
        user_message = {
            "role": "user",
            "content": f"""Categorize this AEM Forms forum question into exactly ONE of these categories:
            
            - adaptive-forms-authoring: Questions about creating, editing, configuring or designing Adaptive Forms
            - adaptive-forms-runtime: Questions about form rendering, submission, or client-side behavior
            - adaptive-forms-core-components: Questions about AEM Forms Core Components specifically
            - adaptive-forms-headless: Questions about headless forms or the Forms React SDK
            - document-of-record: Questions about DoR generation, PDF output, or Document of Record issues
            - designer: Questions about XDP forms, form design templates, or the Designer application
            - integration-third-party: Questions about integrating with external systems or services
            - forms-workflow: Questions about workflows, reviews, or approvals in Forms
            - core: Questions about the AEM Forms core functionality or platform
            - accessibility: Questions about making forms accessible or compliance with standards
            - security: Questions related to form security or privacy
            
            
            - adaptive-forms-authoring-theme-customization: Customizing themes for adaptive forms including creating editing and applying themes
            - adaptive-forms-authoring-form-creation-errors: Errors encountered during the creation of new forms in AEM troubleshooting debugging
            - adaptive-forms-authoring-field-validation: Adding custom field validations patterns and rules to adaptive forms
            - adaptive-forms-authoring-component-development: Developing custom components integrating functionalities like calendars dropdowns
            - adaptive-forms-authoring-localization-multilingual: Creating multilingual adaptive forms adding dictionaries language-specific content
            - adaptive-forms-runtime-field-customization: Customizing form field values formatting and behavior
            - adaptive-forms-runtime-performance-optimization: Performance issues related to repeatable instances and form rendering
            - adaptive-forms-runtime-javascript-integration: Using JavaScript to interact with form elements and manipulate DOM
            - adaptive-forms-runtime-custom-submit-actions: Creating custom submit actions for forms emails or specific actions
            - adaptive-forms-runtime-form-tab-management: Managing form tabs controlling tab states and synchronizing data between tabs
            - adaptive-forms-core-components-rule-editor-functions: Custom functions and rule editor usage within Adaptive Form Core Components
            - adaptive-forms-core-components-component-development: Developing custom Core Form Components and resolving issues with component properties
            - adaptive-forms-core-components-script-validation: Script validation functionality issues and customizations within core components
            - adaptive-forms-core-components-date-input-validation: Date input validation and best practices for date-related fields
            - adaptive-forms-core-components-translation-localization: Translating core adaptive forms using machine translation handling localization
            - core-migration-to-forms-manager: Migrating XDPs or forms to AEM Forms Manager memory configuration setup
            - core-installation-configuration: Installing and configuring AEM Forms post-installation setup
            - core-error-handling-troubleshooting: Errors encountered in AEM Forms internal server errors null pointer exceptions
            - core-dispatcher-configuration: Configuring AEM Dispatcher internal redirects filter path rules form submissions
            - core-correspondence-management: Localization data dictionary failures and correspondence management
            - integration-third-party-form-integration: Integrating AEM Forms with third-party systems or services
            - integration-third-party-api-integration: Integrating AEM Forms with REST APIs or other types of APIs
            - integration-third-party-adobe-sign-configuration: Configuring Adobe Sign within AEM Forms workflows
            - integration-third-party-error-handling: Error handling within AEM Forms especially with core form components
            - integration-third-party-file-upload: Uploading files especially large files to external services like S3 buckets
            - designer-form-field-validation: Field validation within AEM Forms Designer subform validation problems
            - designer-ui-customization: Customizing the AEM Designer UI modifying palettes and the interface
            - designer-pdf-export: Exporting data handling font discrepancies exporting XML data
            - designer-master-page-layout: Creating and managing Master Pages portrait or landscape orientation
            - designer-scripting-functionality: Scripting alternatives issues with specific functions script-related errors
Return your answer in this format:
            Category: [category name]
            Confidence: [number between 0-100]
            Explanation: [brief explanation of why you chose this category]
            
            Question Title: {title}
            Question Content: {content_truncated}
            Question Topics: {topics_text}"""
        }
        
        # Create client credentials
        credentials = ServiceCredentials(
            client_id=os.environ.get("ADOBE_FIREFALL_CLIENT_ID", ""),
            client_secret=os.environ.get("ADOBE_FIREFALL_CLIENT_SECRET", ""),
            client_code=os.environ.get("ADOBE_FIREFALL_CLIENT_CODE", "")
        )
        
        # Create Firefall client
        client = FirefallClient(
            credentials=credentials,
            is_stage=True,  # Force staging environment
            org_id=os.environ.get("ADOBE_FIREFALL_ORG_ID", "aemforms_firefall_client")
        )
        
        # Get the AI response
        response = client.chat_completions(
            messages=[system_message, user_message],
            model=FirefallModels.gpt_35_turbo_0125,
            temperature=0.3,
            max_tokens=300
        )
        
        # Extract the text from the response
        response_text = ""
        if not response.is_error and response.choice_dict and "message" in response.choice_dict:
            if "content" in response.choice_dict["message"]:
                response_text = response.choice_dict["message"]["content"]
        
        # Parse the response
        category = None
        confidence = 0
        explanation = ""
        
        if response_text:
            lines = response_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.lower().startswith("category:"):
                    category = line.split(":", 1)[1].strip().lower()
                elif line.lower().startswith("confidence:"):
                    try:
                        confidence = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        confidence = 50  # Default medium confidence
                elif line.lower().startswith("explanation:"):
                    explanation = line.split(":", 1)[1].strip()
        
        # Validate the category and provide defaults if parsing failed
        if not category:
            logging.warning("Failed to parse LLM response for categorization")
            return "default", 0, "Failed to parse LLM response"
            
        return category, confidence, explanation
        
    except Exception as e:
        logging.error(f"Firefall categorization failed: {str(e)}")
        return fallback_categorization(title, content, topics)

def fallback_categorization(title, content, topics=None):
    """
    Simple rule-based categorization as fallback when LLM is unavailable
    """
    # Combine text for analysis
    combined_text = (title + " " + content).lower() if content else title.lower()
    topics_text = " ".join(topics).lower() if topics else ""
    all_text = combined_text + " " + topics_text
    
    # Simple keyword matching
    if any(kw in all_text for kw in ["document of record", "dor", "pdf output"]):
        return "document-of-record", 70, "Contains explicit references to Document of Record"
    elif any(kw in all_text for kw in ["xdp", "designer", "xfa"]):
        return "designer", 70, "Related to XDP or Designer application"
    elif any(kw in all_text for kw in ["accessibility", "wcag", "screen reader", "aria"]):
        return "accessibility", 70, "Contains accessibility terms"
    elif any(kw in all_text for kw in ["submit", "submission", "runtime", "javascript", "client"]):
        return "adaptive-forms-runtime", 70, "Related to form submission or runtime"
    elif any(kw in all_text for kw in ["core component", "core-component"]):
        return "adaptive-forms-core-components", 70, "Mentions core components"
    elif any(kw in all_text for kw in ["headless", "react", "api", "sdk"]):
        return "adaptive-forms-headless", 70, "Related to headless forms"
    elif any(kw in all_text for kw in ["integration", "third party", "connector"]):
        return "integration-third-party", 70, "About integrations"
    elif any(kw in all_text for kw in ["workflow", "review", "approval"]):
        return "forms-workflow", 70, "About form workflows"
    elif any(kw in all_text for kw in ["authoring", "creating", "editing", "configure"]):
        return "adaptive-forms-authoring", 70, "About creating or configuring forms"
    else:
        return "adaptive-forms-authoring", 50, "Default category (most common)"

# Simple test if run directly
if __name__ == "__main__":
    test_question = {
        "title": "Adaptive Form not submitting properly",
        "content": "I created an adaptive form but the submit button doesn't work. I've checked the JavaScript and it looks fine."
    }
    
    category, confidence, explanation = categorize_forum_question(
        test_question["title"],
        test_question["content"]
    )
    
    print(f"Category: {category}")
    print(f"Confidence: {confidence}%")
    print(f"Explanation: {explanation}") 