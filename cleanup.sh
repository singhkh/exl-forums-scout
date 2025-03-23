#!/bin/bash

# Cleanup script for AEM Scraper project
echo "Starting cleanup process..."

# List of files to delete
TO_DELETE=(
  # Temporary config files
  ".env.new"
  "ai_categorizer.py.new"
  
  # Analysis files
  "category_analysis.py"
  "enhanced_category_analysis.py"
  "category_analysis_20250322_105155.json"
  "enhanced_analysis_20250322_105858.json"
  "categorization_results.json" # Test categorization results
  
  # Subcategory configuration files
  "subcategory_managers.md"
  "subcategory_assignments.csv"
  "update_subcategories.py"
  
  # macOS system files
  ".DS_Store"
  
  # This cleanup script itself (optional)
  # Uncomment if you want the script to delete itself after running
  # "cleanup.sh"
)

# Optional: Add any __pycache__ directories
PYCACHE_CLEANUP=true

# Confirm deletion with user
echo "The following files will be deleted:"
for file in "${TO_DELETE[@]}"; do
  if [ -f "$file" ]; then
    echo "  - $file"
  else
    echo "  - $file (not found)"
  fi
done

if [ "$PYCACHE_CLEANUP" = true ]; then
  echo "  - All __pycache__ directories"
fi

echo ""
read -p "Proceed with deletion? (y/n): " confirm

if [ "$confirm" != "y" ]; then
  echo "Cleanup cancelled."
  exit 0
fi

# Delete the files
echo "Deleting files..."
for file in "${TO_DELETE[@]}"; do
  if [ -f "$file" ]; then
    rm "$file"
    echo "  - Deleted: $file"
  fi
done

# Clean up Python cache files
if [ "$PYCACHE_CLEANUP" = true ]; then
  find . -type d -name "__pycache__" -exec rm -rf {} +2>/dev/null || true
  find . -name "*.pyc" -delete
  echo "  - Cleaned Python cache files"
fi

echo "Cleanup completed!" 