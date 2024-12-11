import json
import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Send a request to the website
url = 'https://roadmap.sh'
response = requests.get(url)

# Parse the HTML content
tree = html.fromstring(response.content)
# Use XPath to extract the element
EntityElement = tree.xpath('/html/body/div[2]/div[2]/div/ul')  # First element in the list

# Stock the data in a dictionary
data = {}
for index in range(1, 22):
    # Extract the span text (Entity)
    li = EntityElement[0].xpath(f'./li[{index}]')
    span = li[0].xpath('./a/span[1]/text()') if li else None
    # Extract the href (url)
    a = li[0].xpath('./a') if li else None
    if span and a:
        data[index] = {"entity": span[0].strip(), "url": url + a[0].attrib.get('href')}


# Set up Selenium WebDriver with headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
try:
    topics_data = []
    # for key, value in data.items():
    for key, value in list(data.items()):
        # Navigate to the URL
        topics_data = []  # Reset topics_data for each entity
        driver.get(value['url'])

        # Wait for the page to load
        time.sleep(5)  # Adjust time as needed

        # Parse the page source
        pdf_tree = html.fromstring(driver.page_source)

        # Use XPath to select all <g> elements with data-type="topic"
        topic_elements = pdf_tree.xpath('//*[@id="resource-svg-wrap"]/svg/g[@data-type="topic"]')

        # Extract topics and their subtopics
        for topic_element in topic_elements:
            topic_data = {
                "data-title": topic_element.get("data-title"),
                "subtopic": []  # Initialize subtopics list
            }
            topic_node_id = topic_element.get("data-node-id")
            # Find subtopic elements that have data-parent-id equal to this topic's data-node-id
            subtopic_elements = pdf_tree.xpath(
                f'//*[@id="resource-svg-wrap"]/svg/g[@data-type="subtopic" and @data-parent-id="{topic_node_id}"]')

            # Extract subtopic titles
            subtopic_titles = [subtopic.get("data-title") for subtopic in subtopic_elements]
            topic_data["subtopic"] = subtopic_titles

            topics_data.append(topic_data)

        # Store the topics data in the data dictionary
        data[key]['topics'] = topics_data

    # Save extracted data to a JSON file
    with open("topics_data.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print("Data has been saved to 'topics_data.json'.")

finally:
    # Close the browser
    driver.quit()