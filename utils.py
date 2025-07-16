"""
Utility functions for the Stock Tracker application
"""

import pandas as pd
import datetime
import json
import os
from config import TRANSACTION_TYPES

def find_column(df, possible_names):
    """Find a column in DataFrame using possible column names"""
    for col in df.columns:
        if col in possible_names:
            return col
    return None

def validate_asin_format(asin):
    """Validate ASIN format (basic validation)"""
    if not asin:
        return False, "ASIN cannot be empty"
    
    asin = str(asin).strip()
    if len(asin) != 10:
        return False, "ASIN must be 10 characters long"
    
    # Basic alphanumeric check
    if not asin.isalnum():
        return False, "ASIN must contain only letters and numbers"
    
    return True, "Valid ASIN"

def format_currency(amount, currency="₹"):
    """Format currency with Indian rupee symbol"""
    if amount == 0:
        return f"{currency}0"
    
    # Convert to float if it's not already
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return f"{currency}0"
    
    # Format with comma separators
    if amount >= 1000:
        return f"{currency}{amount:,.0f}"
    else:
        return f"{currency}{amount:.2f}"

def get_date_range_options():
    """Get common date range options"""
    today = datetime.date.today()
    return {
        "Today": (today, today),
        "Yesterday": (today - datetime.timedelta(days=1), today - datetime.timedelta(days=1)),
        "Last 7 days": (today - datetime.timedelta(days=7), today),
        "Last 30 days": (today - datetime.timedelta(days=30), today),
        "This month": (today.replace(day=1), today),
        "Last month": (
            (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1),
            today.replace(day=1) - datetime.timedelta(days=1)
        )
    }

def export_to_excel(data, filename):
    """Export data to Excel file"""
    try:
        if isinstance(data, dict):
            # Multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, df in data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Single sheet
            data.to_excel(filename, index=False)
        
        return True, f"Data exported to {filename}"
    except Exception as e:
        return False, f"Export failed: {str(e)}"

def clean_excel_data(df):
    """Clean Excel data for processing"""
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Strip whitespace from string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    # Replace 'nan' strings with actual NaN
    df = df.replace('nan', pd.NA)
    
    return df

def validate_transaction_data(transaction_type, data):
    """Validate transaction data before processing"""
    errors = []
    
    if transaction_type == "Stock Inward":
        if not data.get('parent_id'):
            errors.append("Product selection is required")
        if not data.get('weight') or data.get('weight') <= 0:
            errors.append("Weight must be greater than 0")
    
    elif transaction_type == "Packing":
        if not data.get('parent_id'):
            errors.append("Product selection is required")
        if not data.get('asin'):
            errors.append("ASIN selection is required")
        if not data.get('quantity') or data.get('quantity') <= 0:
            errors.append("Quantity must be greater than 0")
    
    elif "Sale" in transaction_type:
        if not data.get('parent_id'):
            errors.append("Product selection is required")
        if not data.get('asin'):
            errors.append("ASIN selection is required")
        if not data.get('quantity') or data.get('quantity') <= 0:
            errors.append("Quantity must be greater than 0")
    
    return len(errors) == 0, errors

def get_product_summary(stock_data, parent_items, packet_variations):
    """Get product summary for dashboard"""
    summary = []
    
    for parent_id, stock in stock_data.items():
        if parent_id not in parent_items:
            continue
            
        product_info = parent_items[parent_id]
        loose_stock = stock.get('loose_stock', 0)
        
        # Calculate packed stock
        total_packed_units = 0
        total_packed_weight = 0
        
        for asin, units in stock.get('packed_stock', {}).items():
            if asin in packet_variations.get(parent_id, {}) and units > 0:
                weight_per_unit = packet_variations[parent_id][asin].get('weight', 0)
                total_packed_units += units
                total_packed_weight += units * weight_per_unit
        
        summary.append({
            'parent_id': parent_id,
            'product_name': product_info['name'],
            'category': product_info.get('category', 'General'),
            'loose_stock': loose_stock,
            'packed_units': total_packed_units,
            'packed_weight': total_packed_weight,
            'total_weight': loose_stock + total_packed_weight,
            'last_updated': stock.get('last_updated', '')
        })
    
    return summary

def calculate_stock_value(stock_data, parent_items, packet_variations):
    """Calculate total stock value"""
    total_value = 0
    
    for parent_id, stock in stock_data.items():
        if parent_id not in parent_items:
            continue
            
        # Calculate packed stock value
        for asin, units in stock.get('packed_stock', {}).items():
            if asin in packet_variations.get(parent_id, {}) and units > 0:
                mrp = packet_variations[parent_id][asin].get('mrp', 0)
                total_value += units * mrp
    
    return total_value

def get_low_stock_alerts(stock_data, parent_items, packet_variations, threshold=10):
    """Get low stock alerts"""
    alerts = []
    
    for parent_id, stock in stock_data.items():
        if parent_id not in parent_items:
            continue
            
        product_name = parent_items[parent_id]['name']
        
        # Check loose stock
        loose_stock = stock.get('loose_stock', 0)
        if loose_stock < threshold:
            alerts.append({
                'type': 'Low Loose Stock',
                'product': product_name,
                'current_stock': loose_stock,
                'threshold': threshold,
                'unit': 'kg'
            })
        
        # Check packed stock
        for asin, units in stock.get('packed_stock', {}).items():
            if asin in packet_variations.get(parent_id, {}) and units < 5:  # Low packed stock threshold
                description = packet_variations[parent_id][asin].get('description', asin)
                alerts.append({
                    'type': 'Low Packed Stock',
                    'product': f"{product_name} ({description})",
                    'current_stock': units,
                    'threshold': 5,
                    'unit': 'units'
                })
    
    return alerts
