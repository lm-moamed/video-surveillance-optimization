import os
from datetime import datetime
import cv2
import time
from data import DatabaseManp

def pro_step(fps, p_fps):
    if p_fps != 0:
        return int(fps / p_fps)


def frame_diff(p_frame, c_frame, thrh=100):
    prc_frame = cv2.absdiff(p_frame, c_frame)
    _, prc_frame = cv2.threshold(prc_frame, thrh, 255, cv2.THRESH_BINARY)
    return prc_frame
def basic_process(cap, mask,frame_skip, fps,out, tperd=1):
    fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
    _, prev_frame = cap.read()
    if mask:
        prev_frame = cv2.bitwise_and(prev_frame, mask)
    prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    #prev_frame = fgbg.apply(prev_frame)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    count = 0
    total_frames = int(int(fps) * 3600 * tperd)
    while count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if count % frame_skip != 0:
            count += 1
            continue
        frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if mask:
            frame2 = cv2.bitwise_and(frame2, mask)
        #frame2 = fgbg.apply(frame2)
        prc_frame = frame_diff(prev_frame, frame2)

        prc_frame = cv2.morphologyEx(prc_frame, cv2.MORPH_OPEN, kernel)
        prc_frame = cv2.morphologyEx(prc_frame, cv2.MORPH_CLOSE, kernel)

        contours, hierarchy = cv2.findContours(prc_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected = False
        for contour in contours:
            _, _, w, h = cv2.boundingRect(contour)
            if w * h > 2000:
                detected = True
                break

        if detected:
            out.write(frame)
            #print('detected')

        count += 1
        prev_frame = frame2

    out.release()

def create_missing_folders(path):
    # Check if the directory exists, if not, create it
    if not os.path.exists(path):
        os.makedirs(path)

def get_data_by_strm(DBfile, strmID):
    data = DatabaseManp(DBfile)
    reslt = data.get_info_by_stream_id(int(strmID))
    if reslt:
        return reslt
    else:
        return None
def get_path_for_record(basePath, user_foldername, stream_foldername, strmID):
    current_date = datetime.now().strftime('%Y-%m-%d')
    base_path = os.path.join(basePath, user_foldername, stream_foldername, current_date)

    # Create the necessary folders if they don't exist
    create_missing_folders(base_path)

    record_filename = f'record_{strmID}_{datetime.now().strftime("%H%M%S")}.webm'
    record_path = os.path.join(base_path, record_filename)

    return record_path


def process(strmID, DBfile, basePath, mask_path=None, p_fps=0) :
    usid, fn, stream_label, rtsp_url,_,period = get_data_by_strm(DBfile,strmID)
    user_foldername = f"user_{usid}_{fn}"
    mask = None
    cap = cv2.VideoCapture(rtsp_url)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_skip = pro_step(fps, p_fps)
    if mask_path:
        mask = cv2.imread(mask_path)
    fourcc = cv2.VideoWriter_fourcc(*'VP90')
    while True:
        current_datetime = datetime.now()
        output_file = get_path_for_record(basePath,user_foldername,stream_label,strmID)
        out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height), isColor=True)
        basic_process(cap=cap, frame_skip=frame_skip, fps=fps, out=out, tperd=int(period), mask=None)
        DatabaseManp(DBfile).insert_record(output_file,strmID,current_datetime,usid)
        print("new record at ",output_file)
