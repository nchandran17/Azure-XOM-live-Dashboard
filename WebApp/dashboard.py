import streamlit as st
import pandas as pd
import time
import psycopg2
import threading
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file   ///this is now useless because i originally made this for a local setup then 
###migrated to azure and just doesnt do anything because we do not need to read from an .env file


st.set_page_config(page_title='XOM Real Time Tracker', layout='wide')
st.title('Exxon(XOM) Real Time Tracker')
st.write('This dashboard displays real-time stock data for Exxon (XOM) using data from the Finnhub API. The data is updated every 2 seconds, providing insights into the latest price and volume information for XOM.')

DB_HOST = os.getenv('DB_HOST')
DB_PASS = os.getenv('DB_PASSWORD')

page = st.sidebar.radio("Select Page", ['Dashboard', 'Candlestick Chart'])
st.sidebar.divider()

st.sidebar.header("System Status")
st.sidebar.success("Dashboard Active")

@st.cache_resource
def init_db_connection():
    return psycopg2.connect(
        dbname='postgres',
        user='pitt_admin',
        password=DB_PASS,
        host=DB_HOST,
        port='5432',
        sslmode='require'
    )

conn = init_db_connection()



@st.cache_resource
def background_data_fetch():
    def run_loop():
        archive_run_today = False
        while True:
            
            now = datetime.now()

            if now.hour == 20 and now.minute == 5:
                if not archive_run_today:
                    try:
                        special_conn = psycopg2.connect(
                        dbname='postgres',
                        user='pitt_admin',
                        password=DB_PASS,
                        host=DB_HOST,
                        port='5432',
                        sslmode='require'
                        )
                        
                        cur = special_conn.cursor()
                        cur.execute("CALL candlestick_add();")
                        special_conn.commit()
                        cur.close()
                        special_conn.close()
                        archive_run_today = True
                        print("Daily archive process executed.")
                    except Exception as e:
                        print(f"Error during daily archive process: {e}")
            
            if now.hour == 0 and now.minute == 0:
                archive_run_today = False
        

            time.sleep(30)

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()
    return thread

background_data_fetch()

            




def get_live_data():
    
    query = "SELECT ticker, price, volume, received_at FROM oil_stock_ticks ORDER BY received_at DESC LIMIT 100"
    df = pd.read_sql(query, conn)
    #conn.close()
    return df

def get_VWAP():
    
    query = "SELECT*FROM VWAP ORDER BY date_val DESC LIMIT 1"
    df = pd.read_sql(query, conn)
    #conn.close()
    return df

def get_whale_data():
    
    query = "SELECT*FROM whale_hunting WHERE received_at >= CURRENT_DATE ORDER BY received_at DESC"
    df = pd.read_sql(query, conn)
    #conn.close()
    return df

def get_candlestick_data():
    query = "SELECT high, low, open_val, close_val, date_val FROM candlestick_table ORDER BY date_val DESC LIMIT 30"
    df = pd.read_sql(query, conn)
    #conn.close()
    return df

placeholder = st.empty()

def check_conn(connection):
    """Checks if connection is dead and reopens if necessary"""

    try:
        # We 'ping' the DB with an empty execution to see if it's alive
        connection.cursor().execute('SELECT 1')
        return connection
    except:
        # If the 'ping' fails, we reconnect
        init_db_connection.clear()
        return init_db_connection()

if 'last_notified_whale_time' not in st.session_state:
    st.session_state.last_notified_whale_time = None

@st.fragment(run_every=2)
def live_dashboard():
    #if page == 'Dashboard':
    global conn
    conn = check_conn(conn)

    df = get_live_data()
    vwap = get_VWAP()
    whales_df = get_whale_data()
    #with placeholder.container():
    m1, m2, m3, m4 = st.columns(4)
    

    m1.metric("Latest Price", f"${df['price'].iloc[0]:.2f}")   
    m2.metric("Latest Volume", f"{df['volume'].iloc[0]:,}")
    m3.metric("Daily Whales", len(whales_df))
    m4.metric("VWAP", f"{vwap['vwap'].iloc[0]:.2f}")
    st.write("All Recent Trades")
    st.dataframe(df, use_container_width=True)
    st.divider()
    if not whales_df.empty:
        current_whale_time = whales_df['received_at'].iloc[0]
        if st.session_state.last_notified_whale_time is None or current_whale_time > st.session_state.last_notified_whale_time:
            st.toast(f"Whale Alert! A large trade of {whales_df['volume'].iloc[0]:,} shares was detected at {current_whale_time}.")
            st.session_state.last_notified_whale_time = current_whale_time

    st.subheader("Today's Whale Activity")
    if not whales_df.empty:
        st.dataframe(whales_df, use_container_width=True)
    else:
        st.write("No whale activity detected today so far")

    

if page == 'Dashboard':
    live_dashboard()
    #time.sleep(2)
    #st.rerun()


elif page == 'Candlestick Chart':
    st.subheader("📈 Historical 30-Day Trends")
    st.write("This view pulls from the 'Gold Layer' historical table, updated daily at 4:05 PM.")
    
    conn = check_conn(conn)
    chart_df = get_candlestick_data()
    
    if not chart_df.empty:
        import plotly.graph_objects as go
        
        # Sort by date ascending for the chart to look right (Left to Right)
        chart_df = chart_df.sort_values('date_val', ascending=True)

        fig = go.Figure(data=[go.Candlestick(
            x=chart_df['date_val'],
            open=chart_df['open_val'],
            high=chart_df['high'],
            low=chart_df['low'],
            close=chart_df['close_val'],
            increasing_line_color='#00ffcc', # Neon Green
            decreasing_line_color='#ff4b4b'  # Bright Red
        )])

        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=600,
            yaxis_title="Price (USD)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # Show the raw data below the chart
        st.write("### Historical Data Details")
        st.dataframe(chart_df.sort_values('date_val', ascending=False), hide_index=True)
    else:
        st.info("Waiting for the first daily candle to be archived...")


#conn.close()
        
    
