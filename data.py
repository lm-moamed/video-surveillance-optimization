import sqlite3
from pathlib import Path

def create_database(database_file):
    # Check if the database file already exists
    if not Path(database_file).is_file():
        print('creating the DataBase')
        # Create a connection to the database (this will create the file if it doesn't exist)
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        # Create the 'users' table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                phone_number TEXT NOT NULL,
                foldername TEXT NOT NULL
            );
        ''')

        # Create the 'streams' table
        cursor.execute('''
            CREATE TABLE streams (
                id INTEGER PRIMARY KEY,
                url TEXT NOT NULL,
                userid INTEGER NOT NULL,
                foldername TEXT NOT NULL,
                status TEXT NOT NULL,
                processing INTEGER  DEFAULT 0,
                FOREIGN KEY (userid) REFERENCES users(id)
            );
        ''')

        # Create the 'records' table
        cursor.execute('''
            CREATE TABLE records (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                streamid INTEGER NOT NULL,
                recorddate DATE NOT NULL,
                FOREIGN KEY (streamid) REFERENCES streams(id)
            );
        ''')

        # Commit the changes and close the connection
        conn.commit()
        print("database created")
        conn.close()


class DatabaseManp:
    def __init__(self, database_file):
        self.conn = sqlite3.connect(database_file)


    def register_udfs(self,func):
        # Get the function object by its name
        func_impl = getattr(self, func, None)
        if func_impl is not None:
            # Register the function with SQLite
            self.conn.create_function(func, func_impl.__code__.co_argcount, func_impl)

    def insert_user(self, phone_number,foldername):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (phone_number,foldername) VALUES (?,?)", (phone_number,foldername))
        self.conn.commit()

    def insert_stream(self, url, userid, foldername, status):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO streams (url, userid, foldername, status) VALUES (?, ?, ?, ?)", (url, userid, foldername, status))
        self.conn.commit()

    def insert_record(self, path, streamid, recorddate):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO records (path, streamid, recorddate) VALUES (?, ?, ?)", (path, streamid, recorddate))
        self.conn.commit()

    def update_user_phone(self, user_id, new_phone_number):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET phone_number = ? WHERE id = ?", (new_phone_number, user_id))
        self.conn.commit()

    def update_stream_status(self, stream_id, new_status):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE streams SET status = ? WHERE id = ?", (new_status, stream_id))
        self.conn.commit()

    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id))
        self.conn.commit()

    def delete_stream(self, stream_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM streams WHERE id = ?", (stream_id))
        self.conn.commit()

    def get_all_streams(self):
        cursor = self.conn.cursor()
        cursor.execute("select * from streams")
        streams = cursor.fetchall()
        return streams

    def get_actif_streams(self):
        cursor = self.conn.cursor()
        cursor.execute("select id from streams where status =\'actif\'")
        streams = cursor.fetchall()
        return streams

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return users

    def get_stream_by_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM streams WHERE userid = ?", (user_id))
        streams = cursor.fetchall()
        return streams

    def get_info_by_stream_id(self, stream_id):

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.foldername AS user_foldername, s.foldername AS stream_foldername, s.url, s.status
            FROM streams s
            INNER JOIN users u ON s.userid = u.id
            WHERE s.id = ?
        ''', str(stream_id))

        return cursor.fetchone()

    def get_new_streams(self):
        cursor = self.conn.cursor()
        cursor.execute('''
                       SELECT id
                       FROM streams
                       WHERE processing = 0
                   ''')
        return  cursor.fetchall()



    def set_stream_processing(self, stream_id, processing):
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE streams
            SET processing = ?
            WHERE id = ?
        ''', (processing, str(stream_id)))

        # Commit the changes and close the connection
        self.conn.commit()

    def close_connection(self):
        self.conn.close()