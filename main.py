import configparser
import os
import time
import threading
import processing
import data


def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    base_folder = config.get('Main', 'base_folder')
    database_name = config.get('Main', 'database_name')

    return base_folder, database_name

def process_new_streams(database_file,basePath):
    print('Start processing')
    while True:
        DBconn = data.DatabaseManp(database_file)
        new_streams =DBconn.get_new_streams()
        mask_path=None
        p_fps=5
        for stream_id, in new_streams:
            thread = threading.Thread(target=processing.process, args=( stream_id, database_file, basePath, mask_path, p_fps))
            thread.start()
            print('processing new stream : ',stream_id)
            DBconn.set_stream_processing(stream_id, '1')
        DBconn.close_connection()

        time.sleep(60)


def preparation(database_file):
    DBconn = data.DatabaseManp(database_file)
    actf_strms = DBconn.get_actif_streams()
    for stream in actf_strms:
        print('actif stream detected : ',stream[0])
        DBconn.set_stream_processing(stream[0], 0)
    DBconn.close_connection()


def main():
    print('Start preparations')
    config_file = 'config.ini'
    base_folder, database_name = read_config(config_file)

    # Create the base folder if it doesn't exist
    processing.create_missing_folders(base_folder)

    # Create the database if it doesn't exist
    database_file = os.path.join(base_folder, database_name)
    data.create_database(database_file)

    preparation(database_file)
    print('Preparations done')
    # Start processing new streams
    process_new_streams(database_file,base_folder)
if __name__ == '__main__':
    main()