from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import unicodecsv as csv
import random
import time
import os

class Connection:

	def __init__(self, cse_url):
		self.driver = webdriver.Firefox()
		self.driver.set_window_size(640, 640)
		self.driver.get(cse_url)
		
		if 'Google' in self.driver.title:
			print 'Succesfully initiated driver.'
		else:
			raise 'Error initiating browser. Quitting.'
			sys.exit()

		for i in self.driver.find_elements_by_tag_name('input'):
			if i.get_attribute('class') == 'gsc-input':
				self.query_box = i

		for button in self.driver.find_elements_by_tag_name('button'):
			if button.get_attribute('class') == 'gsc-search-button gsc-search-button-v2':
				self.submit_button = button

	def close_overlay(self):
		WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'gsc-results-close-btn-visible')))
		self.driver.find_element_by_class_name('gsc-results-close-btn').click()

	def scrape(self):
		
		try:
			self.driver.find_element_by_class_name('gs-spelling')
			auto_correct = True
		except NoSuchElementException:
			auto_correct = False

		soup = BeautifulSoup(self.driver.page_source, 'html.parser')
	
		if soup.find('div', {'class' : 'gsc-webResult gsc-result'}):
			for result in soup.findAll('div', {'class' : 'gsc-webResult gsc-result'}):
				urls = [title.a['href'] for title in result.find('div', {'class':'gs-title'})]

		return {	'urls': urls,
					'results' : len(urls),
					'autocorrect' : autocorrect,
					'troll_handle' : ''
				}

if __name__ == '__main__':
	with open('updated_handles.csv') as csv_in:
		reader = csv.reader(csv_in)
		data = [line for line in reader]

	cse_urls = {	'https://cse.google.com/cse/publicurl?cx=006674705950714944870:oubvsfffxwo' : False,
					'https://cse.google.com/cse/publicurl?cx=006674705950714944870:ejjevixkyr4' : False,
					'https://cse.google.com/cse/publicurl?cx=006674705950714944870:pksdgtyzbtg' : False
				}

	current_cse = random.choice([cse_url for cse_url in cse_urls if cse_urls[cse_url] != True])
	cse_urls[current_cse] = True

	con = Connection(current_cse)

	for troll_handle in data:
		t0 = time.time()

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

		# input in CSE and push query
		print 'Looking for <%s>' % troll_handle
		con.query_box.send_keys('"%s"' % troll_handle[0])
		con.query_box.send_keys(Keys.RETURN)

		# check to see if overlay pops up
		try:
			WebDriverWait(con.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'gsc-results-wrapper-visible')))
		except TimeoutException:
			# No results visible, change CSE
			cse_urls[current_cse] = False
			new_cse = random.choice([cse for cse in cse_urls.keys() if cse_urls[cse] != True])
			cse_urls[new_cse] = True
			print '\t[i] Starting up new CSE: <%s>' % new_cse
			con = Connection(new_cse)
			continue

		# scrape
		data_out = con.scrape()
		data_out['troll_handle'] = troll_handle[0]
		out['Trolls'].append(data_out)
		json.dump(out, open('troll.json', 'w'), sort_keys=True, indent=4)

		# close overlay
		con.close_overlay()
		con.query_box.clear()

		# sleep to prevent rate limit
		time.sleep((time.time() - t0) * 10)