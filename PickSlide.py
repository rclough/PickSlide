import ConfigParser
from os.path import expanduser, join
from bulbs.neo4jserver import Graph, Config, NEO4J_URI
import sys
from UserDownloader import UserDownloader
from TabDownloader import TabDownloader

def main(argv=None):
    # Config processing
    conf_file = join(expanduser("~"),"scrape.conf")
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    salt = config.get('info', 'salt')
    tab_page = config.get('info','tab_page')
    domain = config.get('info','domain')
    delay = config.get('info', 'delay')
    
    # Start graph
    config = Config(NEO4J_URI)
    g = Graph(config)
    g.clear() # Change if youre working with persistent data store!!!!
    
    # Set up local indices 
    users = {}
    instruments = {}
    
    # Make page crawlers
    tab_loader = TabDownloader(domain, tab_page, salt)
    user_loader = UserDownloader(domain, delay)
    
    # Unofficial iterator
    resource = TabSpider(domain)
    
    # Start crawling!
    while resource.has_more():
        # Get tab info
        tab_info = tab_loader.tab_download(resource.next_url())
        
        # has_more doesnt actually work because of the retarted logic needed to keep track of tabs
        if not tab_info:
            break
        
        # If tab is valid
        if tab_info:
            # Store base tab
            tab_node = g.vertices.create(name=tab_info.tab_file)
            tab_node.tab_file = tab_info.tab_file
            tab_node.title = tab_info.title
            tab_node.version = tab_info.version
            tab_node.rating = tab_info.rat
            tab_node.num_ratings = tab_info.num_ratings
            tab_node.num_comments = tab_info.num_comments
            tab_node.label = "tab"
            tab_node.save()
            
            # Add instruments
            for instrument in tab_node.instruments:
                if instruments not in instruments:
                    i_node = g.vertices.create(name=instrument)
                    i_node.label = "instrument"
                    i_node.save()
                    instruments[instrument] = i_node
                i_node = instruments[instrument]
                g.edges.create(tab_node,"has_instrument",i_node)
            
            # Add comments (recursive)
            for comment in tab_info.comments:
                g.edges.create(tab_node,"has_comment",save_comment(g, comment))
            

            tab_attr(("tabber",tab_info.tabber ))
            
            # Get info on the tabber if we don't have it
            if tab_info.tabber:
                if tab_info.tabber not in users:
                    tabber = user_loader.load_user(tab_info.tabber)
                    # create user node for tabber
                    u_node = g.vertices.create(name=tabber.name)
                    u_node.registration_date = tabber.registration_date
                    u_node.num_contributions = tabber.num_contributions
                    u_node.rank = tabber.rank
                    u_node.save()
                    users[tab_info.tabber] = u_node
                
                # Add tab to tabber's transcriptions
                tabber = users[tab_info.tabber]
                g.edges.create(tabber,"tabbed",tab_node)
                
    print "Finished crawl! Woah!"
    
def save_comment(g, comment):
    # Create comment node
    c_node = g.vertices.create(name=comment.author+","+comment.date)
    c_node.author = comment.author #could create user node for this if wanted
    c_node.content = comment.content
    c_node.rating = comment.rating
    c_node.date = comment.date
    c_node.save()
    
    # Recursively save child comments
    for child in comment.child_comments:
        g.edges.create(c_node,"has_comment",save_comment(g, child))
        

if __name__ == "__main__":
    sys.exit(main())
