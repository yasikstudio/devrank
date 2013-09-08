devrank-sqlclient
=================

devrank-sqlclient


Setup
-----

	apt-get install python-dev libmysqlclient-dev (Ubuntu)
	brew install mysql (Mac OS X)
	
    pip install -r ../devrank-sqlclient/requirements.txt

How to use this
---------------

    import sys
    sys.path.append('../devrank-sqlclient')

    from models import *
    from client import *

    db = DevRankDB('mysql://username:pass@host:3306/db')
    db.connect()
    s = db.makesession()
    users = s.query(User).all()
