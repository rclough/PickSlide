import ConfigParser
from os.path import expanduser, join
from collections import deque
from TabSpider import TabSpider

conf_file = join(expanduser("~"),"scrape.conf")

# Config
config = ConfigParser.ConfigParser()
config.read(conf_file)
salt = config.get('info', 'salt')
tab_page = config.get('info','tab_page')
domain = config.get('info','domain')
delay = int(config.get('info','delay'))

#tdl = TabDownloader(domain, tab_page, salt)
#tu = UserDownloader(domain)
#test_page = "http://tabs."+domain+"/m/megadeth/symphony_of_destruction_ver6_guitar_pro.htm"
#test_page = "http://tabs."+domain+"/r/ryan_clough/love_lust_power_tab.htm"
#test_page = "http://tabs."+domain+"/l/lynyrd_skynyrd/free_bird_guitar_pro.htm"
#test_page = "http://tabs."+domain+"/j/justin_bieber/all_that_matters_crd.htm"
#tab_data =  tdl.tab_download(test_page,True)

#tu.load_user("Bonsaischaap")

ts = TabSpider(domain, delay)
while ts.has_more():
    ts.next_url()

# if tab_data:
#     for comment in tab_data.comments:
#         print "level 1 comment by " + comment.author
#         if hasattr(comment, "child_comments"):
#             print "\tlevel 2 comments: " + str(comment.child_comments)
