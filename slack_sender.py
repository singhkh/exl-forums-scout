#!/usr/bin/env python3
"""
Slack notification module for AEM Forms Question Scraper
Sends notifications with scraped questions to Slack channels
"""

import os
import logging
import json
import requests
from datetime import datetime

class SlackSender:
    """Slack notification sender for the AEM Forms Question Scraper"""
    
    def __init__(self, token=None, channel=None):
        """Initialize the Slack sender with API token and channel."""
        self.token = token or os.environ.get("AEM_SLACK_TOKEN")
        self.channel = channel or os.environ.get("AEM_SLACK_CHANNEL", "general")
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate Slack settings and log warnings for missing settings."""
        missing = []
        if not self.token:
            missing.append("Slack token")
        if not self.channel:
            missing.append("Slack channel")
                
        if missing:
            logging.warning(f"Missing Slack settings: {', '.join(missing)}")
    
    def create_slack_blocks(self, questions, start_date):
        """Create Slack message blocks with the list of questions."""
        # Get current date and time for the report
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create header blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "AEM Forms Unanswered Questions Report",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Report generated:* {now}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Questions since:* {start_date}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Found *{len(questions)}* unanswered questions."
                }
            },
            {
                "type": "divider"
            }
        ]
        
        if not questions:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "No unanswered questions found in the specified time period."
                }
            })
        else:
            # Add question blocks (up to 10 to avoid message size limits)
            display_count = min(10, len(questions))
            
            for i, question in enumerate(questions[:display_count]):
                title = question.get("title", "Untitled Question")
                url = question.get("url", "#")
                author = question.get("author", "Unknown Author")
                date = question.get("date", "Unknown Date")
                question_id = question.get("id", "N/A")
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*<{url}|{title}>*\nBy: {author} on {date}\nID: {question_id}"
                    }
                })
                
                # Add divider between questions
                if i < display_count - 1:
                    blocks.append({"type": "divider"})
            
            # If there are more questions than we're showing, add a note
            if len(questions) > display_count:
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"_Showing {display_count} of {len(questions)} questions. Check email report for complete list._"
                        }
                    ]
                })
        
        return blocks
    
    def send_notification(self, questions=None, start_date=None):
        """Send a Slack notification with the list of questions."""
        if not questions:
            logging.warning("No questions to send in the Slack notification")
            return False
            
        if not start_date:
            start_date = "unknown date"
            
        # Validate required Slack settings
        if not self.token or not self.channel:
            logging.error("Missing required Slack settings")
            return False
            
        # Prepare Slack API request
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Create Slack message blocks
        blocks = self.create_slack_blocks(questions, start_date)
        
        # Create the message payload
        data = {
            "channel": self.channel,
            "text": f"AEM Forms Unanswered Questions Report - Found {len(questions)} questions since {start_date}",
            "blocks": blocks
        }
        
        try:
            # Send the message to Slack
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get("ok"):
                logging.info(f"Slack notification sent successfully to #{self.channel}")
                return True
            else:
                error = response_data.get("error", "Unknown error")
                logging.error(f"Failed to send Slack notification: {error}")
                return False
            
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {str(e)}")
<<<<<<< Updated upstream
=======
            return False
    
    def send_categorized_notification(self, questions, start_date):
        """Send questions to appropriate channels based on categories."""
        if not questions:
            logging.warning("No questions to send in the categorized Slack notification")
            return False
            
        # Group questions by category
        categorized_questions = {}
        for question in questions:
            category = self.categorize_question(question)
            if category not in categorized_questions:
                categorized_questions[category] = []
            categorized_questions[category].append(question)
        
        # Log what channels are available in config
        logging.debug(f"Available channels in config: {self.config.channels}")
        
        # Prepare summary statistics
        message_summary = []
        total_questions = 0
        messages_sent = 0
        
        # Send to each channel with appropriate manager tagging
        results = []
        for category, category_questions in categorized_questions.items():
            # Get appropriate channel for this category
            channel = self.config.get_channel(category)
            logging.info(f"Category '{category}' mapped to Slack channel: #{channel}")
            
            # Get managers for this category
            manager_tags = self.config.get_category_managers_for_slack(category)
            
            # If there are no manager tags, get ALL managers
            if not manager_tags:
                # Get all manager Slack handles
                all_manager_handles = []
                for manager_id in self.config.managers:
                    if manager_id != 'default':  # Skip the default manager itself
                        manager_info = self.config.managers[manager_id]
                        if 'slack' in manager_info:
                            all_manager_handles.append(manager_info['slack'])
                
                manager_tags = all_manager_handles
            
            # If we still have no managers, skip this category
            if not manager_tags:
                logging.warning(f"No managers found for category '{category}'. Skipping.")
                continue
            
            # Clean up manager tags to ensure proper Slack formatting - no spaces in tags
            cleaned_manager_tags = []
            for tag in manager_tags:
                # Remove any spaces in the tag itself (e.g., "@ username" → "@username") 
                cleaned_tag = tag.replace(" ", "")
                cleaned_manager_tags.append(cleaned_tag)
            
            manager_mentions = ", ".join(cleaned_manager_tags)
            # Debug log the actual managers being tagged
            logging.info(f"Tagging the following managers for category '{category}': {manager_mentions}")
            
            # Prepare the message blocks without headers
            blocks = []
            
            # Create a simple message with the managers and request
            intro_text = f"{manager_mentions}, can you help answer the following customer queries?"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": intro_text
                }
            })
            
            # Add a small divider
            blocks.append({"type": "divider"})
            
            # Add each question
            for question in category_questions:
                question_blocks = self.create_question_block(question)
                blocks.extend(question_blocks)
            
            # Create a simple text message that summarizes
            text = self.report_summary
            
            # Send to this category's channel
            result = self.send_blocks_to_channel(channel, blocks, text)
            
            # Add to summary statistics
            if result:
                messages_sent += 1
                message_summary.append({
                    "category": category,
                    "channel": channel,
                    "managers": manager_tags,
                    "questions": len(category_questions)
                })
                total_questions += len(category_questions)
            
            results.append(result)
        
        # Print summary report
        print("\n" + "="*80)
        print(f"SLACK NOTIFICATION SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print(f"Total Slack messages sent: {messages_sent}")
        print(f"Total questions processed: {total_questions}")
        print(f"Categories processed: {len(message_summary)}")
        print("-"*80)
        
        # Enhanced reporting with more details
        print("DISTRIBUTION BY CHANNEL:")
        channel_stats = {}
        for summary in message_summary:
            channel = summary["channel"]
            if channel not in channel_stats:
                channel_stats[channel] = {
                    "questions": 0,
                    "categories": set(),
                    "managers": set()
                }
            channel_stats[channel]["questions"] += summary["questions"]
            channel_stats[channel]["categories"].add(summary["category"])
            channel_stats[channel]["managers"].update(summary["managers"])
        
        for channel, stats in channel_stats.items():
            categories_str = ", ".join(stats["categories"])
            print(f"  #{channel}: {stats['questions']} questions across {len(stats['categories'])} categories")
            print(f"    Categories: {categories_str}")
            print(f"    Tagged managers: {len(stats['managers'])}")
        
        print("-"*80)
        print("DISTRIBUTION BY MANAGER:")
        manager_stats = {}
        for summary in message_summary:
            for manager in summary["managers"]:
                if manager not in manager_stats:
                    manager_stats[manager] = {
                        "questions": 0,
                        "categories": set(),
                        "channels": set()
                    }
                manager_stats[manager]["questions"] += summary["questions"]
                manager_stats[manager]["categories"].add(summary["category"])
                manager_stats[manager]["channels"].add(summary["channel"])
        
        for manager, stats in manager_stats.items():
            print(f"  {manager}: {stats['questions']} questions across {len(stats['categories'])} categories")
            print(f"    Channels: {', '.join(stats['channels'])}")
        
        print("-"*80)
        print(f"{'CATEGORY':<25} {'CHANNEL':<20} {'QUESTIONS':<10} {'MANAGERS'}")
        print("-"*80)
        
        for summary in message_summary:
            managers_str = ", ".join(summary["managers"])
            # Use a more generous limit and indicate truncation differently
            if len(managers_str) > 55:
                # Count how many managers we have
                manager_count = len(summary["managers"])
                shown_count = min(3, manager_count)  # Show at most 3 managers
                managers_shown = ", ".join(summary["managers"][:shown_count])
                managers_str = f"{managers_shown} (and {manager_count - shown_count} more)"
            
            print(f"{summary['category']:<25} {summary['channel']:<20} {summary['questions']:<10} {managers_str}")
        
        print("="*80 + "\n")
        
        return all(results)  # Success only if all messages sent successfully
    
    def categorize_question(self, question):
        """Determine the category of a question based on topics and content."""
        # Check for explicit topic tags first
        for topic in question.get("topics", []):
            topic_lower = topic.lower().replace(' ', '-')
            
            # Direct match with category
            for category in self.config.category_managers.keys():
                if topic_lower == category or topic_lower in category:
                    return category
                    
        # Content-based matching
        content = question.get("title", "") + " " + question.get("content", "")
        content_lower = content.lower()
        
        # Check each category for keyword matches
        category_scores = {}
        for manager_id, manager_info in self.config.managers.items():
            if 'expertise' in manager_info:
                for expertise in manager_info['expertise']:
                    if expertise in content_lower:
                        # Find categories this manager is assigned to
                        for category, managers in self.config.category_managers.items():
                            if manager_id in managers:
                                category_scores[category] = category_scores.get(category, 0) + 1
        
        if category_scores:
            # Return highest scoring category
            return max(category_scores.items(), key=lambda x: x[1])[0]
            
        # Default fallback
        return "default"
    
    def send_blocks_to_channel(self, channel, blocks, text):
        """Send a list of blocks to a specific Slack channel."""
        if not blocks or not channel:
            logging.error("Missing blocks or channel for sending notification")
            return False
            
        # Prepare Slack API request
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Create the message payload
        data = {
            "channel": channel,
            "text": text,
            "blocks": blocks
        }
        
        try:
            # Send the message to Slack
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get("ok"):
                logging.info(f"Slack notification sent successfully to #{channel}")
                return True
            else:
                error = response_data.get("error", "Unknown error")
                logging.error(f"Failed to send Slack notification to #{channel}: {error}")
                return False
            
        except Exception as e:
            logging.error(f"Failed to send Slack notification to #{channel}: {str(e)}")
>>>>>>> Stashed changes
            return False 