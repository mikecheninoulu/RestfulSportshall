'''
Created on 13.02.2013

Modified on 06.03.2016

Provides the database API to access the forum persistent data.

@author: ivan

@modified: chenhaoyu
'''

from datetime import datetime
import time, sqlite3, re, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/forum.db'
DEFAULT_SCHEMA = "db/forum_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/forum_data_dump.sql"


class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/forum.db*

    '''
    def __init__(self, db_path=None):
        '''
        '''

        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return Connection(self.db_path)

    def remove_database(self):
        '''
        Removes the database file from the filesystem.

        '''
        if os.path.exists(self.db_path):
            #THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        #THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM orders")
            cur.execute("DELETE FROM sports")
            cur.execute("DELETE FROM users")
            cur.execute("DELETE FROM users_profile")
            cur.execute("DELETE FROM friends")
            #NOTE since we have ON DELETE CASCADE BOTH IN users_profile AND
            #friends, WE DO NOT HAVE TO WORRY TO CLEAR THOSE TABLES.

    #METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
    def create_tables(self, schema=None):
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/forum_schema_dump.sql* is utilized.

        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with open(schema) as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then *db/forum_data_dump.sql* is utilized.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open (dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    #METHODS TO CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT
	#METHODS TO CREATE THE SPORT TABLE
    def create_sports_table(self):
        '''
        Create the table ``sports`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE sports(sport_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    sportname TEXT UNIQUE, time TEXT, hallnumber INTEGER, \
                    note TEXT)'
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

	#METHODS TO CREATE THE ORDER TABLE
    def create_order_table(self):
        '''
        Create the table ``order`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE orders(order_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    nickname TEXT,sportname TEXT, timestamp INTEGER, \
                    FOREIGN KEY(sportname) REFERENCES sports(sportname) \
                    ON DELETE CASCADE, \
                    FOREIGN KEY (nickname) \
                    REFERENCES users(nickname) ON DELETE SET NULL)'
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True	
		
	#METHODS TO CREATE THE USER TABLE
    def create_users_table(self):
        '''
        Create the table ``users`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                    nickname TEXT UNIQUE, password TEXT, regDate INTEGER,\
                                    lastLogin INTEGER, timesviewed INTEGER, userType BOOL,\
                                    UNIQUE(user_id, nickname))'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

	#METHODS TO CREATE THE USER PROFILE TABLE
    def create_users_profile_table(self):
        '''
        Create the table ``users_profile`` programmatically, without using
        .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        '''
        #TASK3 TODO#
        Write the SQL Statement and neccesary codeto create users_profile table
        '''
        stmnt = 'CREATE TABLE users_profile(user_id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                    firstname TEXT, lastname TEXT, email TEXT, website TEXT,\
                                    picture TEXT, mobile TEXT, skype TEXT, age INTEGER,\
                                    residence TEXT, gender TEXT, signature TEXT, avatar TEXT,\
                                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

        # return False

	#METHODS TO CREATE THE FRIENDS TABLE
    def create_friends_table(self):
        '''
        Create the table ``friends`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE friends (user_id INTEGER, friend_id INTEGER, \
                     PRIMARY KEY(user_id, friend_id), \
                     FOREIGN KEY(user_id) REFERENCES users(user_id) \
                     ON DELETE CASCADE, \
                     FOREIGN KEY(friend_id) REFERENCES users(user_id) \
                     ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None


class Connection(object):
    '''
    API to access the Forum database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    '''
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()

    #FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        try:
            #Create a cursor to receive the database values
            cur = self.con.cursor()
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print "Foreign Keys status: %s" % 'ON' if is_activated else 'OFF'
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    def unset_foreign_keys_support(self):
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    #HELPERS
    #Here the helpers that transform database rows into dictionary. They work
    #similarly to ORM

    #Helpers for sports
    def _create_sport_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:


            * ``sport_id``: spoort selection id
            * ``sportname``: name of the sport
            * ``time``: sport time
            * ``hallnumber``: sportplace
            * ``note``: some desciptions of the sport

            Note that all values are string if they are not otherwise indicated.

        '''
        sport_id = row['sport_id']
        return {'sport id': sport_id,
		'sport name': row['sportname'],
		'sport time': row['time'],
		'sporthall number': row['hallnumber'],
		'note': row['note']
		}

    def _create_sport_list_object(self, row):
        '''
        Same as :py:meth:`_create_sport_object`. However, the resulting
        dictionary is targeted to build sports in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``sportname`` and
            ``time``

        '''
        return {'sport_id': row['sport_id'], 'sportname': row['sportname'], 'time': row['time'], 'hallnumber': row['hallnumber'], 'note': row['note']}

		
    #Helpers for orders

    def _create_order_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``order_id``: id of the order (int)
            * ``sport_id``: sport to order
            * ``user_nickname``: which user is ordering
            * ``timestamp``: UNIX timestamp (long integer) that specifies when
              the message was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        order_id = 'order-' + str(row['order_id'])
        user = row['nickname']
        sportname = row['sportname']
        timestamp = row['timestamp']
        order = {'order_id': order_id, 'nickname': user,
                   'sportname': sportname, 'timestamp': timestamp}
        return order

    def _create_order_list_object(self, row):
        '''
        Same as :py:meth:`_create_order_object`. However, the resulting
        dictionary is targeted to build orders in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``orderid``, ``user``,
            ``timestamp`` and ``sport_id``.

        '''
        order_id = 'order-' + str(row['order_id'])
        user = row['nickname']
        sport_name = row['sportname']
        timestamp = row['timestamp']
        order = {'order_id': order_id, 'nickname': user,'timestamp': timestamp, 'sportname': sport_name}
        return order

    #Helpers for users
    def _create_user_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'registrationdate':,'nickname':'',
                                   'signature':'','avatar':''},
                'restricted_profile':{'firstname':'','lastname':'','email':'',
                                      'website':'','mobile':'','skype':'',
                                      'age':'','residence':'','gender':'',
                                      'picture':''}
                }

            where:

            * ``registrationdate``: UNIX timestamp when the user registered in
                                 the system (long integer)
            * ``nickname``: nickname of the user
            * ``signature``: text chosen by the user for signature
            * ``avatar``: name of the image file used as avatar
            * ``firstanme``: given name of the user
            * ``lastname``: family name of the user
            * ``email``: current email of the user.
            * ``website``: url with the user's personal page. Can be None
            * ``mobile``: string showing the user's phone number. Can be None.
            * ``skype``: user's nickname in skype. Can be None.
            * ``residence``: complete user's home address.
            * ``picture``: file which contains an image of the user.
            * ``gender``: User's gender ('male' or 'female').
            * ``age``: integer containing the age of the user.

            Note that all values are string if they are not otherwise indicated.

        '''
        return {'public_profile': {'nickname': row['nickname'],
                                   'password': row['password'],
                                   'regDate' : row['regDate'],
                                   'signature': row['signature'],
                                   'avatar': row['avatar'],
                                   'userType': row['userType']},
                'restricted_profile': {'firstname': row['firstname'],
                                       'lastname': row['lastname'],
                                       'email': row['email'],
                                       'website': row['website'],
                                       'gender': row['gender']}
                }

    def _create_user_list_object(self, row):
        '''
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``registrationdate`` and
            ``nickname``

        '''
        return {'nickname': row['nickname'], 'regDate': row['regDate'], 'lastLogin': row['lastLogin'], 'timesviewed': row['timesviewed']}

    #API ITSELF
	
    #ORDER Table API.
    def get_order(self, order_id):
        '''
        Extracts a order from the database.

        :param orderid: The id of the order. Note that orderid is a
            string with format ``order-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_order_object` or None if the order with target
            id does not exist.
        :raises ValueError: when ``orderid`` is not well formed

        '''
        #Extracts the int which is the id for a order in the database
        match = re.match(r'order-(\d{1,3})', order_id)
        if match is None:
            raise ValueError("The order_id is malformed")
        order_id = int(match.group(1))
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM orders WHERE order_id = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (order_id,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return self._create_order_object(row)

    def get_orders(self, nickname=None, number_of_orders=-1,
                     before=-1, after=-1):
        '''
        Return a list of all the orders in the database filtered by the
        conditions provided in the parameters.

        :param user_nickname: default None. Search orders of a user with the given
            nickname. If this parameter is None, it returns the orders of
            any user in the system.
        :type nickname: str
        :param number_of_orders: default -1. Sets the maximum number of
            orders returning in the list. If set to -1, there is no limit.
        :type number_of_orders: int
        :param before: All timestamps > ``before`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type before: long
        :param after: All timestamps < ``after`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type after: long

        :return: A list of orders. Each order is a dictionary containing
            the following keys:

            * ``orderid``: string with the format order-\d{1,3}.Id of the
                order.
            * ``user_nickname``: nickname of the order's owner.
            * ``sport_id``: which sport ordered.
            * ``timestamp``: UNIX timestamp (long int) that specifies when the
                order was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        :raises ValueError: if ``before`` or ``after`` are not valid UNIX
            timestamps

        '''
        #Create the SQL Statement build the string depending on the existence
        #of nickname, numbero_of_orders, before and after arguments.
        query = 'SELECT * FROM orders'
          #Nickname restriction
        if nickname is not None or before != -1 or after != -1:
            query += ' WHERE'
        if nickname is not None:
            query += " nickname = '%s'" % nickname
          #Before restriction
        if before != -1:
            if nickname is not None:
                query += ' AND'
            query += " timestamp < %s" % str(before)
          #After restriction
        if after != -1:
            if nickname is not None or before != -1:
                query += ' AND'
            query += " timestamp > %s" % str(after)
          #Order of results
        query += ' ORDER BY timestamp DESC'
          #Limit the number of resulst return
        if number_of_orders > -1:
            query += ' LIMIT ' + str(number_of_orders)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Build the return object
        orders = []
        for row in rows:
            order = self._create_order_list_object(row)
            orders.append(order)
        return orders

    def delete_order(self, order_id):
        '''
        Delete the order with id given as parameter.

        :param str orderid: id of the order to remove.Note that messageid
            is a string with format ``order-\d{1,3}``
        :return: True if the order has been deleted, False otherwise
        :raises ValueError: if the messageId has a wrong format.

        '''
        #Extracts the int which is the id for a order in the database
        match = re.match(r'order-(\d{1,3})', order_id)
        if match is None:
            raise ValueError("The order_id is malformed")
        order_id = int(match.group(1))
        '''
        * HOW TO TEST: Use the database_api_tests_message. The following tests
          must pass without failure or error:
            * test_delete_order
            * test_delete_order_malformed_id
            * test_delete_order_noexisting_id
        '''
        query = 'DELETE FROM orders WHERE order_id = ?'
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (order_id,)
        cur.execute(query,pvalue)
        self.con.commit()
        if cur.rowcount < 1:
            return False
        return True

    def create_order(self, nickname,
                    sportname):
        '''
        Create a new order with the data provided as arguments.


        :param str user_nickname: the nickname of the person who is ordering.

        :param str sport_id:which sport is ordered

        :return: the id of the created order or None if the order was
            not found. Note that it is a string with the format order-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.

        * HOW TO TEST: Use the database_api_tests_order. The following tests
                       must pass without failure or error:
                * test_create_order
                * test_create_order_malformed_id
                * test_create_order_noexistingid
        '''
        _timestamp = time.mktime(datetime.now().timetuple())
        _nickname = nickname
        _sportname = sportname
        
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        query3 ='SELECT * FROM orders'
        cur.execute(query3)
        rows = cur.fetchall()
        row = cur.fetchone()
        for row in rows:
            if int(_timestamp)-int(row["timestamp"]) > 1000*3600*24*7:
				order_id=row["order_id"]
				query4 = 'DELETE FROM orders WHERE order_id = ?'
				pvalue4 = (order_id,)
				cur.execute(query4,pvalue4)
				self.con.commit()
        query2 = 'SELECT * from sports WHERE sportname = ?'
        pvalue2 = (sportname,)
        cur.execute(query2,pvalue2)
        row = cur.fetchone()
        if row is None:
            return False
        else:
            _sportname = row["sportname"]

        query1 = 'INSERT INTO orders(nickname,sportname,timestamp) VALUES(?,?,?)'
        pvalue1 = (_nickname,_sportname,_timestamp)
        # cur = self.con.cursor()
        cur.execute(query1,pvalue1)
        self.con.commit()
        order_id = cur.lastrowid
        
        if order_id is None:
            ordernumber = None
        else:
            ordernumber = 'order-'+str(order_id)
        return ordernumber

    #MESSAGE UTILS
	
    def get_orderuser(self, order_id):
        match = re.match(r'order-(\d{1,3})', order_id)
        if match is None:
            raise ValueError("The order_id is malformed")
        order_id = int(match.group(1))
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM orders WHERE order_id = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (order_id,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        else:
			username = row["nickname"]
        return username
		
    def contains_order(self, order_id):
        '''
        Checks if a order is in the database.

        :param str order_id: Id of the order to search. Note that messageid
            is a string with the format order-\d{1,3}.
        :return: True if the order is in the database. False otherwise.

        '''
        return self.get_order(order_id) is not None

    #Sport Table API.
    def get_sports(self):
        '''
        Extracts all users in the database.

        :return: list of Users of the database. Each user is a dictionary
            that contains two keys: ``sportname``(str) and ``time``
           . None is returned if the database
            has no users.

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the users
        query = 'SELECT * FROM sports'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Process the response.
        sports = []
        for row in rows:
            sports.append(self._create_sport_list_object(row))
        return sports

    def get_sport(self, sportname):
        '''
        Extracts all the information of a sport.

        :param str sportname: The sportname of the sport to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_sport_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the sport given a sportname
        query1 = 'SELECT sport_id from sports WHERE sportname = ?'
          #SQL Statement for retrieving the sport information
        query2 = 'SELECT sports.* FROM sports \
                  WHERE sports.sport_id = ?'
          #Variable to be used in the second query.
        sport_id = None
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a sportname
        pvalue = (sportname,)
        cur.execute(query1, pvalue)
        #Extract the sport id
        row = cur.fetchone()
        if row is None:
            return None
        sport_id = row["sport_id"]
        # Execute the SQL Statement to retrieve the sport invformation.
        # Create first the valuse
        pvalue = (sport_id, )
        #execute the statement
        cur.execute(query2, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        return self._create_sport_object(row)

    def delete_sport(self, sportname):
        '''
        Remove all sport information of the sport with the sportname passed in as
        argument.

        :param str sportname: The sportname of the sport to remove.

        :return: True if the sport is deleted, False otherwise.

        '''
        #Create the SQL Statements
          #SQL Statement for deleting the sport information
        query = 'DELETE FROM sports WHERE sportname = ?'
        #Activate foreign key support
        #self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (sportname,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def append_sport(self, sportname, sport):
        '''
        Create a new sport in the database.

        :param str sportname: The name of the sport to add
        :param dict sport: a dictionary with the information to be modified. The
        dictionary has the following structure:
		:return: a dictionary with the following format:
                .. code-block:: javascript

            * ``sport_id``: spoort selection id
            * ``sportname``: name of the sport
            * ``time``: sport time
            * ``hallnumber``: sportplace
            * ``note``: some desciptions of the sport

        Note that all values are string if they are not otherwise indicated.
        sport_id = row['sport_id']
        return {'sport id': sport_id,
		'sport name': row['sportname'],
		'sporthall number': row['hallnumber'],
		'note': row['note']
		}

        :return: the sportname of the sport or None if the
            ``sportname`` passed as parameter is not  in the database.
        :raise ValueError: if the sport argument is not well formed.

        '''
        #Create the SQL Statements
          #SQL Statement for extracting the sport id given a sport name
        query1 = 'SELECT sport_id from sports WHERE sportname = ?'
          #SQL Statement to create the row in  sports table
        query2 = 'INSERT INTO sports(sportname,time,hallnumber,note)\
                  VALUES(?,?,?,?)'
          #SQL Statement to create the row in sports table
        #temporal variables for sports table

        _sport_name = sport.get('sport name', None)
        _sport_time = sport.get('sport time', None)
        _number = sport.get('sporthall number', None)
        _note = sport.get('note', None)
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (sportname,)
        cur.execute(query1, pvalue)
        #No value expected (no other sport with that name expected)
        row = cur.fetchone()
        #If there is no sport add rows in sport
        if row is None:
            #Add the row in sports table
            # Execute the statement
            pvalue = (sportname, _sport_time, _number, _note)
            cur.execute(query2, pvalue)

            self.con.commit()
            #We do not do any comprobation and return the sportname
            return sportname
        else:
            return False


    #ACCESSING THE USER and USER_PROFILE tables
    def get_users(self):
        '''
        Extracts all users in the database.

        :return: list of Users of the database. Each user is a dictionary
            that contains two keys: ``nickname``(str) and ``registrationdate``
            (long representing UNIX timestamp). None is returned if the database
            has no users.

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the users
        query = 'SELECT users.*, users_profile.* FROM users, users_profile \
                 WHERE users.user_id = users_profile.user_id'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Process the response.
        users = []
        for row in rows:
            users.append(self._create_user_list_object(row))
        return users

    def get_user(self, nickname):
        '''
        Extracts all the information of a user.

        :param str nickname: The nickname of the user to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the user given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement for retrieving the user information
        query2 = 'SELECT users.*, users_profile.* FROM users, users_profile \
                  WHERE users.user_id = ? \
                  AND users_profile.user_id = users.user_id'
          #Variable to be used in the second query.
        user_id = None
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #Extract the user id
        row = cur.fetchone()
        if row is None:
            return None
        user_id = row["user_id"]
        # Execute the SQL Statement to retrieve the user invformation.
        # Create first the valuse
        pvalue = (user_id, )
        #execute the statement
        cur.execute(query2, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        return self._create_user_object(row)

    def delete_user(self, nickname, password):
        '''
        Remove all user information of the user with the nickname passed in as
        argument.

        :param str nickname: The nickname of the user to remove.

        :return: True if the user is deleted, False otherwise.

        '''
        #Create the SQL Statements
          #SQL Statement for deleting the user information
        query0 = 'select * from users where nickname = ?'
        query1 = 'DELETE FROM users WHERE nickname = ? And password = ?'
        query2 = 'DELETE FROM users_profile WHERE user_id = ?'
        #Activate foreign key support
        #self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (nickname,)
        print nickname
        print password
        cur.execute(query0, pvalue)
        row = cur.fetchone()
        if row is None:
            return False
        user_id = row["user_id"]
        print user_id
        pvalue = (nickname, password)
        cur.execute(query1, pvalue)
        pvalue = (user_id,)
        cur.execute(query2, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def modify_user(self, nickname, user):
        '''
        Modify the information of a user.

        :param str nickname: The nickname of the user to modify
        :param dict user: a dictionary with the information to be modified. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {'public_profile':{'registrationdate':,'signature':'',
                                       'avatar':''},
                    'restricted_profile':{'firstname':'','lastname':'',
                                          'email':'', 'website':'','mobile':'',
                                          'skype':'','age':'','residence':'',
                                          'gender':'', 'picture':''}
                    }

                where:

                * ``registrationdate``: UNIX timestamp when the user registered
                    in the system (long integer)
                * ``signature``: text chosen by the user for signature
                * ``avatar``: name of the image file used as avatar
                * ``firstanme``: given name of the user
                * ``lastname``: family name of the user
                * ``email``: current email of the user.
                * ``website``: url with the user's personal page. Can be None
                * ``mobile``: string showing the user's phone number. Can be
                    None.
                * ``skype``: user's nickname in skype. Can be None.
                * ``residence``: complete user's home address.
                * ``picture``: file which contains an image of the user.
                * ``gender``: User's gender ('male' or 'female').
                * ``age``: integer containing the age of the user.

            Note that all values are string if they are not otherwise indicated.

        :return: the nickname of the modified user or None if the
            ``nickname`` passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
                #Create the SQL Statements
           #SQL Statement for extracting the userid given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement to update the user_profile table
        query2 = 'UPDATE users_profile SET firstname = ?,lastname = ?, \
                                           email = ?,website = ?, \
                                           picture = ?,mobile = ?, \
                                           skype = ?,age = ?,residence = ?, \
                                           gender = ?,signature = ?,avatar = ?\
                                           WHERE user_id = ?'
        #temporal variables
        user_id = None
        p_profile = user['public_profile']
        r_profile = user['restricted_profile']
        print p_profile
        print r_profile
        _signature = p_profile.get('signature', None)
        print _signature
        _avatar = p_profile.get('avatar', None)
        print _avatar
        _firstname = r_profile.get('firstname', None)
        print _firstname
        _lastname = r_profile.get('lastname', None)
        print _lastname
        _email = r_profile.get('email', None)
        _website = r_profile.get('website', None)
        '''_picture = r_profile.get('picture', None)
        _mobile = r_profile.get('mobile', None)
        _skype = r_profile.get('skype', None)
        _age = r_profile.get('age', None)
        _residence = r_profile.get('residence', None)'''
        _gender = r_profile.get('gender', None)
        _picture = None
        _mobile = None
        _skype = None
        _age = None
        _residence = None
        _signature = p_profile.get('signature', None)
        _avatar = p_profile.get('avatar', None)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return None
        else:
            user_id = row["user_id"]
            #execute the main statement
            pvalue = (_firstname, _lastname, _email, _website, _picture,
                      _mobile, _skype, _age, _residence, _gender,
                      _signature, _avatar, user_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that I have modified the user
            if cur.rowcount < 1:
                return None
            return nickname


    def append_user(self, nickname, user):
        '''
        Create a new user in the database.

        :param str nickname: The nickname of the user to modify
        :param dict user: a dictionary with the information to be modified. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {'public_profile':{'registrationdate':,'signature':'',
                                       'avatar':''},
                    'restricted_profile':{'firstname':'','lastname':'',
                                          'email':'', 'website':'','mobile':'',
                                          'skype':'','age':'','residence':'',
                                          'gender':'', 'picture':''}
                    }

                where:

                * ``registrationdate``: UNIX timestamp when the user registered
                    in the system (long integer)
                * ``signature``: text chosen by the user for signature
                * ``avatar``: name of the image file used as avatar
                * ``firstanme``: given name of the user
                * ``lastname``: family name of the user
                * ``email``: current email of the user.
                * ``website``: url with the user's personal page. Can be None
                * ``mobile``: string showing the user's phone number. Can be
                    None.
                * ``skype``: user's nickname in skype. Can be None.
                * ``residence``: complete user's home address.
                * ``picture``: file which contains an image of the user.
                * ``gender``: User's gender ('male' or 'female').
                * ``age``: integer containing the age of the user.

            Note that all values are string if they are not otherwise indicated.

        :return: the nickname of the modified user or None if the
            ``nickname`` passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
        #Create the SQL Statements
          #SQL Statement for extracting the userid given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement to create the row in  users table
        query2 = 'INSERT INTO users(nickname,password,regDate,lastLogin,timesviewed,userType)\
                  VALUES(?,?,?,?,?,?)'
          #SQL Statement to create the row in user_profile table
        query3 = 'INSERT INTO users_profile (firstname,lastname, \
                                             email,website, \
                                             picture,mobile, \
                                             skype,age,residence, \
                                             gender,signature,avatar)\
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?)'
        
        #temporal variables for user table
        #timestamp will be used for lastlogin and regDate.
        timestamp = time.mktime(datetime.now().timetuple())
        timesviewed = 0
        #temporal variables for user profiles
        #p_profile is for user,r_profile is for user_profile
        p_profile = user['public_profile']
        r_profile = user['restricted_profile']
        print p_profile
        print r_profile
        _password = p_profile.get('password')
        print _password
        _regDate = p_profile.get('regDate')
        print _regDate
        _signature = p_profile.get('signature', None)
        print _signature
        _avatar = p_profile.get('avatar', None)
        print _avatar
        _userType = p_profile.get('userType', None)
        print _userType
        _firstname = r_profile.get('firstname', None)
        print _firstname
        _lastname = r_profile.get('lastname', None)
        print _lastname
        _email = r_profile.get('email', None)
        _website = r_profile.get('website', None)
        '''_picture = r_profile.get('picture', None)
        _mobile = r_profile.get('mobile', None)
        _skype = r_profile.get('skype', None)
        _age = r_profile.get('age', None)
        _residence = r_profile.get('residence', None)'''
        _birthday = r_profile.get('birthday', None)
        _gender = r_profile.get('gender', None)
        _picture = None
        _mobile = None
        _skype = None
        _age = None
        _residence = None
        #Activate foreign key support
        #self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #No value expected (no other user with that nickname expected)
        row = cur.fetchone()
        #If there is no user add rows in user and user profile
        if row is None:
            #Add the row in users table
            # Execute the statement
            pvalue = (nickname, _password, _regDate, timestamp, timesviewed,_userType)
            cur.execute(query2, pvalue)
            #Extrat the rowid => user-id
            lid = cur.lastrowid
            #Add the row in users_profile table
            # Execute the statement
            pvalue = (_firstname, _lastname, _email, _website,
                      _picture, _mobile, _skype, _age, _residence, _gender,
                      _signature, _avatar)
            cur.execute(query3, pvalue)
            self.con.commit()
            #We do not do any comprobation and return the nickname
            return nickname
        else:
            return None

    # UTILS

    def get_user_id(self, nickname):
        '''
        Get the key of the database row which contains the user with the given
        nickname.

        :param str nickname: The nickname of the user to search.
        :return: the database attribute user_id or None if ``nickname`` does
            not exit.
        :rtype: str

        '''

        '''
        TASK5 TODO :
        * Implement this method.
        HINTS:
          * Check the method get_message as an example.
          * The value to return is a string and not a dictionary
          * You can access the columns of a database row in the same way as
            in a python dictionary: row [attribute] (Check the exercises slides
            for more information)
          * There is only one possible user_id associated to a nickname
          * HOW TO TEST: Use the database_api_tests_user. The following tests
            must pass without failure or error:
                * test_get_user_id
                * test_get_user_id_unknown_user
        '''
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        
        query = 'SELECT user_id from users WHERE nickname = ?'
        pvalue = (nickname,)
        cur.execute(query,pvalue)
        self.con.commit()
        row = cur.fetchone()
        if row is None:
            return None
        return row['user_id']

    def contains_user(self, nickname):
        '''
        :return: True if the user is in the database. False otherwise
        '''
        return self.get_user_id(nickname) is not None

    def login(self, nickname, password):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        stmnt = 'select * from users where nickname=? and password=?'
        pvalue = (nickname,password)
        cur.execute(stmnt, pvalue)
        row = cur.fetchone()
        if row is None:
            return False
        else:
			return row