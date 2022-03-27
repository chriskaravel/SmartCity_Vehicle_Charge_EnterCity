from datetime import datetime
from pytesseract import pytesseract 
import cv2
import imutils
import mysql.connector
from getpass import getpass
from mysql.connector import connect, Error
from operator import mul
import csv
import os


def get_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def city_cost(vtype,time_in,time_out):
    s1 = time_in
    s2 = time_out
    FMT = '%H:%M:%S'
    tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
    my_time = str(tdelta)
    factors = (60, 1, 1/60)
    time = sum(i*j for i, j in zip(map(int, my_time.split(':')), factors))
    t2 = sum(map(mul, map(int, my_time.split(':')), factors))
    time = int(time)
    if vtype == 'car':
        if time < 30:
            cost = 0
        elif time >= 30 and time < 60:
            cost = 3
        elif time >= 60 and time < 120:
            cost = 5
        elif time >= 120 and time <= 240:
            cost = 7
        else:
            if int((time-240)/60) < 1:
                time = 1 
                cost = 7 + time
            else:
                time = int((time-240)/60)
                cost = 7 + time +1
    elif vtype == 'truck':
        if time < 30:
            cost = 0
        elif time >= 30 and time < 60:
            cost = 5
        elif time >= 60 and time < 120:
            cost = 9
        elif time >= 120 and time <= 240:
            cost = 11
        else:
            if int((time-240)/60) < 1:
                time = 1 
                cost = 9 + (time * 2)
            else:
                time = int((time-240)/60)
                cost = 9 + (time *2) +2
    elif vtype =='bus':
        if time < 30:
            cost = 0
        elif time >= 30 and time < 60:
            cost = 7
        elif time >= 60 and time < 120:
            cost = 16
        elif time >= 120 and time <= 240:
            cost = 19
        else:
            if int((time-240)/60) < 1:
                time = 1 
                cost = 19 + (time * 3)
            else:
                time = int((time-240)/60)
                cost = 19 + (time *3) +3
    else:
        return ('error')
    return cost

def detect_vehicle():
    cap = cv2.VideoCapture('cars.mp4')  #Path to footage
    try:
        # creating a folder named data
        if not os.path.exists('data'):
            os.makedirs('data')
        # if not created then raise error
    except OSError:
        print('Error: Creating directory of data')

    car_cascade = cv2.CascadeClassifier('haarcascade_car.xml')  #Path to cars.xml
    bus_cascade = cv2.CascadeClassifier('bus.xml')
    truck_cascade = cv2.CascadeClassifier('truck.xml')
    while True:
        ret, img = cap.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        cars=car_cascade.detectMultiScale(gray,1.16,2)
        buses=bus_cascade.detectMultiScale(gray,2,2)
        trucks=bus_cascade.detectMultiScale(gray,1.8,2)
        #Drawing rectangles on detected cars
        currentframe =1
        for (x,y,w,h) in cars:
            cv2.rectangle(img,(x,y),(x+w,y+h),(225,0,0),2)
            ret, frame = cap.read()
            name = './data/car' + str(currentframe) + '.jpg'
            # writing the extracted images
            cv2.imwrite(name, frame)
            return ('car')
        for (x,y,w,h) in buses:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,100,0),2)
            ret, frame = cap.read()
            name = './data/car' + str(currentframe) + '.jpg'
            # writing the extracted images
            cv2.imwrite(name, frame)
            return ('bus')
        for (x,y,w,h) in trucks:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,110),2)
            ret, frame = cap.read()
            name = './data/car' + str(currentframe) + '.jpg'
            # writing the extracted images
            cv2.imwrite(name, frame)
            return ('truck')
        cv2.imshow('img',img) #Shows the frame
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def get_plate():
    path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.tesseract_cmd = path_to_tesseract
    #Taking in our image input and resizing its width to 300 pixels
    image = cv2.imread('test_plate.jpg')
    image = imutils.resize(image, width=300 )
    #Converting the input image to greyscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #Reducing the noise in the greyscale image
    gray_image = cv2.bilateralFilter(gray_image, 11, 17, 17) 
    #Detecting the edges of the smoothened image
    edged = cv2.Canny(gray_image, 30, 200) 
    #Finding the contours from the edged image
    cnts,new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    image1=image.copy()
    cv2.drawContours(image1,cnts,-1,(0,255,0),3)
    #Sorting the identified contours
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True) [:30]
    screenCnt = None
    image2 = image.copy()
    cv2.drawContours(image2,cnts,-1,(0,255,0),3)
    #Finding the contour with four sides
    i=7
    for c in cnts:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * perimeter, True)
        if len(approx) == 4: 
            screenCnt = approx
            #Cropping the rectangular part identified as license plate
            x,y,w,h = cv2.boundingRect(c) 
            new_img=image[y:y+h,x:x+w]
            cv2.imwrite('./'+str('license_plate')+'.png',new_img)
            i+=1
        break
    #Drawing the selected contour on the original image
    cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 3)
    #Extracting text from the image of the cropped license plate
    Cropped_loc = './license_plate.png'
    #cv2.imshow("cropped", cv2.imread(Cropped_loc))
    plate = pytesseract.image_to_string(Cropped_loc, lang='eng')
    #print("Number plate is:", plate)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return str(plate)

