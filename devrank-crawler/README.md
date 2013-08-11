devrank-crawler
===============

This is a simple Github Crawler for DeveloperRank by YasikStudio.


Install dependencies (global)
-----------------------------

    virtualenv .
	source bin/activate
    pip install -r requirements.txt


Settings
--------

Set your GitHub username and password to `config.py` file like this.
You can create `client_id` and `client_secret` at here:
https://github.com/settings/applications/new

    # config.py (copied from config-templates.py)
    username = 'jong10'
    password = 'abcdefghijklmn'
    client_id = 'xxxxxxxxxxxxxxxxx'
    client_secret = 'xxxxxxxxxxxxxxxxxxxx'


Set first userlist to `userlist.txt' file.

    # userlist.txt (copied from userlist-templates.txt)
    beonit
    frst1809
    jong10
    jweb
    raycon
    reeoss


Set MAXDEPTH in ghcrawler.py source file.

    class GitHubCrawler(object):

        USERLIST = 'userlist.txt'
        MAXDEPTH = 5 <<================ this


How to run this
---------------

    nohup ./ghcrawler.py &

and watch gh.log file
