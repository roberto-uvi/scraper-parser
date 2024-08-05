from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

gecko_driver_path = r"C:\Users\roberto.renteria\OneDrive - Unique Travel Vacation\Desktop\py8\webdriver\geckodriver.exe"

firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")  # for headless mode

service = FirefoxService(executable_path=gecko_driver_path)
driver = webdriver.Firefox(service=service, options=firefox_options)

driver.get("https://www.sandals.com")
print(driver.title)  # Example usage

driver.quit()  # Don't forget to close the driver