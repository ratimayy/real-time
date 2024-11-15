import pandas as pd
import streamlit as st
from pinotdb import connect
import plotly.express as px
import time

# Function to fetch data from Pinot
@st.cache_data(ttl=5)  # Cache data for 5 seconds for near real-time updates
def fetch_data(query):
    conn = connect(host='13.212.192.212', port=8099, path='/query/sql', scheme='http')
    cursor = conn.cursor()
    cursor.execute(query)
    return pd.DataFrame(cursor, columns=[col[0] for col in cursor.description])

# Streamlit App Title
st.title("Interactive Dashboard with Real-Time Updates")

# Sidebar for Navigation
st.sidebar.title("Navigation")
plot_type = st.sidebar.selectbox("Choose a Visualization", [
    "Inventory by Category",
    "Price by Brand",
    "Discount Distribution",
    "Production Cost by Material",
    "Most Recent Page Views"
])

# Auto-Refresh Option
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 5)

# Placeholder for Real-Time Updates
placeholder = st.empty()
counter = 0  # Initialize a counter for unique keys

# Infinite Loop for Real-Time Updates
while True:
    with placeholder.container():
        unique_key = f"plot{counter}"  # Create a unique key for each iteration

        # 1. Inventory by Category
        if plot_type == "Inventory by Category":
            query1 = """
            SELECT category, SUM(inventory_count) AS total_inventory
            FROM topic3new
            GROUP BY category
            ORDER BY total_inventory DESC;
            """
            data1 = fetch_data(query1)
            st.subheader("Inventory by Category")
            fig1 = px.bar(data1, x='category', y='total_inventory', color='category', 
                          title="Inventory by Category",
                          color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig1, key=f"{unique_key}_1")

        # 2. Price by Brand
        elif plot_type == "Price by Brand":
            query2 = """
            SELECT brand, AVG(price) AS avg_price
            FROM topic3new
            GROUP BY brand
            ORDER BY avg_price DESC;
            """
            data2 = fetch_data(query2)
            st.subheader("Price by Brand")
            fig2 = px.line(data2, x='brand', y='avg_price', title="Average Price by Brand",
                           markers=True, color_discrete_sequence=['orange'])
            st.plotly_chart(fig2, key=f"{unique_key}_2")

        # 3. Discount Distribution
        elif plot_type == "Discount Distribution":
            query3 = """
            SELECT discount, COUNT(*) AS discount_count
            FROM topic3new
            GROUP BY discount
            ORDER BY discount DESC;
            """
            data3 = fetch_data(query3)
            st.subheader("Discount Distribution")
            fig3 = px.scatter(data3, x='discount', y='discount_count', size='discount_count', color='discount',
                              title="Discount Distribution", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig3, key=f"{unique_key}_3")

        # 4. Production Cost by Material
        elif plot_type == "Production Cost by Material":
            query4 = """
            SELECT material, AVG(production_cost) AS avg_cost
            FROM topic3new
            GROUP BY material
            ORDER BY avg_cost DESC;
            """
            data4 = fetch_data(query4)
            st.subheader("Production Cost by Material")
            fig4 = px.bar(data4, x='avg_cost', y='material', orientation='h', color='material',
                          title="Production Cost by Material", color_discrete_sequence=px.colors.sequential.Blues)
            st.plotly_chart(fig4, key=f"{unique_key}_4")

        # 5. Most Recent Page Views
        elif plot_type == "Most Recent Page Views":
            query6 = """
            SELECT pageid, userid, viewtime
            FROM topic1
            ORDER BY viewtime DESC
            LIMIT 10;
            """
            data6 = fetch_data(query6)
            st.subheader("Most Recent Page Views")
            fig6 = px.scatter(data6, x='viewtime', y='pageid', color='userid', 
                              title="Most Recent Page Views", 
                              labels={'viewtime': 'View Time', 'pageid': 'Page ID', 'userid': 'User ID'},
                              color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig6, key=f"{unique_key}_6")  # Use the unique key

        # Refresh Interval
        time.sleep(refresh_interval)
        counter += 1  # Increment the counter to ensure the key is unique for each refresh
