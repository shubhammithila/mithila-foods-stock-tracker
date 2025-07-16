# Stock Tracker Configuration
APP_CONFIG = {
    "app_name": "Mithila Foods Stock Tracker",
    "version": "1.0.0",
    "author": "Stock Management System",
    "description": "Comprehensive stock tracking system for Mithila Foods"
}

# Default settings
DEFAULT_SETTINGS = {
    "auto_save": True,
    "backup_frequency": "daily",
    "data_retention_days": 365,
    "sync_to_sheets": False,
    "default_currency": "INR",
    "date_format": "%Y-%m-%d",
    "time_format": "%H:%M:%S",
    "undo_window_hours": 24,
    "max_recent_transactions": 50
}

# Sample product categories
PRODUCT_CATEGORIES = [
    "Rice",
    "Flour", 
    "Pulses",
    "Spices",
    "Oil",
    "Cereals",
    "Dry Fruits",
    "Condiments",
    "Ready to Cook",
    "Organic Products"
]

# Sample units
UNITS = [
    "kg",
    "gm", 
    "ltr",
    "ml",
    "pcs",
    "packets"
]

# Transaction types
TRANSACTION_TYPES = [
    "Stock Inward",
    "Packing",
    "FBA Sale",
    "FBA Sale (Bulk)",
    "Easy Ship Sale",
    "Easy Ship Sale (Bulk)",
    "Stock Adjustment",
    "Damage/Loss",
    "Return"
]

# File paths
FILE_PATHS = {
    "data_file": "stock_data.json",
    "backup_folder": "backups",
    "uploads_folder": "uploads",
    "exports_folder": "exports"
}
