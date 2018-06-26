from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import unicodecsv as csv
import random
import time
import json
import sys
import os

def scrape(html):
	soup = BeautifulSoup(html, 'html.parser')
	results = soup.findAll('div', {'class' : 'gsc-webResult gsc-result'})

	print '\tFound %i results' % len(results)
	
	urls = []

	if results:
		for result in results:
			title = result.find('div', {'class':'gs-title'})
			if title:
				urls.append(title.a['href'])

	return urls

cse_urls = {	'https://cse.google.com/cse/publicurl?cx=006674705950714944870:oubvsfffxwo' : False,
				'https://cse.google.com/cse/publicurl?cx=006674705950714944870:ejjevixkyr4' : False,
				'https://cse.google.com/cse/publicurl?cx=006674705950714944870:pksdgtyzbtg' : False
			}


with open('updated_handles.csv') as csv_in:
	reader = csv.reader(csv_in)
	data = [line for line in reader]


def build_driver(cse_url):
	driver = webdriver.Firefox(executable_path='./geckodriver-win')
	driver.set_window_size(640, 640)
	driver.get(cse_url)

	if 'Google' in driver.title:
		print '[i] Succesfully initiated browser.'
	else:
		print '[!] Error initiating browser. Quitting.'
		sys.exit()

	inputs = driver.find_elements_by_tag_name('input')

	for i in inputs:
		if i.get_attribute('class') == 'gsc-input':
			query_box = i

	buttons = driver.find_elements_by_tag_name('button')

	for button in buttons:
		if button.get_attribute('class') == 'gsc-search-button gsc-search-button-v2':
			submit_button = button

	return driver, submit_button, query_box, cse_url

current_cse = random.choice(cse_urls.keys())
cse_urls[current_cse] = True
driver, submit_button, query_box, current_cse = build_driver(current_cse)
	
for troll_handle in data:
	if 'troll.json' in os.listdir('.'):
		with open('troll.json', 'r') as json_in:
			out = json.load(json_in)
		
		processed = [t['troll_handle'] for t in out['Trolls']]

		print '[i] processed %i trolls' % len(processed)
		if troll_handle[0] in processed:
			print '[i] Already processed <%s>' % troll_handle
			continue
	else:
		out = {'Trolls' : []}

	t0 = time.time()
	
	print '[i] Looking for <%s>.' % troll_handle[0]
	query_box.send_keys('"%s"' % troll_handle[0])
	query_box.send_keys(Keys.RETURN)
#	submit_button.click()
	
	# wait for overlay to be visible
	try:
		WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'gsc-results-wrapper-visible')))
	except TimeoutException:
		print '\t[!] Timed-out while waiting for form to be submitted...'
		
		# time-out: get other CSE
		driver.close()
		cse_urls[current_cse] = False
		new_cse = random.choice([cse for cse in cse_urls.keys() if cse_urls[cse] != True])
		cse_urls[new_cse] = True
		print '\t[i] Starting up new CSE: <%s>' % new_cse
		driver, submit_button, query_box, current_cse = build_driver(new_cse)
		query_box.clear()
		continue

	try:
		driver.find_element_by_class_name('gs-spelling')
		auto_correct = True
	except NoSuchElementException:
		auto_correct = False

	urls = scrape(driver.page_source)
	
	# wait untill button for exiting overlay become clickable
	WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'gsc-results-close-btn-visible')))
	driver.find_element_by_class_name('gsc-results-close-btn').click()
	
	dict_out = {	'troll_handle' : troll_handle[0],
					'autocorrect' : auto_correct,
					'hits' : len(urls),
					'urls' : urls
				}

	out['Trolls'].append(dict_out)
	with open('troll.json', 'w') as json_out:
		json.dump(out, json_out, sort_keys=True, indent=4)

	query_box.clear()
	time.sleep((time.time() - t0) * 5)

driver.close()
sys.exit()