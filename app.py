import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import os

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

def main():
    st.title("Stock Tracker - Mithila Foods")
    st.write("A simple stock tracking application for Mithila Foods")
    
    # Basic dashboard
    if st.session_state.stock_data:
        st.subheader("Stock Overview")
        
        for parent_id, stock in st.session_state.stock_data.items():
            product_name = st.session_state.parent_items[parent_id]["name"]
            loose_stock = stock.get("loose_stock", 0)
            
            st.write(f"**{product_name}:** {loose_stock} kg loose stock")
            
            # Show packed stock
            packed_stock = stock.get("packed_stock", {})
            for asin, units in packed_stock.items():
                if units > 0:
                    weight = st.session_state.packet_variations[parent_id][asin]["weight"]
                    description = st.session_state.packet_variations[parent_id][asin]["description"]
                    st.write(f"  - {description}: {units} units ({weight}kg each)")

if __name__ == "__main__":
    main()
                            
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
