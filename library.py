import re
import sys
from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver

print '\n\t' + '*' * 40 + '\n \t DTU Library at your terminal' + '\n\t' + '*' * 40

print 'Starting server...'
driver = webdriver.Firefox()
driver.set_window_size(1024, 768)

print 'Going to the site...'
driver.get('http://14.139.251.99:8080/jopacv06/html/checkouts')
login_id_element = driver.find_element_by_id('txtmemberid')
member_id = raw_input('Please Enter your Library Registration Number \n --> ')
login_id_element.send_keys(member_id)
submit_btn = driver.find_element_by_xpath("//*[@type='submit']")

print 'Submitting Details...'
submit_btn.submit()

home_btn_class = 'aHrefTitleMenu'
driver.get('http://14.139.251.99:8080/jopacv06/html/SearchForm')
driver.get('http://14.139.251.99:8080/jopacv06/html/checkouts')
sleep(3)

print 'All right! If you are a GUI kind of person, a screenshot has been clicked for you'

screenshot_name = 'library ' + member_id + ' ' + str(datetime.now().date())
driver.save_screenshot(screenshot_name + '.png')

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
with open('soup.txt', 'w') as file:
    file.write(html.encode('utf-8'))

user_detail_soup = soup.find('table', id='AutoNumber1')
if user_detail_soup:
    user_details = {}
    try:
        user_name_list = user_detail_soup.find('td', class_='memberTDOUT').get_text().split()
        user_details['user_name'] = user_name_list[2] + ' ' + user_name_list[1]
        checkout_stats = user_detail_soup.find_all('td', class_='memberTDIN')
        user_details['num_checkouts'] = checkout_stats[0].get_text()
        user_details['last_checkout_date'] = checkout_stats[1].get_text()
        user_details['num_reserves'] = checkout_stats[2].get_text()
        user_details['fine'] = float(re.search(r'\d+\.\d+', checkout_stats[3].get_text()).group())
    except:
        pass

print 'So Mr. ' + user_details['user_name'] + ' let\'s see what you\'ve got...'

if user_details['num_checkouts'] == 0:
    print 'So you have no books issued from library \n looks like you don\'t study at all. \n Complaining your parents...'
    sys.exit(1)

print 'Hmm...not bad\n You have %s books issued. \n The last time you checked out was on %s' \
      % (user_details['num_checkouts'], user_details['last_checkout_date'])
if user_details['fine'] > 1:
    print "You owe %f as fine. So careless...." % (user_details['fine'])
else:
    print "And thankfully, you don't have any fine."

book_details_soup = soup.find('table', class_='briefListTbl')
if book_details_soup:
    book_details_list = []
    try:
        for row in book_details_soup.find_all('tr', id=re.compile('^checkoutsRow')):
            details = row.find_all('td')
            details_dict = {}
            details_dict['s_no'] = int(re.search(r'\d', row['id']).group())
            details_dict['book_code'] = details[0].get_text().replace('\n', '')
            details_dict['book_name'] = details[1].get_text().replace('\n', '')
            details_dict['book_author'] = details[2].get_text().replace('\n', '')
            due_date_string = details[3].get_text()
            due_date = datetime.strptime(due_date_string, '%d/%m/%Y\n')
            details_dict['book_due_date'] = due_date
            details_dict['next_renewal_date_diff'] = (due_date - datetime.now()).days
            book_details_list.append(details_dict)
    except:
        pass

renewal_button = driver.find_element_by_class_name('briefListHREFFoot')
sleep(6)
print '\n' + '*' * 15 + '\n YOUR BOOKS' + '\n' + '*' * 15

for book in book_details_list:
    for key, value in book.iteritems():
        print '%s : %s \t' % (key, value)
    print '\n'

print "Well! I can also reissue the books for you, Just enter the s_no of all the books to reissue seperated by space."
to_renew = [int(s_no) for s_no in raw_input('--> ').split(' ')]
for book in book_details_list:
    if book['next_renewal_date_diff'] > 0 and book['s_no'] in to_renew:
        book_row_element = driver.find_element_by_id('checkoutsRow' + str(book['s_no']))
        book_row_element.click()
        renewal_button.click()
