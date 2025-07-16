import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from utils import *
from config import *

# Configure page
st.set_page_config(
    page_title="Stock Tracker - Mithila Foods",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data persistence
DATA_FILE = "stock_data.json"

def initialize_sample_data():
    """Initialize with sample data"""
    st.session_state.parent_items = {
        "RICE_BASMATI": {"name": "Basmati Rice Premium", "unit": "kg", "category": "Rice"},
        "RICE_JASMINE": {"name": "Jasmine Rice Fragrant", "unit": "kg", "category": "Rice"},
        "WHEAT_FLOUR": {"name": "Wheat Flour Organic", "unit": "kg", "category": "Flour"},
        "PULSES_TOOR": {"name": "Toor Dal Premium", "unit": "kg", "category": "Pulses"}
    }
    
    st.session_state.packet_variations = {
        "RICE_BASMATI": {
            "B07BASMATI1KG": {"weight": 1, "asin": "B07BASMATI1KG", "description": "1kg Basmati Rice Pack", "mrp": 120},
            "B07BASMATI5KG": {"weight": 5, "asin": "B07BASMATI5KG", "description": "5kg Basmati Rice Pack", "mrp": 580}
        },
        "RICE_JASMINE": {
            "B07JASMINE1KG": {"weight": 1, "asin": "B07JASMINE1KG", "description": "1kg Jasmine Rice Pack", "mrp": 110}
        },
        "WHEAT_FLOUR": {
            "B07WHEAT1KG": {"weight": 1, "asin": "B07WHEAT1KG", "description": "1kg Wheat Flour Pack", "mrp": 45},
            "B07WHEAT5KG": {"weight": 5, "asin": "B07WHEAT5KG", "description": "5kg Wheat Flour Pack", "mrp": 220}
        },
        "PULSES_TOOR": {
            "B07TOOR1KG": {"weight": 1, "asin": "B07TOOR1KG", "description": "1kg Toor Dal Pack", "mrp": 85},
            "B07TOOR2KG": {"weight": 2, "asin": "B07TOOR2KG", "description": "2kg Toor Dal Pack", "mrp": 165}
        }
    }
    
    # Initialize stock data
    st.session_state.stock_data = {}
    for parent_id in st.session_state.parent_items:
        st.session_state.stock_data[parent_id] = {
            "loose_stock": 0,
            "packed_stock": {},
            "opening_stock": 0,
            "last_updated": datetime.datetime.now().isoformat()
        }
        for asin in st.session_state.packet_variations.get(parent_id, {}):
            st.session_state.stock_data[parent_id]["packed_stock"][asin] = 0
    
    st.session_state.transactions = []

def save_data():
    """Save data to JSON file"""
    data = {
        "stock_data": st.session_state.stock_data,
        "transactions": st.session_state.transactions,
        "parent_items": st.session_state.parent_items,
        "packet_variations": st.session_state.packet_variations,
        "daily_opening_stock": getattr(st.session_state, 'daily_opening_stock', {}),
        "last_updated": datetime.datetime.now().isoformat()
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                st.session_state.stock_data = data.get("stock_data", {})
                st.session_state.transactions = data.get("transactions", [])
                st.session_state.parent_items = data.get("parent_items", {})
                st.session_state.packet_variations = data.get("packet_variations", {})
                st.session_state.daily_opening_stock = data.get("daily_opening_stock", {})
        except Exception as e:
            st.error(f"Error loading data: {e}")
            initialize_sample_data()
    else:
        initialize_sample_data()

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

if not st.session_state.initialized:
    load_data()
    st.session_state.initialized = True

def record_transaction(transaction_type, parent_id, asin=None, quantity=0, weight=0, notes="", batch_id=None, transaction_date=None):
    """Record a transaction and return transaction ID"""
    transaction_id = len(st.session_state.transactions) + 1
    
    # Use provided date or default to today
    if transaction_date is None:
        transaction_date = datetime.date.today()
    
    transaction = {
        "id": transaction_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "date": transaction_date.isoformat(),
        "type": transaction_type,
        "parent_id": parent_id,
        "parent_name": st.session_state.parent_items[parent_id]["name"],
        "asin": asin,
        "quantity": quantity,
        "weight": weight,
        "notes": notes
    }
    
    # Add batch information if provided
    if batch_id:
        transaction["batch_id"] = batch_id
    
    st.session_state.transactions.append(transaction)
    save_data()
    return transaction_id

def main():
    st.title("Stock Tracker - Mithila Foods")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Stock Inward", "Packing Operations", "Sales Management", "Products Management"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Stock Inward":
        show_stock_inward()
    elif page == "Packing Operations":
        show_packing_operations()
    elif page == "Sales Management":
        show_sales_management()
    elif page == "Products Management":
        show_products_management()

def show_dashboard():
    """Display main dashboard"""
    st.header("📊 Stock Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    total_loose = sum(stock.get("loose_stock", 0) for stock in st.session_state.stock_data.values())
    total_packed_items = sum(sum(stock.get("packed_stock", {}).values()) for stock in st.session_state.stock_data.values())
    total_products = len(st.session_state.parent_items)
    total_value = calculate_stock_value(st.session_state.stock_data, st.session_state.parent_items, st.session_state.packet_variations)
    
    with col1:
        st.metric("Total Loose Stock", f"{total_loose:.1f} kg")
    with col2:
        st.metric("Total Packed Items", total_packed_items)
    with col3:
        st.metric("Product Categories", total_products)
    with col4:
        st.metric("Stock Value", format_currency(total_value))
    
    # Recent transactions
    st.subheader("📋 Recent Transactions")
    if st.session_state.transactions:
        recent_transactions = st.session_state.transactions[-10:]  # Last 10 transactions
        
        for transaction in reversed(recent_transactions):
            with st.expander(f"{transaction['type']} - {transaction['parent_name']} ({transaction['date']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Product:** {transaction['parent_name']}")
                    if transaction.get('asin'):
                        st.write(f"**ASIN:** {transaction['asin']}")
                    st.write(f"**Date:** {transaction['date']}")
                with col2:
                    if transaction.get('weight'):
                        st.write(f"**Weight:** {transaction['weight']} kg")
                    if transaction.get('quantity'):
                        st.write(f"**Quantity:** {transaction['quantity']} units")
                    if transaction.get('notes'):
                        st.write(f"**Notes:** {transaction['notes']}")
    else:
        st.info("No transactions recorded yet.")
    
    # Current Stock Overview
    st.subheader("📦 Current Stock Overview")
    
    if st.session_state.stock_data:
        summary = get_product_summary(st.session_state.stock_data, st.session_state.parent_items, st.session_state.packet_variations)
        
        if summary:
            df_stock = pd.DataFrame(summary)
            df_stock = df_stock[['product_name', 'category', 'loose_stock', 'packed_units', 'packed_weight', 'total_weight']]
            df_stock.columns = ['Product', 'Category', 'Loose Stock (kg)', 'Packed Units', 'Packed Weight (kg)', 'Total Weight (kg)']
            
            st.dataframe(df_stock, use_container_width=True)
            
            # Low stock alerts
            alerts = get_low_stock_alerts(st.session_state.stock_data, st.session_state.parent_items, st.session_state.packet_variations)
            if alerts:
                st.subheader("⚠️ Low Stock Alerts")
                for alert in alerts:
                    st.warning(f"**{alert['type']}:** {alert['product']} - Current: {alert['current_stock']} {alert['unit']}")
    else:
        st.info("No stock data available.")

def show_stock_inward():
    """Stock inward entry"""
    st.header("📥 Stock Inward")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Add New Stock")
        
        with st.form("stock_inward_form"):
            parent_id = st.selectbox(
                "Select Product",
                options=list(st.session_state.parent_items.keys()),
                format_func=lambda x: st.session_state.parent_items[x]["name"]
            )
            
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, format="%.2f")
            notes = st.text_area("Notes (optional)")
            
            submitted = st.form_submit_button("Add Stock")
            
            if submitted and weight > 0:
                if parent_id not in st.session_state.stock_data:
                    st.session_state.stock_data[parent_id] = {"loose_stock": 0, "packed_stock": {}}
                
                st.session_state.stock_data[parent_id]["loose_stock"] += weight
                st.session_state.stock_data[parent_id]["last_updated"] = datetime.datetime.now().isoformat()
                
                transaction_id = record_transaction("Stock Inward", parent_id, weight=weight, notes=notes)
                
                st.success(f"✅ Added {weight} kg of {st.session_state.parent_items[parent_id]['name']} to stock!")
                st.rerun()
    
    with col2:
        st.subheader("Current Loose Stock")
        if st.session_state.stock_data:
            loose_stock_data = []
            for parent_id, stock in st.session_state.stock_data.items():
                loose_stock_data.append({
                    "Product": st.session_state.parent_items[parent_id]["name"],
                    "Stock (kg)": stock.get("loose_stock", 0)
                })
            
            df_loose = pd.DataFrame(loose_stock_data)
            st.dataframe(df_loose, use_container_width=True)

def show_packing_operations():
    """Packing operations"""
    st.header("📦 Packing Operations")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Pack Products")
        
        parent_id = st.selectbox(
            "Select Product to Pack",
            options=list(st.session_state.parent_items.keys()),
            format_func=lambda x: st.session_state.parent_items[x]["name"]
        )
        
        if parent_id and parent_id in st.session_state.packet_variations:
            def format_packet_option(asin_key):
                details = st.session_state.packet_variations[parent_id][asin_key]
                weight = details.get('weight', 1.0)
                description = details.get('description', '')
                
                if not description or str(description).lower() in ['nan', 'null', 'none', '']:
                    parent_name = st.session_state.parent_items[parent_id]["name"]
                    description = f"{weight}kg {parent_name}"
                
                return f"{description} ({weight}kg)"
            
            asin = st.selectbox(
                "Select Packet Size",
                options=list(st.session_state.packet_variations[parent_id].keys()),
                format_func=format_packet_option
            )
            
            if asin:
                packet_weight = st.session_state.packet_variations[parent_id][asin]["weight"]
                available_loose = st.session_state.stock_data.get(parent_id, {}).get("loose_stock", 0)
                max_packets = int(available_loose / packet_weight) if packet_weight > 0 else 0
                
                st.info(f"Available loose stock: {available_loose} kg")
                st.info(f"Each packet: {packet_weight} kg")
                st.info(f"Maximum packets possible: {max_packets}")
                
                with st.form("packing_form"):
                    packets_to_pack = st.number_input(
                        "Number of packets to pack",
                        min_value=0,
                        max_value=max_packets,
                        step=1
                    )
                    
                    notes = st.text_area("Notes (optional)")
                    
                    submitted = st.form_submit_button("Pack Products")
                    
                    if submitted and packets_to_pack > 0:
                        total_weight_used = packets_to_pack * packet_weight
                        
                        st.session_state.stock_data[parent_id]["loose_stock"] -= total_weight_used
                        
                        if asin not in st.session_state.stock_data[parent_id]["packed_stock"]:
                            st.session_state.stock_data[parent_id]["packed_stock"][asin] = 0
                        st.session_state.stock_data[parent_id]["packed_stock"][asin] += packets_to_pack
                        
                        st.session_state.stock_data[parent_id]["last_updated"] = datetime.datetime.now().isoformat()
                        
                        transaction_id = record_transaction("Packing", parent_id, asin, packets_to_pack, total_weight_used, notes)
                        
                        st.success(f"✅ Packed {packets_to_pack} packets successfully!")
                        st.rerun()
        else:
            st.warning("No packet variations defined for this product.")
    
    with col2:
        st.subheader("Packed Stock Summary")
        if st.session_state.stock_data:
            packed_summary = []
            for parent_id, stock in st.session_state.stock_data.items():
                for asin, units in stock.get("packed_stock", {}).items():
                    if units > 0 and asin in st.session_state.packet_variations.get(parent_id, {}):
                        packed_summary.append({
                            "Product": st.session_state.parent_items[parent_id]["name"],
                            "ASIN": asin,
                            "Description": st.session_state.packet_variations[parent_id][asin]["description"],
                            "Units": units,
                            "Weight per Unit": st.session_state.packet_variations[parent_id][asin]["weight"],
                            "Total Weight": units * st.session_state.packet_variations[parent_id][asin]["weight"]
                        })
            
            if packed_summary:
                df_packed = pd.DataFrame(packed_summary)
                st.dataframe(df_packed, use_container_width=True)
            else:
                st.info("No packed stock available.")

def show_sales_management():
    """Sales management"""
    st.header("🛒 Sales Management")
    
    tab1, tab2 = st.tabs(["📝 Manual Sale", "📊 Sales Analytics"])
    
    with tab1:
        st.subheader("Record Sale")
        
        parent_id = st.selectbox(
            "Select Product",
            options=list(st.session_state.parent_items.keys()),
            format_func=lambda x: st.session_state.parent_items[x]["name"]
        )
        
        if parent_id and parent_id in st.session_state.packet_variations:
            def format_product_option(asin_key):
                details = st.session_state.packet_variations[parent_id][asin_key]
                weight = details.get('weight', 1.0)
                description = details.get('description', '')
                
                if not description or str(description).lower() in ['nan', 'null', 'none', '']:
                    parent_name = st.session_state.parent_items[parent_id]["name"]
                    description = f"{weight}kg {parent_name}"
                
                return f"{description} ({weight}kg)"
            
            asin = st.selectbox(
                "Select Product Variation",
                options=list(st.session_state.packet_variations[parent_id].keys()),
                format_func=format_product_option
            )
            
            if asin:
                available_units = st.session_state.stock_data.get(parent_id, {}).get("packed_stock", {}).get(asin, 0)
                
                with st.form("sales_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        quantity_sold = st.number_input(
                            "Units Sold",
                            min_value=1,
                            max_value=available_units if available_units > 0 else 1,
                            step=1
                        )
                        
                        sale_type = st.selectbox(
                            "Sale Type",
                            ["FBA Sale", "Easy Ship Sale", "Direct Sale"]
                        )
                    
                    with col2:
                        sale_date = st.date_input("Sale Date", value=datetime.date.today())
                        order_id = st.text_input("Order ID (Optional)")
                    
                    notes = st.text_area("Notes (Optional)")
                    
                    submitted = st.form_submit_button("Record Sale")
                    
                    if submitted:
                        if available_units >= quantity_sold:
                            # Update stock
                            st.session_state.stock_data[parent_id]["packed_stock"][asin] -= quantity_sold
                            st.session_state.stock_data[parent_id]["last_updated"] = datetime.datetime.now().isoformat()
                            
                            # Record transaction
                            weight_sold = quantity_sold * st.session_state.packet_variations[parent_id][asin]["weight"]
                            transaction_notes = f"{sale_type}"
                            if order_id:
                                transaction_notes += f" | Order: {order_id}"
                            if notes:
                                transaction_notes += f" | {notes}"
                            
                            transaction_id = record_transaction(
                                transaction_type=sale_type,
                                parent_id=parent_id,
                                asin=asin,
                                quantity=quantity_sold,
                                weight=weight_sold,
                                notes=transaction_notes,
                                transaction_date=sale_date
                            )
                            
                            st.success(f"✅ Sale recorded successfully! {quantity_sold} units of {format_product_option(asin)}")
                            st.rerun()
                        else:
                            st.error(f"❌ Insufficient stock! Available: {available_units}, Requested: {quantity_sold}")
            else:
                st.info("Please select a product variation to continue")
        else:
            st.warning("No product variations available for this product.")
    
    with tab2:
        st.subheader("Sales Analytics")
        
        if st.session_state.transactions:
            # Filter sales transactions
            sales_transactions = [t for t in st.session_state.transactions if "Sale" in t.get("type", "")]
            
            if sales_transactions:
                # Sales by date
                sales_df = pd.DataFrame(sales_transactions)
                sales_df['date'] = pd.to_datetime(sales_df['date'])
                
                # Daily sales chart
                daily_sales = sales_df.groupby('date').agg({
                    'quantity': 'sum',
                    'weight': 'sum'
                }).reset_index()
                
                fig = px.bar(daily_sales, x='date', y='quantity', title='Daily Sales (Units)')
                st.plotly_chart(fig, use_container_width=True)
                
                # Sales by product
                product_sales = sales_df.groupby('parent_name').agg({
                    'quantity': 'sum',
                    'weight': 'sum'
                }).reset_index()
                
                fig2 = px.pie(product_sales, values='quantity', names='parent_name', title='Sales by Product')
                st.plotly_chart(fig2, use_container_width=True)
                
                # Recent sales table
                st.subheader("Recent Sales")
                recent_sales = sales_df.tail(10)[['date', 'type', 'parent_name', 'quantity', 'weight', 'notes']]
                st.dataframe(recent_sales, use_container_width=True)
            else:
                st.info("No sales transactions recorded yet.")
        else:
            st.info("No transactions recorded yet.")

def show_products_management():
    """Products management"""
    st.header("🏷️ Products Management")
    
    tab1, tab2 = st.tabs(["📦 View Products", "➕ Add Product"])
    
    with tab1:
        st.subheader("Current Products")
        
        for parent_id, parent_info in st.session_state.parent_items.items():
            with st.expander(f"{parent_info['name']} ({parent_info.get('category', 'General')})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Product ID:** {parent_id}")
                    st.write(f"**Name:** {parent_info['name']}")
                    st.write(f"**Category:** {parent_info.get('category', 'General')}")
                    st.write(f"**Unit:** {parent_info.get('unit', 'kg')}")
                
                with col2:
                    # Show variations
                    if parent_id in st.session_state.packet_variations:
                        st.write("**Variations:**")
                        for asin, variation in st.session_state.packet_variations[parent_id].items():
                            st.write(f"• {asin}: {variation.get('description', 'No description')} ({variation.get('weight', 0)}kg) - ₹{variation.get('mrp', 0)}")
                    else:
                        st.write("**No variations defined**")
    
    with tab2:
        st.subheader("Add New Product")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("Product Name")
                category = st.selectbox("Category", PRODUCT_CATEGORIES)
                unit = st.selectbox("Unit", UNITS)
            
            with col2:
                # Variation details
                st.write("**First Variation:**")
                asin = st.text_input("ASIN")
                weight = st.number_input("Weight per packet", min_value=0.1, step=0.1)
                mrp = st.number_input("MRP", min_value=0.0, step=1.0)
            
            description = st.text_area("Product Description")
            
            submitted = st.form_submit_button("Add Product")
            
            if submitted and product_name and asin:
                # Generate product ID
                product_id = product_name.upper().replace(" ", "_")
                
                # Add parent item
                st.session_state.parent_items[product_id] = {
                    "name": product_name,
                    "category": category,
                    "unit": unit
                }
                
                # Add variation
                if product_id not in st.session_state.packet_variations:
                    st.session_state.packet_variations[product_id] = {}
                
                st.session_state.packet_variations[product_id][asin] = {
                    "weight": weight,
                    "asin": asin,
                    "description": description or f"{weight}kg {product_name}",
                    "mrp": mrp
                }
                
                # Initialize stock data
                st.session_state.stock_data[product_id] = {
                    "loose_stock": 0,
                    "packed_stock": {asin: 0},
                    "opening_stock": 0,
                    "last_updated": datetime.datetime.now().isoformat()
                }
                
                save_data()
                st.success(f"✅ Product '{product_name}' added successfully!")
                st.rerun()

if __name__ == "__main__":
    main()
