# Fetches the top posts from a sister subreddit and updates the main subreddit's sidebar with a list of them
# The main subreddit's sidebar must include strings to denote the beginning and ending location of the list, the bot will not update the sidebar if these strings are not present
# With the default delimiters the sidebar should include a chunk of text like:
# 
# **Top posts in our sister subreddit:**
# [](/hot-sister-start)
# [](/hot-sister-end)
# Other text that will be below the list

import re
import praw

# defines the main and sister subreddits, and how many posts to list in the sidebar
MAIN_SUBREDDIT = 'gamestest'
SISTER_SUBREDDIT = 'Games'
POSTS_TO_LIST = 5

# login info for the script to log in as, this user must be a mod in the main subreddit
REDDIT_USERNAME = 'username'
REDDIT_PASSWORD = 'password'

# don't change unless you want different delimiter strings for some reason
START_DELIM = '[](/hot-sister-start)'
END_DELIM = '[](/hot-sister-end)'

# log into reddit
r = praw.Reddit(user_agent=REDDIT_USERNAME)
r.login(REDDIT_USERNAME, REDDIT_PASSWORD)

# get the subreddits
main_subreddit = r.get_subreddit(MAIN_SUBREDDIT)
sister_subreddit = r.get_subreddit(SISTER_SUBREDDIT)

# fetch the top posts from the sister subreddit, and build the text to update the sidebar with
list_text = str()
for (i, post) in enumerate(sister_subreddit.get_hot(limit=POSTS_TO_LIST)):
    list_text += '%s. [%s](%s)\n' % (i+1, post.title, post.permalink)

# update the sidebar
current_sidebar = main_subreddit.get_settings()['description']
replace_pattern = re.compile('%s.*?%s' % (re.escape(START_DELIM), re.escape(END_DELIM)), re.IGNORECASE|re.DOTALL|re.UNICODE)
new_sidebar = re.sub(replace_pattern,
                    '%s\\n\\n%s\\n%s' % (START_DELIM, list_text, END_DELIM),
                    current_sidebar)
main_subreddit.update_settings(description=new_sidebar)
