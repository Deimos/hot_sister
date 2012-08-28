# Fetches the top posts from a sister subreddit and updates the main subreddit's sidebar with a list of them
# The user defined in the cfg file must be a moderator of all main subreddits defined in the db
# The main subreddit's sidebar must include strings to denote the beginning and ending location of the list, the bot will not update the sidebar if these strings are not present
# With the default delimiters the sidebar should include a chunk of text like:
# 
# **Top posts in our sister subreddit:**
# [](/hot-sister-start)
# [](/hot-sister-end)
# Other text that will be below the list

import sys, os
import re
import praw
import HTMLParser
from ConfigParser import SafeConfigParser
import sqlite3

def main():
    containing_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

    # load config file
    cfg_file = SafeConfigParser()
    path_to_cfg = os.path.join(containing_dir, 'hot_sister.cfg')
    cfg_file.read(path_to_cfg)

    # connect to db and get data
    path_to_db = os.path.join(containing_dir, 'hot_sister.db')
    con = sqlite3.connect(path_to_db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM subreddit_pairs')
    subreddit_pairs = cur.fetchall()

    # log into reddit
    r = praw.Reddit(user_agent=cfg_file.get('reddit', 'user_agent'))
    r.login(cfg_file.get('reddit', 'username'), cfg_file.get('reddit', 'password'))

    for pair in subreddit_pairs:
        # get the subreddits
        main_subreddit = r.get_subreddit(pair['main'])
        sister_subreddit = r.get_subreddit(pair['sister'])

        # fetch the posts from the sister subreddit, and build the text to update the sidebar with
        list_text = str()
        if pair['post_type'] == 'new':
            get_method = getattr(sister_subreddit, 'get_new_by_date')
        else:
            get_method = getattr(sister_subreddit, 'get_hot')
        for (i, post) in enumerate(get_method(limit=pair['num_posts'])):
            list_text += '%s. [%s](%s)\n' % (i+1, post.title, post.permalink)

        # update the sidebar
        current_sidebar = main_subreddit.get_settings()['description']
        current_sidebar = HTMLParser.HTMLParser().unescape(current_sidebar)
        replace_pattern = re.compile('%s.*?%s' % (re.escape(cfg_file.get('reddit', 'start_delimiter')), re.escape(cfg_file.get('reddit', 'end_delimiter'))), re.IGNORECASE|re.DOTALL|re.UNICODE)
        new_sidebar = re.sub(replace_pattern,
                            '%s\\n\\n%s\\n%s' % (cfg_file.get('reddit', 'start_delimiter'), list_text, cfg_file.get('reddit', 'end_delimiter')),
                            current_sidebar)
        main_subreddit.update_settings(description=new_sidebar)
        

if __name__ == '__main__':
        main()
