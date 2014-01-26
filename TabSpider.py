from bs4 import BeautifulSoup
from collections import deque
import re
import time
import requests

class TabSpider:
    def __init__(self, domain, delay=0):
        self.domain = domain
        self.delay = delay
        self.last_time = 0
        self.alphas = deque(["0-9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"])
        self.prepare_artist_list()
        
    def wait(self):
        while self.last_time > time.time():
            pass
        self.last_time = time.time()+(self.delay/1000)
        return
    
    def prepare_artist_list(self,page=None):
        # we need to have pages to pop
        if page and self.alpha_pages:
            # Page is used when switching pages in the same alpha
            url = self.alpha_pages.popleft()
        else:
            # otherwise get another batch
            self.current_alpha = self.alphas.popleft()
            url = "http://www.%s/bands/%s.htm" %(self.domain,self.current_alpha)
        
        # Get page
        self.wait()
        print "retrieving " + url[31:]
        request = requests.get(url)
        soup = BeautifulSoup(request.text)
        
        # Fill artist URLs
        self.artist_urls = deque([])
        urls = soup.find_all("a",href=re.compile("^/tabs/"))
        for url in urls:
            self.artist_urls.append("http://www."+self.domain+url.get("href"))
        
        # get page listing
        if not page: 
            page_links = soup.find_all(class_="ys")
            self.alpha_pages = deque([])
            for link in page_links:
                self.alpha_pages.append(link)
        
        # Prepare tab list for first artist
        self.prepare_tabs_list()
        
    def prepare_tabs_list(self, page=None):
        # Note: artist_pages are paginated pages for 1 artist
        # artist_urls is the master list of artists
        
        if page and self.artist_pages:
            artist_url = self.artist_pages.popleft()
        else:
            # Pop the first artist
            artist_url = self.artist_urls.popleft()
            self.tab_urls = deque([])
        
        # Get page
        self.wait()
        print "retrieving " + artist_url[31:]
        request = requests.get(artist_url)
        soup = BeautifulSoup(request.text)
        
        # Get all guitar pro links
        tab_links = soup.find_all("a",href=re.compile("tabs\."+self.domain),text=re.compile("Guitar Pro Tab"));
        for link in tab_links:
            self.tab_urls.append(link.get("href"))
            
        # get page listing if new
        if not page:
            page_links = soup.find_all(class_="ys")
            self.artist_pages = deque([])
            for link in page_links:
                self.artist_pages.append("http://www."+self.domain+link.get("href"))
                
    def next_url(self):
        # this logic is gonna hurt, sorry, but it covers all the worst possible edge cases of invalid tabs
        if self.tab_urls:
            return self.tab_urls.popleft()
        else:
            # Check if theres another page of tabs
            while self.artist_pages:
                # load new page
                self.prepare_tabs_list(True)
                if self.tab_urls:
                    return self.tab_urls.popleft()
            # Ran out of pages for that specific artist, check if there's another artist ready
            while self.artist_urls:
                # load new artist
                self.prepare_tabs_list()
                # check for new Urls
                if self.tab_urls:
                    return self.tab_urls.popleft()
                # nope
                if self.tab_urls:
                    return self.tab_urls.popleft()
                # No valid tabs on this page for this artist, check for more pages
                while self.artist_pages:
                    # load tab new page
                    self.prepare_tabs_list(True)
                    if self.tab_urls:
                        return self.tab_urls.popleft()
                # No remaining pages of tabs for this artist
            # At this point we've run out of artists on this page, lets do more pages
            while self.artist_pages:
                # load new artist pages
                self.prepare_artist_list(True)
                # check for new Urls
                if self.tab_urls:
                    return self.tab_urls.popleft()
                # nope
                while self.artist_urls:
                    # load new artist
                    self.prepare_tabs_list()
                    if self.tab_urls:
                        return self.tab_urls.popleft()
                    # No valid tabs on this page for this artist, check for more pages
                    while self.artist_pages:
                        # load tab new page
                        self.prepare_tabs_list(True)
                        if self.tab_urls:
                            return self.tab_urls.popleft()
            # Now we've exhausted all pages for this alpha, onto next alpha!
            while self.alphas:
                self.prepare_artist_list()
                # check for new Urls
                if self.tab_urls:
                    return self.tab_urls.popleft()
                # nope
                while self.artist_pages:
                    # load new artist pages
                    self.prepare_artist_list(True)
                    while self.artist_urls:
                        # load new artist
                        self.prepare_tabs_list()
                        # check for new Urls
                        if self.tab_urls:
                            return self.tab_urls.popleft()
                        # nope
                        if self.tab_urls:
                            return self.tab_urls.popleft()
                        # No valid tabs on this page for this artist, check for more pages
                        while self.artist_pages:
                            # load tab new page
                            self.prepare_tabs_list(True)
                            if self.tab_urls:
                                return self.tab_urls.popleft()
        # There arent even any alphas left, we're done!
        return None
        
    def has_more(self):
       return True # I'm so sorry, this is a hackathon 
