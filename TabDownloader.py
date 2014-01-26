import hashlib
import urllib2
import requests
from bs4 import BeautifulSoup
from os.path import join
import re
import ast
import time
from TabSpider import TabSpider
from TabData import TabData
from User import User
from Comment import Comment



class TabDownloader:
    def __init__(self, domain, tab_page, salt,delay, tab_dir=""):
        self.domain = domain    
        self.tab_page = tab_page
        self.salt = salt
        self.tab_dir=tab_dir
        self.last_time = 0
	self.delay = delay
        
    def process_comment(self,comment):
        result = Comment()
        
        # Get content
        result.content = comment.find("div", attrs={"class":"comment_content"}).text.strip()
        
        # Get rating
        result.rating = int(comment.find("ins").text.replace("+",""))
        
        # Get author
        result.author = comment.find("a", attrs={"href":re.compile("profile")}).text.strip()
        
        # Get date
        result.date = comment.find("span", attrs={"class":"gray1"}).text.split("wrote on ")[-1].strip()
        
        return result
        
    def tab_download(self, request_url, get_comments=False):
        print"Getting info on tab "+ request_url[31:]
        # TabData file, will be returned at the end
        tab_data = TabData()
        
        # Load page
        self.wait()
        request = requests.get(request_url)
        soup = BeautifulSoup(request.text)
        
        # Check if tab is removed
        if len(soup.find_all(class_="t_blocked")) > 0:
            return None
        
        # Find session ID
        session_id = soup.find("input", attrs={"name":"session_id"})
        if session_id:
            session = session_id.get("value")
        else:
            return None
        
        # Find Tab ID
        tab_id = soup.find("input", attrs={"name":"tab_id"}).get("value")
        
        # Get hash
        sha1 = hashlib.sha1(self.salt+tab_id).hexdigest()
        
        try:
            # Get TAB file
            file_url = "http://www."+self.domain+"/"+self.tab_page+"?tab_id=%s&session_id=%s&token=%s" %(tab_id,session,sha1)
            tab_file = urllib2.urlopen(file_url)
            
            # URL does not contain filename, need to get it from headers
            filename = tab_file.headers['Content-Disposition'].split("=")[-1]
            
            # Write it to disk
            local_file = open(self.tab_dir+filename, "wb")
            #local_file.write(f.read())
            local_file.close()
            
            tab_data.tab_file = join(self.tab_dir+filename)
            
        except urllib2.HTTPError, e:
            print "HTTP Error:",e.code , url
        except urllib2.URLError, e:
            print "URL Error:",e.reason , url
            
        # Get title and version
        tab_info = ast.literal_eval("{"+soup(text=re.compile("'name': '.+?',"))[0].split("= {")[-1].split(";")[0])
        tab_data.title = tab_info["name"]
        tab_data.version = tab_info["version"]
        
        # Get tab contributor, if there is no contributor, instruments needs -1 index
        shift = 1
        tab_data.tabber = None
        
        t_dtde = soup.find_all("div", attrs={"class":"t_dtde"})
        if (len(t_dtde) == 3):
            shift = 0
            tab_data.tabber = t_dtde[0].text.strip()
        
        # Get instruments
        tab_data.instruments = t_dtde[2-shift].text.strip().split(",")
        
        # Get rating
        tab_data.rating = len(soup.find_all("a", attrs={"class":"cur"}))
        
        # Get number of ratings, empty if no ratings
        tab_data.num_ratings = soup.find("div", attrs={"class":"v_c"}).text.strip().split("x ")[-1]
        if not tab_data.num_ratings:
            tab_data.num_ratings = 0
        
        # Get num views
        tab_data.num_views = soup.find("div", attrs={"class":"stats"}).text.strip().split(" views")[0].replace(",","")
        
        # Get num comments
        tab_data.num_comments = soup.find("span", attrs={"class":"t_cbl"}).text.strip().split(" comments")[0]
        if tab_data.num_comments == "no":
            tab_data.num_comments = 0
        
        
        # Get comment content
        if get_comments:
            comment_url = "http://tabs.%s/comment/?tabid=%s" %(self.domain,tab_id)
            self.wait()
            request = requests.get(comment_url)
            soup2 = BeautifulSoup(request.text.strip())
            
            # Comments are flat in html, but nested based on their "level" as denoted in their class
            # To deal with this, we use a stack to make sure subcomments are appropriately added.
            # Recursion would be optimal, but is not possible due to the flat structure
            comment_level=0
            current_level_comments = []
            stack = []
            for comment in soup2.find_all("div", class_=re.compile("lev")):
                new_level = int(comment.get("class")[2].split("lev")[-1])
                
                if new_level > comment_level:
                    stack.append(current_level_comments)
                    current_level_comments = []
                    current_level_comments.append(self.process_comment(comment))
                    comment_level = new_level
                elif new_level < comment_level:
                    # when popping, you may drop multiple levels
                    while comment_level != new_level:
                        popped = stack.pop()
                        popped[-1].child_comments = current_level_comments
                        current_level_comments = popped
                        comment_level -= 1 
                    current_level_comments.append(self.process_comment(comment))
                else:
                    current_level_comments.append(self.process_comment(comment))
                    
            # Pop until list is empty
            while stack:
                popped = stack.pop()
                popped[-1].child_comments = current_level_comments
                current_level_comments = popped
                
            tab_data.comments = current_level_comments
        
        return tab_data
    
    def wait(self):
        while self.last_time > time.time():
            pass
        self.last_time = time.time()+(self.delay/1000)
        return
