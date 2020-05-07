# Moodle Bot
what it can do?
- update your calendar with moodle exercises
- send you en email if you have an open exercises that you need to finish in a day

# Usage
## Prerequisites
Install the packages
- selenium
- pytz
- ics
- google-api-python-client 
- google-auth-httplib2 
- google-auth-oauthlib
- beautifulsoup4

one command rule them all:
pip install --upgrade selenium pytz ics google-api-python-client google-auth-httplib2 google-auth-oauthlib beautifulsoup4

install [Chrome Driver](https://chromedriver.chromium.org/) and put it in the same directory of moodle_to_calendar.py 

go to [google console](https://console.cloud.google.com/) create a new project and
go to the api library and enable [calender api](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com?q=calender) and [gmail api](https://console.cloud.google.com/apis/library/gmail.googleapis.com?q=gmail)
now you need to create credential so your python code can access those apis, click on the burger menu and click on api
 -> [credentials](https://console.cloud.google.com/apis/credentials) click configure consent screen -> external -> create 
-> fill the gaps -> add scope -> google calender api (make sure to choose events or stronger access) gmail api (make sure to choose send or stronger access) -> add -> scroll down and save.
click on the burger menu and click on api -> [credentials](https://console.cloud.google.com/apis/credentials) click on create credentials -> Oauth client ID -> other -> save -> ok -> now in this page search for the credential you just created under OAuth 2.0 Client IDs and download it.
rename it to 'credentials.json' and put it in the same directory of moodle_to_calendar.py 

## the code itself
you choose to creat file secrets.py like that:

moodle_username = 'YOUR MOODLE USERNAME'

moodle_password = 'YOUR MOODLE PASSWORD'

mail_to = 'YOUR EMAIL'

mail_from = 'YOUR EMAIL'

if you don't want to create this file, you need to search in the code those variables and swap them with your secrets

## run the code
in the first time run it with a regularly to check for a problems, it there are non, run it with pythonw so it will run in the background.  
there may be a problem with the background process
