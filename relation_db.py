from sqlite3 import connect

'''
Contact: Agosh Saini (as7saini@uwaterloo.ca)
---------
This class handles the database generation for data management for the experiments being conducted
'''


class relation_db:

    # initializing class
    def __init__(self, db_name, db_dir="database"):
        self.db_dir = db_dir
        self.db_name = db_name

    # connect to a db, if db does not exist, creat db
    def create_db(self, name=None, db_dir_update=None):
        # update dir if needed
        if db_dir_update is not None:
            self.db_dir = db_dir_update

        # update name if needed
        if name is not None:
            self.db_name = name
        print(self.db_dir + '\\' + self.db_name)
        # create db
        connection = connect(self.db_dir + '\\' + self.db_name)
        # exit
        connection.commit()
        connection.close()

        return self.db_dir, self.db_name

    # creating the index db
    def create_table(self, db_name=None, db_dir=None):

        # update dir if needed
        if db_dir is not None:
            self.db_dir = db_dir

        # update name if needed
        if db_name is not None:
            self.db_name = db_name

        # connect to index db and create cursor for communication
        connection = connect(self.db_dir + '\\' + self.db_name)
        cursor = connection.cursor()

        # create the DB
        cursor.execute(
            """ 
           CREATE TABLE IF NOT EXISTS formatted_data (
               id INTEGER PRIMARY KEY,
               filename TEXT,
               Analyte TEXT,
               ppm TEXT,
               on_cycle TEXT,
               off_cycle TEXT
           ); 
           """
        )

        # exit
        connection.commit()
        connection.close()

    def add_to_table(self, filename, analyte, ppm, ON, OFF):

        # connect to index db and create cursor for communication
        connection = connect(self.db_dir + '\\' + self.db_name)
        cursor = connection.cursor()

        # Insert data into the index table
        cursor.execute(""" 
            INSERT INTO formatted_data
            (filename, analyte, ppm, on_cycle, off_cycle) 
            VALUES (?, ?, ?, ?, ?)
            """,
                       (filename, analyte, ppm, ON, OFF))

        # exit
        connection.commit()
        connection.close()


