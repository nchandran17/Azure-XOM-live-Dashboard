# Azure-XOM-live-Dashboard
Uses finnhub api, postgreSQL and python to create a live webapp on Azure


**Go To Web App Below**:
[XOM dashboard](https://xom-tracker-eygqhnheeqhvbsa8.canadacentral-01.azurewebsites.net)



Project Process:
I started this project locally before moving it to Azure, which is why I use streamlit instead of a power bi dashboard. 
I used the free finnhub api to get data in json form into stock_streaming.py and use python to 'clean' the data and put it in the postgreSQL
database. Within the database, created views and stored procedures to either analyze the data(view) or change the data(stored procedure).
In Azure, the project works by having the stock_streaming.py in a webjob. It sends the information to an Azure SQL database for postgreSQL server and puts it in a table. The database already has views and stored procedures, so dashboard.py doesn't need to have complicated SQL logic written in it. Dashboard.py does the magic of 
displaying the changing data in real time. To change to the candlestick table, we cache a resource so it only runs once and use a streamlit fragment decorator to ensure the dashboard is updated every two seconds without forcing the entire page to reload.
