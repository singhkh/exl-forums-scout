# AEM Forms Forum Scraper

This utility scrapes unanswered questions from the Adobe Experience Manager Forms forum on Adobe Experience League Communities.

## Features

- Scrapes unanswered questions from the AEM Forms forum
- Filters questions by date
- Collects title, author, date, content preview, and other metadata
- Supports pagination
- Saves results to a JSON file
- Automatically cleans up temporary files
- Sends email reports with formatted question listings

## Requirements

- Python 3.7+
- Required packages: `requests`, `beautifulsoup4`, `python-dotenv`

## Installation

1. Clone this repository or download the source code.
2. Create a virtual environment (recommended):

```bash
python -m venv aem_env
source aem_env/bin/activate  # On Windows: aem_env\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the scraper with the following command:

```bash
python scraper.py --start-date YYYY-MM-DD [--output FILENAME] [--max-pages N] [--debug] [--keep-html] [--cleanup]
```

### Arguments:

#### Scraping Options:
- `--start-date`: Only include questions posted after this date (required, format: YYYY-MM-DD)
- `--output`: Output JSON file name (default: questions.json)
- `--max-pages`: Maximum number of pages to scrape (default: 10)
- `--debug`: Enable debug mode (saves downloaded HTML to files)
- `--keep-html`: Keep HTML files after scraping (only applies in debug mode)
- `--cleanup`: Only clean up HTML files from previous runs without scraping

#### Email Options:
- `--email`: Send email report to this address (optional if default recipients configured)
- `--smtp-server`: SMTP server address (or set AEM_SMTP_SERVER env var)
- `--smtp-port`: SMTP server port (or set AEM_SMTP_PORT env var)
- `--sender-email`: Sender email address (or set AEM_SENDER_EMAIL env var)
- `--sender-name`: Sender name (or set AEM_SENDER_NAME env var)
- `--email-password`: Email password (or set AEM_EMAIL_PASSWORD env var)
- `--use-ssl`: Use SSL instead of TLS (or set AEM_USE_SSL=true)
- `--skip-email`: Skip sending email even if --email is provided

### Examples:

```bash
# Basic usage
python scraper.py --start-date 2023-01-01 --output aem_questions.json

# Debug mode with kept HTML files
python scraper.py --start-date 2023-01-01 --debug --keep-html

# Only clean up existing HTML files without scraping
python scraper.py --cleanup

# Scrape and send email report
python scraper.py --start-date 2023-01-01 --email user@example.com --smtp-server smtp.gmail.com --sender-email sender@gmail.com --email-password mypassword

# Scrape and send email report using SSL
python scraper.py --start-date 2023-01-01 --email user@example.com --smtp-server smtp.gmail.com --sender-email sender@gmail.com --email-password mypassword --use-ssl

# Scrape and send email report using environment variables for SMTP settings
export AEM_SMTP_SERVER=smtp.gmail.com
export AEM_SENDER_EMAIL=sender@gmail.com
export AEM_EMAIL_PASSWORD=mypassword
python scraper.py --start-date 2023-01-01 --email user@example.com

# Scrape and send email report with sender name
python scraper.py --start-date 2023-01-01 --email user@example.com --sender-name "AEM Scraper Bot" --sender-email sender@gmail.com
```

## Email Configuration

Email notifications can be configured in three ways:

1. **Command line arguments:** Provide SMTP settings directly via command line
2. **Environment variables:** Set the environment variables with your SMTP settings
3. **.env file:** Create a `.env` file with your SMTP settings (a template is provided)

The following settings can be configured:
   - `AEM_SMTP_SERVER`: SMTP server address
   - `AEM_SMTP_PORT`: SMTP server port (default: 587 for TLS, 465 for SSL)
   - `AEM_SENDER_EMAIL`: Sender email address
   - `AEM_SENDER_NAME`: Sender name (displayed in email clients)
   - `AEM_EMAIL_PASSWORD`: Email password or app password
   - `AEM_USE_SSL`: Set to "true" to use SSL instead of TLS
   - `AEM_DEFAULT_RECIPIENTS`: Comma-separated list of default email recipients (To: field)
   - `AEM_CC_RECIPIENTS`: Comma-separated list of CC recipients
   - `AEM_BCC_RECIPIENTS`: Comma-separated list of BCC recipients

### Using .env File

1. Copy the `.env.template` file to `.env` in the same directory
2. Edit the `.env` file with your SMTP settings
3. The script will automatically load these settings when run

### Using Gmail

If using Gmail as your SMTP provider:
1. Use `smtp.gmail.com` as the SMTP server
2. Use port 587 for TLS (default) or 465 for SSL
3. Enable 2-factor authentication and create an app password
4. Use your Gmail address as the sender and the app password instead of your regular password

### Email Format

The email report includes:
- Summary of scraped questions
- Each question with title, author, date, content preview, and stats
- Clickable links to the original questions
- Clean formatting in both HTML and plain text formats

## Output Format

The script produces a JSON file with an array of question objects. Each question contains the following fields:

- `id`: Question ID
- `title`: Question title
- `url`: URL to the question
- `author`: Username of the author
- `date`: Publication date (YYYY-MM-DD format)
- `content`: Preview of the question content
- `views`: Number of views
- `likes`: Number of likes
- `replies`: Number of replies
- `topics`: Array of topic tags

## File Management

The script handles temporary files as follows:

- HTML files from previous runs are automatically cleaned up before each new run
- When debug mode is enabled, HTML files of each page are saved for inspection
- By default, these files are deleted after successful scraping
- Use `--keep-html` to preserve the HTML files after scraping
- Use `--cleanup` to remove HTML files without running the scraper

## Troubleshooting

If you encounter issues:

1. Enable debug mode with the `--debug` flag to save the HTML content to files for inspection
2. Use `--keep-html` to preserve the HTML files for further analysis
3. Check your internet connection and proxy settings
4. Make sure the forum structure hasn't changed
5. For email issues, verify your SMTP settings and try sending to a different email address

## Running as a Scheduled Task

To run the scraper regularly and receive email notifications:

### Using cron (Linux/Mac):

```bash
# Run daily at 8 AM and save logs
0 8 * * * cd /path/to/aem_scraper && source aem_env/bin/activate && python scraper.py --start-date $(date -d "7 days ago" +\%Y-\%m-\%d) --email your@email.com > /path/to/logs/scraper_$(date +\%Y\%m\%d).log 2>&1
```

### Using Task Scheduler (Windows):

Create a batch file (run_scraper.bat) with:

```batch
@echo off
cd /d D:\path\to\aem_scraper
call aem_env\Scripts\activate
python scraper.py --start-date 2023-01-01 --email your@email.com
```

Then schedule this batch file to run at your desired interval using Windows Task Scheduler.

## License

MIT 