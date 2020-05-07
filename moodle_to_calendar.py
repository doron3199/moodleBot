# credit https://medium.com/@moungpeter/how-to-automate-downloading-files-using-python-selenium-and-headless-chrome-9014f0cdd196
import base64
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import datetime
import pytz
from ics import Calendar
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
from email.mime.text import MIMEText
import os
from bs4 import BeautifulSoup
import secrets


class Exercise:
    def __init__(self, course, ex_num, date):
        self.course = course
        self.ex_num = ex_num
        self.date = date


SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/gmail.send']


def login():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--verbose')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.dirname(os.path.abspath(__file__)),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')

    # initialize driver object and change the <path_to_chrome_driver> depending on your directory where your chromedriver should be
    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get('https://moodle.idc.ac.il/2020/my/index.php?lang=en')
    username = driver.find_element_by_xpath('//*[@id="input_1"]')
    password = driver.find_element_by_xpath('//*[@id="input_2"]')
    login_btn = driver.find_element_by_xpath('//*[@id="submit_row"]/td[2]/input')
    username.send_keys(secrets.moodle_username)
    password.send_keys(secrets.moodle_password)
    login_btn.click()
    sleep(1)
    return driver


def download_calender():
    # instantiate a chrome options object so you can set the size and headless preference
    # some of these chrome options might be uncessary but I just used a boilerplate
    # change the <path_to_download_default_directory> to whatever your default download folder is located
    driver = login()
    driver.get('https://moodle.idc.ac.il/2020/calendar/export.php')
    radio_btn1 = driver.find_element_by_xpath('//*[@id="id_events_exportevents_all"]')
    radio_btn2 = driver.find_element_by_xpath('//*[@id="id_period_timeperiod_recentupcoming"]')
    export = driver.find_element_by_xpath('//*[@id="id_export"]')

    radio_btn1.click()
    radio_btn2.click()
    export.click()
    is_downloaded = False

    while not is_downloaded:
        try:
            f = open("icalexport.ics", "r")
            print('calender downloaded')
            f.close()
            is_downloaded = True
            driver.close()
        except:
            print('calender downloading...')
            sleep(1)

def google_api_auth():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def upload_to_google_calender():
    creds = google_api_auth()
    service = build('calendar', 'v3', credentials=creds)

    f = open("icalexport.ics", "r", encoding="utf8")
    text = f.read()
    temp_cal = Calendar(text)
    f.close()
    os.remove("icalexport.ics")

    for eve in temp_cal.events:
        event = {
            'summary': eve.name + " " + eve.categories.pop().split('-')[0],
            'start': {
                'dateTime': eve.begin.datetime.isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'dateTime': eve.end.datetime.isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
            'reminders': {
                'useDefault': False,
            },
            'id': eve.uid.split('@')[0] + 'moodlecalenderbot1'
        }
        try:
            event = service.events().insert(calendarId='primary', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))
        except Exception as e:
            if 'The requested identifier already exists.' not in str(e):
                print('failed to send email, error: {}'.format(e))
    print('calender upload finished')



def check_for_unaccomplished_tasks():
    month_dict = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }
    driver = login()
    sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # close web browser
    driver.close()
    html_text = soup.getText()
    html_text = html_text.split('Today')[1]
    html_text = html_text.split('Next 30 days')[0]
    exe = html_text.split('Exercise')
    text_list = []
    final_list = []
    for ex in exe:
        if 'Add submission' in ex:
            text_list.append(ex.split('Add submission')[0])

    for item in text_list:
        item = str(item).strip()
        item = item.split('\n', 2)
        num = 'unknown'
        for i in list(item[0].split()[0]):
            if i.isdigit():
                num = i
                break
        name = item[1].split('-')[0]
        date_text, time_text = item[2][-15:].strip().split(',')
        day, month = date_text.split(' ')
        year = datetime.date.today().year
        if month == 'January' and datetime.date.today().month == 12:
            year += 1
        date = datetime.datetime(year=year, month=month_dict[month[:3]], day=int(day),
                                 hour=int(time_text.split(':')[0]), minute=int(time_text.split(':')[1]))
        date = pytz.timezone('Asia/Jerusalem').localize(date)
        final_list.append(Exercise(name, num, date))

    return_text = ''

    for i in final_list:
        delta = i.date - pytz.timezone('Asia/Jerusalem').localize(datetime.datetime.today())

        if delta.days <= 1:
            return_text += 'Exercise {} in {} is not submitted, you have {} hours left\n'.format(i.ex_num,
                                                                                                 str(i.course).strip(),
                                                                                                 str(delta).split(":")[
                                                                                                     0])

    return return_text


def send_mail(tasks):
    creds = google_api_auth()
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(str(tasks))
    message['to'] = secrets.mail_to
    message['from'] = secrets.mail_from
    message['subject'] = 'moodle remainder'

    msg = {'raw': base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')}

    try:
        message = (service.users().messages().send(userId='me', body=msg)
                  .execute())
        print('Message Id: {}'.format(message['id']))
        return message
    except Exception as e:
        print('An error occurred while sending email {}'.format(e))


def main():
    while 1:
        print('moodle bot says good morning!')
        download_calender()
        upload_to_google_calender()
        tasks = check_for_unaccomplished_tasks()
        if len(tasks) is not 0:
            send_mail(tasks)
        print('moodle bot is going to sleep')
        sleep(60 * 60 * 24)


if __name__ == '__main__':
    main()
