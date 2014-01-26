import requests
from bs4 import BeautifulSoup
import time
from User import User
import re

class UserDownloader:
    def __init__(self, domain, delay):
        self.domain = domain
	self.delay = delay
        self.last_time = 0
        
    def load_user(self, username):
        self.wait()
        print "Getting info on user " + username
        request = requests.get("http://profile."+self.domain+"/"+username+"/")
        soup = BeautifulSoup(request.text)
        user = User(username)
        
        # Get join date
        if soup(text=re.compile("registered")):
            user.registration_date = soup(text=re.compile("registered"))[0].parent.text.split("registered ")[-1]
        
        # Get # contributions (not just tabs)
        if soup(text=re.compile("contributions to the site total")):
            user.num_contributions = int(soup(text=re.compile("contributions to the site total"))[0].parent.text.split("contributions to ")[0].split("made ")[-1])
        
        # Get ranking
        if soup(text=re.compile("contributor among all users")):
            user.rank = int(soup(text=re.compile("contributor among all users"))[0].parent.text.split(" contributor among all users")[0].split("ranked #")[-1])
        
        # More later, this should suffice
        
    def wait(self):
        while self.last_time > time.time():
            pass
        self.last_time = time.time()+(self.delay/1000)
        return
