import streamlit as st
import pandas as pd
from engine import InventoryManager
from vision import VisionProcessor
import os
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="The Big Game | Supply Chain Intelligence",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0f1116;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1e2128;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #3e4451;
    }
    .critical-card {
        background-color: #ff4b4b22;
        border: 1px solid #ff4b4b;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Logic
if 'engine' not in st.session_state:
    st.session_state.engine = InventoryManager()

# Sidebar Setup
with st.sidebar:
    st.title("⚙️ Control Center")
    api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio API Key")
    
    st.divider()
    panic_factor = st.slider(
        "Panic Factor (Demand Multiplier)", 
        min_value=1.0, max_value=5.0, value=1.0, step=0.5,
        help="Increase this during festivals or high-demand periods to adjust predictions."
    )
    
    if st.button("Reset Inventory Data"):
        if os.path.exists('inventory.csv'):
            os.remove('inventory.csv')
            st.session_state.engine = InventoryManager()
            st.rerun()

# Main Dashboard
st.title("🏆 The Big Game")
st.subheader("AI-Driven Supply Chain Intelligence for India")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📸 Upload Bill")
    uploaded_file = st.file_uploader("Take a photo or upload a bill image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Bill", use_column_width=True)
        
        if st.button("🚀 Extract & Update Stock"):
            if not api_key:
                st.error("Please provide a Gemini API Key in the sidebar.")
            else:
                with st.spinner("Gemini is analyzing the bill..."):
                    # Save temp file
                    temp_path = "temp_bill.jpg"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    try:
                        processor = VisionProcessor(api_key)
                        items = processor.extract_bill_data(temp_path)
                        
                        if items:
                            st.session_state.engine.add_or_update_stock(items)
                            st.success(f"Successfully added {len(items)} items to inventory!")
                            st.balloons()
                        else:
                            st.warning("No items could be extracted. Please ensure the bill is clear.")
                    except Exception as e:
                        st.error(f"Processing failed: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

with col2:
    st.header("📊 Real-time Inventory & Predictions")
    
    # Calculate predictions based on panic factor
    inventory_df = st.session_state.engine.calculate_predictions(panic_factor)
    
    if inventory_df.empty:
        st.info("No inventory data yet. Upload a bill to get started!")
    else:
        # Prediction Radar Highlights
        critical_items = inventory_df[inventory_df['Status'] == 'CRITICAL']
        
        if not critical_items.empty:
            st.warning(f"🚨 ALERT: {len(critical_items)} products are running low!")
            for _, row in critical_items.iterrows():
                st.markdown(f"""
                <div class="critical-card">
                    <strong>{row['Product Name']}</strong>: Expected to run out in <b>{row['Days of Stock Left']} days</b>.
                </div>
                """, unsafe_allow_html=True)
        
        # Display Table
        st.dataframe(
            inventory_df.style.apply(lambda x: ['background-color: #ff4b4b22' if x.Status == 'CRITICAL' else '' for _ in x], axis=1),
            use_container_width=True
        )

# Metrics Footer
if not inventory_df.empty:
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total SKU Count", len(inventory_df))
    m2.metric("Critical Alerts", len(critical_items))
    m3.metric("Avg DSL", f"{inventory_df['Days of Stock Left'].mean():.1f} Days")
