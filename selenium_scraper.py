from selenium import webdriver
from selenium.webdriver.firefox.options import Options 
import re, time, json 

user_email = ''
user_pass = ''

''' Initialize Driver in the background '''
option = Options()
option.headless = True 
driver = webdriver.Firefox(options=option)

links = [ 
    'https://www.alomoves.com/series/building-balance-ground-work'
]

def get_info(entry):
    '''
    Extract name, url and id from HTML
    '''
    main = entry.find_element_by_css_selector('.workout-title > a')
    wo_name = entry.find_element_by_css_selector('.index').text + ' - ' + main.text.capitalize()
    wo_url =  main.get_attribute('href')
    wo_id = re.search(r"/workouts/(?P<id>.+?)\?", wo_url).group(1)

    return [wo_name, wo_id, wo_url]

def get_download_link(wo_url): 
    '''
    Extract video src from page
    '''
    driver.get(wo_url)
    time.sleep(2)
    try:
        video_url = driver.find_element_by_css_selector('.alo-video-container video').get_attribute('src')
        return video_url
    except: 
        print('something went wrong here!')
        return
    
        

''' Login ''' 
print('starting scrapper')
driver.get('https://www.alomoves.com/signin')
time.sleep(2)

email = driver.find_elements_by_xpath('//form[@id="signin"]/div[@class="field"]//input')
password = driver.find_elements_by_xpath('//form[@id="signin"]//input')
button = driver.find_elements_by_xpath("//div[@class='login-button']//button")

email[0].send_keys(user_email)
email[1].send_keys(user_pass)
button[0].click()

time.sleep(2)
print('logged in')

''' Scrapping '''
total = len(links)
for count, link in enumerate(links, 1):
    print('PLAN #{} OUT OF {}'.format(count, total))

    driver.get(link)
    time.sleep(2)

    ''' Header infos ''' 
    print('getting headers')
    header = driver.find_element_by_css_selector('.plan-bundle-label-container > .content-section')
    entries = driver.find_elements_by_css_selector('.plan_entry > .workouts-section-header')
    difficulty = driver.find_element_by_css_selector('.difficulty-section .desc')
    unique_videos = driver.find_element_by_css_selector('.stat-row .desc')

    get_header = lambda pg_header : { 'name': pg_header.find_element_by_css_selector('.big-title').text, 'class_link': link, 
    'instructor': pg_header.find_element_by_css_selector('.plan-coach-link').text, 'difficulty' : difficulty.text, 'unique_videos' : unique_videos.text}
    plan = get_header(header)
    print(plan)
    time.sleep(1)

    ''' Workout infos '''
    print('getting workouts info')
    plan['workouts'] = [get_info(entry) for entry in entries] 

    print('getting video url ({})'.format(len(plan['workouts'])))
    for item in plan['workouts']: 
        item.append(get_download_link(item[2]))

    ''' JSON '''
    print('writing json')
    js = json.dumps(plan)
    with open('/Users/ana/Documents/Python/links_alomoves.json', 'a' ) as outfile:
        outfile.write(js)

    print('saving plan done')

''' Quit '''
print('quitting driver')
driver.quit()

