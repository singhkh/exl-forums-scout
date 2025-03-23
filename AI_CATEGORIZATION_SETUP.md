# Setting Up AI Categorization for AEM Forms Forum Scraper

This guide will help you set up the AI-powered categorization feature for the AEM Forms Forum Scraper. This feature uses Adobe's Firefall service to automatically categorize forum questions, making it easier to route them to the appropriate teams and Slack channels.

## Prerequisites

1. Adobe Firefall credentials (client ID, client secret, and client code)
2. Access to Adobe's internal Artifactory repository
3. The AEM Forms Forum Scraper installed and configured

## Installation Steps

### 1. Install the formsgenailib package

The AI categorization feature uses Adobe's `formsgenailib` package, which is available in Adobe's internal Artifactory repository. To install it:

```bash
# Set up environment variables for Artifactory access
export ARTIFACTORY_USER=your-artifactory-username
export ARTIFACTORY_API_TOKEN=your-artifactory-api-token

# Install the package using pip with the extra index URL
pip install --extra-index-url "https://${ARTIFACTORY_USER}:${ARTIFACTORY_API_TOKEN}@artifactory.corp.adobe.com/artifactory/api/pypi/pypi-aemforms-release-local/simple" formsgenailib
```

### 2. Configure Firefall credentials

1. Open your `.env` file (or create one from `.env.template` if you haven't already)
2. Add the following configuration parameters:

```
# Artifactory Configuration - For accessing formsgenailib package
ARTIFACTORY_USER=your-artifactory-username
ARTIFACTORY_API_TOKEN=your-artifactory-api-token

# Forms GenAI Library Configuration
ADOBE_FIREFALL_CLIENT_ID=your-client-id
ADOBE_FIREFALL_CLIENT_SECRET=your-client-secret
ADOBE_FIREFALL_CLIENT_CODE=your-client-code
ADOBE_FIREFALL_ORG_ID=your-org-id
```

These credentials are used to authenticate with Adobe's Firefall service for AI-powered categorization.

### 3. Test the AI categorization

Run the provided test script to verify that everything is set up correctly:

```bash
python test_categorization.py
```

This will generate a report showing how the AI categorizes a set of sample questions. The results will be saved to `categorization_results.json`.

If your credentials are not set up correctly, the system will fall back to rule-based categorization, which still provides reasonable results.

## How AI Categorization Works

1. When a forum question is processed, the system analyzes its title, content, and topic tags.
2. This information is sent to Adobe's Firefall service, which uses a language model to determine the most appropriate category.
3. The AI returns a category, confidence score, and explanation.
4. Based on the category, the question is routed to the appropriate Slack channel and relevant managers are tagged.
5. If the AI service is unavailable, the system falls back to rule-based categorization, ensuring that the system continues to function even if the AI service is down.

## Available Categories

The AI categorizes questions into the following categories:

- `adaptive-forms-authoring`: Questions about creating, editing, configuring, or designing Adaptive Forms
- `adaptive-forms-runtime`: Questions about form rendering, submission, or client-side behavior
- `adaptive-forms-core-components`: Questions about AEM Forms Core Components
- `adaptive-forms-headless`: Questions about headless forms or the Forms React SDK
- `document-of-record`: Questions about DoR generation, PDF output, or Document of Record issues
- `designer`: Questions about XDP forms, form design templates, or the Designer application
- `integration-third-party`: Questions about integrating with external systems or services
- `forms-workflow`: Questions about workflows, reviews, or approvals in Forms
- `core`: Questions about the AEM Forms core functionality or platform
- `accessibility`: Questions about making forms accessible or compliance with standards
- `security`: Questions related to form security or privacy

## Troubleshooting

### Error: "cannot import name 'GenAIClient' from 'formsgenailib'"

This error occurs if you have an outdated version of `formsgenailib`. Try reinstalling it with the latest version.

### Error: "ServiceCredentials.__init__() missing 1 required positional argument: 'client_code'"

Make sure you've provided the `ADOBE_FIREFALL_CLIENT_CODE` in your `.env` file.

### Error: "Error while getting token. Status code: 400"

This usually indicates invalid credentials. Double-check your client ID, client secret, and client code.

### No AI categorization occurs, falls back to rule-based

If the AI categorization isn't working but no error is shown, check:
1. Your internet connection
2. VPN access (if required)
3. Firewall settings
4. That your Firefall credentials have the necessary permissions

## Support

If you encounter any issues with the AI categorization feature, please contact the AEM Forms team or create an issue in the project repository. 