from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

class FlightScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
    def search_flights(self, origin, destination, date):
        """
        Search for flights between two cities on a specific date
        """
        url = f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{date}"
        
        try:
            self.driver.get(url)
            time.sleep(5)  # Wait for dynamic content to load
            
            wait = WebDriverWait(self.driver, 10)
            flight_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[role='row']"))
            )
            
            flights = []
            for element in flight_elements:
                flight = {
                    'airline': element.find_element(By.CSS_SELECTOR, '.airline-name').text,
                    'departure': element.find_element(By.CSS_SELECTOR, '.departure-time').text,
                    'arrival': element.find_element(By.CSS_SELECTOR, '.arrival-time').text,
                    'price': element.find_element(By.CSS_SELECTOR, '.price').text,
                    'duration': element.find_element(By.CSS_SELECTOR, '.duration').text
                }
                flights.append(flight)
                
            return pd.DataFrame(flights)
            
        except Exception as e:
            print(f"Error searching flights: {str(e)}")
            return pd.DataFrame()
        
    def find_best_deals(self, origin, destination, start_date, end_date):
        """
        Find the best deals within a date range
        """
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        all_flights = []
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            flights = self.search_flights(origin, destination, date_str)
            if not flights.empty:
                flights['date'] = date_str
                all_flights.append(flights)
            current += timedelta(days=1)
            
        if all_flights:
            combined_flights = pd.concat(all_flights)
            return combined_flights.sort_values('price')
        return pd.DataFrame()
    
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()