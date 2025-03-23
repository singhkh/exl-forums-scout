#!/usr/bin/env python3
"""
Configuration loader for AEM Forms Question Scraper
Loads all settings from .env file
"""

import os
import re
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class ScraperConfig:
    """Configuration manager for the Adobe Experience League Forums Scout"""
    
    def __init__(self):
        """Initialize and load all configuration from environment"""
        self.load_basic_config()
        self.managers = self.load_managers()
        self.channels = self.load_channels()
        self.category_managers = self.load_category_managers()
        
    def load_basic_config(self):
        """Load basic scraper configuration"""
        # Calculate default date (1 month ago) if not specified in .env
        one_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Use .env value or command-line param (AEM_START_DATE), or fall back to 1 month ago
        self.start_date = os.environ.get('AEM_START_DATE', os.environ.get('AEM_DEFAULT_START_DATE', one_month_ago))
        
        self.max_pages = int(os.environ.get('AEM_MAX_PAGES', '10'))
        self.debug = os.environ.get('AEM_DEBUG', 'false').lower() == 'true'
        
        # Slack config
        self.slack_token = os.environ.get('SLACK_TOKEN', '')
        # Get slack channel from environment without hardcoded fallback
        self.slack_default_channel = os.environ.get('AEM_SLACK_CHANNEL', '')
        
    def load_managers(self):
        """Load manager configurations from environment variables"""
        managers = {}
        manager_pattern = re.compile(r'^MANAGER_([A-Z0-9_]+)_([A-Z]+)$')
        
        # Find all manager-related environment variables
        for key, value in os.environ.items():
            match = manager_pattern.match(key)
            if match:
                manager_id, attribute = match.groups()
                manager_id = manager_id.lower()
                
                if manager_id not in managers:
                    managers[manager_id] = {}
                
                if attribute.lower() == 'expertise':
                    # Convert comma-separated expertise to list
                    managers[manager_id][attribute.lower()] = [
                        exp.strip() for exp in value.split(',')
                    ]
                else:
                    managers[manager_id][attribute.lower()] = value
        
        return managers
    
    def load_channels(self):
        """Load channel configurations from environment variables"""
        channels = {}
        channel_pattern = re.compile(r'^CHANNEL_([A-Z0-9_]+)$')
        
        for key, value in os.environ.items():
            match = channel_pattern.match(key)
            if match:
                category = match.group(1).lower()
                category = category.replace('_', '-')
                channels[category] = value
        
        return channels
    
    def load_category_managers(self):
        """Load category-manager mappings from environment variables"""
        category_managers = {}
        mapping_pattern = re.compile(r'^CATEGORY_([A-Z0-9_]+)_MANAGERS$')
        
        for key, value in os.environ.items():
            match = mapping_pattern.match(key)
            if match:
                category = match.group(1).lower()
                category = category.replace('_', '-')
                
                # Store original manager IDs to properly match in self.managers
                manager_ids = [m.strip() for m in value.split(',')]
                category_managers[category] = manager_ids
        
        return category_managers
    
    def get_manager(self, manager_id):
        """Get manager information by ID"""
        if not manager_id:
            return None
        
        # Handle full manager ID format (e.g., "MANAGER_SUDHANSH")
        if manager_id.upper().startswith('MANAGER_'):
            manager_key = manager_id.upper().replace('MANAGER_', '').lower()
        else:
            manager_key = manager_id.lower()
        
        # Check if manager ID exists
        if manager_key in self.managers:
            manager_info = self.managers[manager_key]
            
            # Ensure slack handle has @ prefix and no spaces
            if 'slack' in manager_info:
                # Remove any spaces in the handle
                clean_handle = manager_info['slack'].replace(" ", "")
                # Ensure it starts with @ 
                if not clean_handle.startswith('@'):
                    clean_handle = f"@{clean_handle}"
                manager_info['slack'] = clean_handle
                
            return manager_info
        
        # Return basic info if manager not found
        return {
            'name': manager_key,
            'slack': f"@{manager_key}",
            'expertise': []
        }
    
    def get_channel(self, category):
        """Get Slack channel for a category"""
        # First try category-specific channel
        if category in self.channels:
            return self.channels[category]
        
        # Then try default channel from CHANNEL_DEFAULT
        if 'default' in self.channels:
            return self.channels['default']
        
        # Finally use the global default from AEM_SLACK_CHANNEL  
        return self.slack_default_channel
    
    def get_category_managers(self, category):
        """Get manager IDs for a specific category"""
        if category in self.category_managers:
            return [
                self.get_manager(manager_id) 
                for manager_id in self.category_managers[category]
            ]
        
        # Return default if no managers found for category
        if 'default' in self.category_managers:
            return [
                self.get_manager(manager_id)
                for manager_id in self.category_managers['default']
            ]
            
        return []
    
    def get_category_managers_for_slack(self, category):
        """Get Slack handles for a category - for tagging in messages."""
        if category in self.category_managers:
            slack_handles = []
            for manager_id in self.category_managers[category]:
                # Get the actual Slack handle from the manager config
                manager_info = self.get_manager(manager_id)
                if manager_info and 'slack' in manager_info:
                    # Use the slack handle as defined in .env
                    slack_handles.append(manager_info['slack'])
            
            # If we found handles, return them
            if slack_handles:
                return slack_handles
        
        # For default cases, always collect all manager slack handles
        # Get all manager Slack handles 
        all_manager_handles = []
        for manager_id in self.managers:
            if manager_id != 'default':  # Skip the default manager itself
                manager_info = self.managers[manager_id]
                if 'slack' in manager_info:
                    all_manager_handles.append(manager_info['slack'])
        
        if all_manager_handles:
            return all_manager_handles
        
        # If we've reached here and still have no handles, return an empty list
        # rather than using a generic team handle
        return []