def vehicle_entry_in_db():
    vplate = get_plate()
    plate = str(vplate.rstrip())
    vtype = detect_vehicle()
    insert_vehicle_query = ("INSERT INTO ots.vehicle "
                "(vtype,plate) "
                "VALUES (%s, %s)")
    data = (vtype,plate)
    with connection.cursor() as cursor: 
        cursor.execute(insert_vehicle_query,data)
        records = cursor.fetchall()
        vid=0
        for row in records:
            print("Id = ", row[0], )
            print("type = ", row[1])
        connection.commit()

def vehicle_entry_in_city():
    vplate = get_plate()
    plate = str(vplate.rstrip())
    vtype = detect_vehicle()
    current_time=get_time()
    plate = (plate,)
    select_vehicle_query = "SELECT * FROM ots.vehicle where plate = %s"
    insert_city_query = ("INSERT INTO ots.city "
                "(time_in,time_out,vid,cost) "
                "VALUES (%s, %s,%s,%s)")
    data = (vtype,plate)
    with connection.cursor() as cursor: 
        cursor.execute(select_vehicle_query,plate)
        records = cursor.fetchall()
        vid=0
        for row in records:
            vid =row[0]

        data2 = (current_time,0,vid,0)

        cursor.execute(insert_city_query,data2)
        connection.commit()

def vehicle_exit_city():
    vplate = get_plate()
    plate = str(vplate.rstrip())
    cur_time=get_time()
    plate = (plate,)
    select_vehicle_query = "SELECT * FROM ots.vehicle where plate = %s"
    select_city_query = "SELECT * FROM ots.city where vid = %s"
    update_city_query ="UPDATE ots.city SET time_out = %s,cost= %s WHERE vid = %s"
    with connection.cursor() as cursor: 
        cursor.execute(select_vehicle_query,plate)
        records = cursor.fetchall()
        for row in records:
            vid= row[0]
            vtype =row[1]
            vplate = row[2]
        cursor.execute(select_city_query,(vid,))
        records = cursor.fetchall()       
        for row in records:
            cid= row[0]
            time_in =row[1]
            time_out = row[2]
            vid= row[3]
            cost =row[4]
        vcost=city_cost(vtype,str(time_in),str(cur_time))
        val = (cur_time, vcost,vid)
        cursor.execute(update_city_query,val)
        connection.commit()

def daily_report():
    select_city_query = "SELECT * FROM ots.city "
    with connection.cursor() as cursor: 
        cursor.execute(select_city_query)
        records = cursor.fetchall()
        header = ['cid', 'time_in', 'time_out', 'vid','cost']  
        with open("city_vehicles.csv", "w", newline='') as csv_file:  # Python 3 version    
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(header) # write headers
            csv_writer.writerows(records)
        connection.commit()

try:
    with connect(
        host="localhost",
        user="root",
        password="1234",
        database="ots",
    ) as connection:
        print(connection)
        cursor = connection.cursor()
        vehicle_entry_in_db()
        vehicle_entry_in_city()
        vehicle_exit_city()
        daily_report()

except Error as e:
    print(e)
