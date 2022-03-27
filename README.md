Smart Cities Tutorial -
The concept of this tutorial is that we assume that we have a livestream video of cars entering the city we use (cars4.mp4)
to accomplish that and we use the (function detect_vehicle())  to detect the vehicle type from that video.The (function detect_vehicle())  
gets the type of vehicles from the haarcascade_car.xml,bus.xml and truck.xml(their data are not correct or verified they are just 
used as example for the tutorial).Then we assume the car stops at the toll station where the system takes a photo of the lisence plate,
we use the (test_plate.jpg) to  accomplish that and with (function get_plate()) we convert the license plate into a string.
We have created two tables in the database vehicles and city.So we insert the vehicles in the database and the vehicles in 
the "virtual city" so that we can begin charging the vehicles. To accomplish that we use (functions vehicle_entry_in_db(),vehicle_entry_in_city()).
When the vehicle leaves the city we use (fuction vehicle_exit_city()) and at the end of the day we can use the (function daily_report())  to see
the vehicles that enter/exit the city and their charges.

For this tutorial to work we will need to install
1) Python
2) Pytesseract - pip install pytesseract
3) OpenCV - pip install opencv-python
4) Mysql
