URL = 'https://www.google.com/search?q=coleman+vision+abq&oq=coleman&aqs=chrome.0.69i59l3j46i67i199i275i291i433j69i60l2j69i61l2.3704j1j9&sourceid=chrome&ie=UTF-8#lrd=0x8722744a2cf14269:0x647508579888f998,1,,,'
TIMEFRAME = {'a week ago', 'day ago', 'days ago', 'weeks ago', 'month ago', 'months ago'}
DATE = datetime.datetime.now().strftime("%x")
DB_URL = 'http://127.0.0.1:5000/patients'

"""
    web scraper for cross checking patients in db with google reviews. 
"""
		
from selenium import webdriver
import time
import datetime
import random
from selenium.webdriver.common.keys import Keys
import json
import requests


# --------- EDIT BELOW -----------

URL = ''  # google reviews url
TIMEFRAME = {'a week ago', 'day ago', 'days ago', 'weeks ago', 'month ago', 'months ago'}
CHROMEDRIVER_PATH = ''

# ---------------------------


DATE = datetime.datetime.now().strftime("%x")
DB_URL = 'http://127.0.0.1:5000/patients'

res_json = requests.get(DB_URL).text
res = json.loads(res_json)
res_patients = res["patients"]

class ReviewBot:
	def __init__(self):
		self.reviews = []
		# navigate to goog reviews
		self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)
		self.driver.get(URL)
		time.sleep(5)
		#switch to most recent reviews
		self.driver.find_element_by_xpath('//*[@id="gsr"]/span/g-lightbox/div[2]/div[3]/span/div/div/div/div[1]/div[3]/div[2]/g-dropdown-menu').click()
		time.sleep(2)
		self.driver.find_element_by_xpath('//*[@id="lb"]/div/g-menu/g-menu-item[2]').click()


	def collectNewReviews(self):
		"""
			scrolls down n times, collects new reviews from timeframe within TIMEFRAME
		"""
		popup = self.driver.find_element_by_xpath('//*[@id="gsr"]/span/g-lightbox/div[2]/div[3]/span/div/div/div/div[2]')
		self.scroller(popup)
		# select all review elements:
		all_reviews = self.driver.find_elements_by_xpath('//*[@id="reviewSort"]/div/div[2]/div')
		for review in all_reviews:
			name = review.find_element_by_class_name('TSUbDb').find_element_by_css_selector('a').text
			stars_ = review.find_element_by_css_selector('g-review-stars').find_element_by_css_selector('span').get_attribute('aria-label')
			stars = stars_.split()[1]
			timeframe = review.find_element_by_class_name('PuaHbe').find_elements_by_css_selector('span')[2].text
			# make json ish element with them:
			# this will only take elements within the specified timeframe
			is_valid = False
			for t in TIMEFRAME:
				if t in timeframe:
					is_valid = True
			if is_valid:
				# find patient in database, change patient data 
				first_name, last_name = name.split()[0], name.split()[1]
				print(first_name + ' ' + last_name)
				name_variations = self.generateNames(first_name, last_name)
				db_name = self.findMatch(name_variations, res_patients)
				# print(db_name)
				if db_name != "":
					print("FOUND DB MATCH:" + db_name)
					# make post request to db to change patient data
					r = requests.put(DB_URL + '/' + db_name, json={'wrote_review' : True})
		self.driver.quit()
		return



	def calculateDate(self, timeframe):
		t = timeframe.split()[0]
		if t == 'a':
			t = 1
		else:
			t = int(t)
		date = DATE.split('/')
		date[0] = int(date[0])
		date[1] = int(date[1])
		date[2] = int(date[2])
		if 'day' in timeframe or 'week' in timeframe:
			if 'week' in timeframe:
				t *= 7  # convert to days
			if date[1] > t:
				date[1] -= t
			else:
				leftover = t - date[1]
				if date[0] > 1:
					date[0] -= 1
				else:
					date[0] = 12
				date[1] = 31 - leftover
		elif 'month' in timeframe:
			if date[0] > t:
				date[0] -= t
			else:
				leftover = t - date[0]
				date[2] -= 1
				date[0] = 12 - leftover
			date[1] = 30  # end of the month, to check across the entire month
		else:  # year
			date[2] -= t

		date[0] = str(date[0])
		date[1] = str(date[1])
		date[2] = str(date[2])

		return '/'.join(date)


	def scroller(self, popup_element, num_scrolls=20):
		"""
			scrolls down a page - not to the very bottom
		"""
		time.sleep(2)
		for _ in range(num_scrolls):
			print('SCROLL')
			self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', popup_element)
			time.sleep(1)
		time.sleep(2)
		print('done SCROLLING')
		return

	def findMatch(self, names, google_reviews):
		potentials = ""
		for i, review in enumerate(google_reviews):
			google_name = review['name'].lower()
			if google_name in names:
				potentials = google_name
		return potentials

	def generateNames(self, first, last):
		variations = set()
		nickname = None
		if "\"" in first or "\'" in first:  # check for nickname
			indexes = [x for x, v in enumerate(first) if (v == "\'" or v == "\"")]
			name = first[:indexes[0]]
			nickname = first[indexes[0] + 1 : indexes[1]]
		if last is not None:
			variations.add((first + ' ' + last).lower())
			variations.add((first + ' ' + last[0]).lower())
			if nickname is not None:
				variations.add((nickname + ' ' + last).lower())
				variations.add((nickname + ' ' + last[0]).lower())
		return variations



if __name__ == '__main__':
	# print(DATE)
	bot = ReviewBot()
	bot.collectNewReviews()

	# write to file
	f = open('../server/worker/google_reviews.txt', 'a+')
	f.write(json.dumps(bot.reviews))
	f.close()






