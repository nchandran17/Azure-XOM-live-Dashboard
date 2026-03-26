import websocket
import json
import psycopg2
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv('FINNHUB_KEY')
DB_HOST = os.getenv('DB_HOST')
DB_PASS = os.getenv('DB_PASSWORD')
#API_KEY = 'd6pk5fhr01qo88aji0r0d6pk5fhr01qo88aji0rg'


DB_stuff = {
    'dbname': 'postgres',
    'user': 'pitt_admin',
    'password': DB_PASS,
    'host': DB_HOST,
    'port': '5432',
    'sslmode': 'require'
}

#conn = psycopg2.connect(**DB_stuff)
#cur = conn.cursor()  

def on_open(ws):
    print("Connection opened.")    
    ws.send('{"type":"subscribe","symbol":"XOM"}')   ##subscribe allow us to see when something happens with our selected symbol


def on_message(ws, message):
    global conn
    conn = check_conn(conn)  # Ensure we have a valid connection before processing the message
    data = json.loads(message) #If we just did print(message), we would get gibberish, this helps us decode that
    
    if data['type'] == 'trade':
        cur = conn.cursor()
        for trade in data['data']:
            ticker = trade['s']
            price = trade['p']
            volume = trade['v']
            trade_time = trade['t']
            query = "INSERT INTO oil_stock_ticks (ticker, price, volume, trade_time) VALUES (%s, %s, %s, %s)"
            values = (ticker, price, volume, trade_time)
            cur.execute(query, values)
        print(f"Received data: {data}")

        conn.commit()
        
        print("Data inserted into the database.")
        cur.close()
    else:
        pass


def on_close(ws, close_status_code, close_msg):
    # 2. ONLY close when the script actually stops
    
    print("Database connection closed.")

def check_conn(connection):
    """Checks if connection is dead and reopens if necessary"""
    try:
        # We 'ping' the DB with an empty execution to see if it's alive
        connection.cursor().execute('SELECT 1')
        return connection
    except:
        # If the 'ping' fails, we reconnect
        return psycopg2.connect(**DB_stuff)

conn = None

if __name__ == "__main__":
    while True:
        conn = check_conn(conn)
        
        try:
            ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={API_KEY}",
                                        on_message=on_message,
                                        on_close=on_close)
            
            ws.on_open=on_open
            ws.run_forever()

        except Exception as e:
            print(f"Conn    ection error: {e}")
        time.sleep(5)


