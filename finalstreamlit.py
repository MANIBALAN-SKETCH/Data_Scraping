import pandas as pd
import mysql.connector
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import time

# Load data for each state
def load_state_data(filename):
    df = pd.read_csv(filename)
    return df["Route_name"].tolist()

lists_k = load_state_data("df_k.csv")
lists_A = load_state_data("df_A.csv")
lists_T = load_state_data("df_T.csv")
lists_g = load_state_data("df_G.csv")
lists_R = load_state_data("df_R.csv")
lists_SB = load_state_data("df_SB.csv")
lists_H = load_state_data("df_H.csv")
lists_AS = load_state_data("df_AS.csv")
lists_UP = load_state_data("df_UP.csv")
lists_WB = load_state_data("df_WB.csv")

# Page config
st.set_page_config(layout="wide", page_title="BMB - Bus Route Explorer", page_icon="🚌")

# Custom CSS for modern look
st.markdown("""
    <style>
    .main {
        background-color: #041538;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: black;
        border-radius: 5px;
    }
    .stSelectbox {
        background-color: black;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.image("guvit.png", width=200)
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "States and Routes"],
        icons=["house", "geo-alt"],
        menu_icon="cast",
        default_index=0,
    )

# Home page
if selected == "Home":
    st.title("🚌 Redbus Data Explorer")
    st.subheader("Transforming Bus Travel Data with Streamlit")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎯 Objective")
        st.info("To revolutionize the transportation industry by providing comprehensive bus travel data analysis and visualization.")

    with col2:
        st.markdown("### 🛠️ Tools Used")
        st.success("• Selenium\n• Python\n• MySQL\n• Streamlit")

    st.markdown("### 📊 Project Overview")
    st.markdown("""
    This application leverages cutting-edge technologies to scrape, process, and visualize bus travel data:
    - **Selenium** for automated web scraping from Redbus
    - **Pandas** for efficient data manipulation and preprocessing
    - **MySQL** for robust data storage and retrieval
    - **Streamlit** for creating this interactive web application
    """)

    st.markdown("### 👨‍💻 Developer")
    st.info("Developed by: Manibalan")

# States and Routes page
elif selected == "States and Routes":
    st.title("🌍 States and Routes Explorer")

    col1, col2 = st.columns(2)
    with col1:
        S = st.selectbox("Select a State", ["Kerala", "Andhra Pradesh", "Telangana", "Goa", "Rajasthan", 
                                            "South Bengal", "Haryana", "Assam", "Uttar Pradesh", "West Bengal"])
    
    with col2:
        TIME = st.time_input("Select departure time")

    col3, col4 = st.columns(2)
    with col3:
        select_type = st.radio("Choose bus type", ("sleeper", "semi-sleeper", "others"))
    with col4:
        select_fare = st.radio("Choose bus fare range", ("50-1000", "1000-2000", "2000 and above"))

    # Function to get route options based on selected state
    def get_route_options(state):
        state_list_map = {
            "Kerala": lists_k,
            "Andhra Pradesh": lists_A,
            "Telangana": lists_T,
            "Goa": lists_g,
            "Rajasthan": lists_R,
            "South Bengal": lists_SB,
            "Haryana": lists_H,
            "Assam": lists_AS,
            "Uttar Pradesh": lists_UP,
            "West Bengal": lists_WB
        }
        return state_list_map.get(state, [])

    route = st.selectbox("Select a route", get_route_options(S))

    def query_database(state, route, bus_type, fare_range, time):
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="RED_BUS_DETAILS")
        cursor = conn.cursor()

        if fare_range == "50-1000":
            fare_min, fare_max = 50, 1000
        elif fare_range == "1000-2000":
            fare_min, fare_max = 1000, 2000
        else:
            fare_min, fare_max = 2000, 100000

        if bus_type == "sleeper":
            bus_type_condition = "Bus_type LIKE '%Sleeper%'"
        elif bus_type == "semi-sleeper":
            bus_type_condition = "Bus_type LIKE '%A/c Semi Sleeper %'"
        else:
            bus_type_condition = "Bus_type NOT LIKE '%Sleeper%' AND Bus_type NOT LIKE '%Semi-Sleeper%'"

        query = f"""
            SELECT * FROM bus_details 
            WHERE Price BETWEEN {fare_min} AND {fare_max}
            AND Route_name = %s
            AND {bus_type_condition} AND Start_time >= %s
            ORDER BY Price, Start_time DESC
        """
        cursor.execute(query, (route, time))
        results = cursor.fetchall()
        conn.close()

        return pd.DataFrame(results, columns=[
            "ID", "Bus_name", "Bus_type", "Start_time", "End_time", "Total_duration",
            "Price", "Seats_Available", "Ratings", "Route_link", "Route_name"
        ])

    if st.button("Search Buses"):
        with st.spinner('Searching for buses...'):
            df_result = query_database(S, route, select_type, select_fare, TIME)

        if df_result.empty:
            st.warning("No buses found matching your criteria.")
        else:
            st.subheader("Available Buses")
            st.dataframe(df_result, use_container_width=True)

            # Visualizations
            fig = px.scatter(df_result, x="Start_time", y="Price", color="Bus_type", 
                             hover_data=["Bus_name", "Seats_Available"],
                             title="Bus Prices vs. Departure Time")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.histogram(df_result, x="Price", nbins=20,
                                title="Price Distribution")
            st.plotly_chart(fig2, use_container_width=True)

            # Additional statistics
            st.subheader("Route Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Average Price", f"₹{df_result['Price'].mean():.2f}")
            col2.metric("Lowest Price", f"₹{df_result['Price'].min()}")
            col3.metric("Highest Price", f"₹{df_result['Price'].max()}")

# Footer
st.markdown("---")
st.markdown("© 2024 BMB - Bus Route Explorer. All rights reserved.")