import configparser
import os

from data import DatabaseManp
import inquirer
from inquirer.themes import GreenPassion

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    base_folder = config.get('Main', 'base_folder')
    database_name = config.get('Main', 'database_name')

    return base_folder, database_name

def main():
    base_folder, database_file = read_config("config.ini")
    database_file = os.path.join(base_folder, database_file)
    DBconn = DatabaseManp(database_file)

    while True:
        questions = [
            inquirer.List('action',
                          message='Choose an option:',
                          choices=['Add a new user', 'Add a new stream', 'Set Processing', 'Exit']
                          )
        ]

        answer = inquirer.prompt(questions)

        if answer['action'] == 'Add a new user':
            questions = [
                inquirer.Text('phone_number', message='Enter the phone number of the user:'),
                inquirer.Text('foldername', message='Enter the foldername for the user:')
            ]

            user_answer = inquirer.prompt(questions)
            phone_number = user_answer['phone_number']
            user_foldername = user_answer['foldername']
            DBconn.insert_user( phone_number, user_foldername)
            print("User added successfully!\n")

        elif answer['action'] == 'Add a new stream':
            questions = [
                inquirer.Text('url', message='Enter the URL of the stream:'),
                inquirer.Text('userid', message='Enter the user ID of the stream\'s owner:'),
                inquirer.Text('foldername', message='Enter the foldername for the stream:'),
                inquirer.Text('status', message='Enter the status of the stream:')
            ]

            stream_answer = inquirer.prompt(questions)
            url = stream_answer['url']
            userid = int(stream_answer['userid'])  # Convert input to int
            stream_foldername = stream_answer['foldername']
            stream_status = stream_answer['status']
            DBconn.insert_stream(url, userid, stream_foldername, stream_status)
            print("Stream added successfully!\n")

        elif answer['action'] == 'Set Processing':
            questions = [
                inquirer.Text('streamid', message='Enter the  ID of the stream:'),
                inquirer.Text('processing', message='Enter 1 if processing or 0 if not:')
            ]
            stream_answer = inquirer.prompt(questions)
            streamid = stream_answer['streamid']
            processing = int(stream_answer['processing'])
            DBconn.set_stream_processing(streamid, processing)

        elif answer['action'] == 'Exit':
            print("Exiting the program.")
            break

if __name__ == "__main__":
    main()