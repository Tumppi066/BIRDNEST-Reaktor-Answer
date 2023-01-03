import xml.etree.ElementTree as ET # For the drone data
import time 
import reaktorAPI
import os
from datetime import datetime
import math
import json # For the pilot data

apiUpdateRate = 2 # seconds
nestPosition = [250000, 250000] # millimeters (x,y) (250000 = 250m)
noFlyZoneRadius = 100000 # millimeters (100000 = 100m)
pilotStorageTime = 600 # seconds, how long the pilots are stored after their drones disappear



# Main drone class
class Drone:
    serialNumber = ""
    model = ""
    manufacturer = ""
    mac = ""
    ipv4 = ""
    ipv6 = ""
    firmware = ""
    positionX = ""
    positionY = ""
    altitude = ""
    lastSeen = ""
    closestPositionX = ""
    closestPositionY = ""

    # Set the drone's fields during initialization
    def __init__(self, serialNumber, model, manufacturer, mac, ipv4, ipv6, firmware, positionX, positionY, altitude, lastSeen, closestPositionX, closestPositionY):
        self.serialNumber = serialNumber
        self.model = model
        self.manufacturer = manufacturer
        self.mac = mac
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.firmware = firmware
        self.positionX = positionX
        self.positionY = positionY
        self.altitude = altitude
        self.lastSeen = lastSeen
        self.closestPositionX = closestPositionX
        self.closestPositionY = closestPositionY




# Main pilot class
class Pilot:
    name = ""
    phone = ""
    email = ""
    closestDistance = 0 # millimeters
    droneSerialNumber = "" # The serial number of the drone the pilot was controlling
    lastViolation = ""
    lastSeen = ""
    closestPositionX = ""
    closestPositionY = ""

    # Set the pilot's fields during initialization
    def __init__(self, name, phone, email, droneSerialNumber, lastViolation, lastSeen, closestPositionX, closestPositionY):
        self.name = name
        self.phone = phone
        self.email = email
        self.droneSerialNumber = droneSerialNumber
        self.lastViolation = lastViolation
        self.lastSeen = lastSeen
        self.closestPositionX = closestPositionX
        self.closestPositionY = closestPositionY
        




def LoadPilotDatabase(filename):
    # Load the database from a file
    data = open(filename, "r").readlines() # A for loop is technically faster for reading, but this is more readable
    data.pop(0) # Remove the first line (column names)

    pilots = []

    for line in data: # (for pilot in database)
        line = line.split(",")
        try:
            # Fields :          name,    phone,   email,   serial,lastVio...,lastSeen,close x, close y
            pilots.append(Pilot(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7]))
        except:
            pass

    return pilots


def LoadDroneDatabase(filename):
    # Load the database from a file
    data = open(filename, "r").readlines() # A for loop is faster for reading, but this is more readable
    data.pop(0) # Remove the first line (column names)

    drones = []

    for line in data: # (for drone in database)
        line = line.split(",")
        try:
            # Fields :          serial,  model,manufacturer, mac,   ipv4,    ipv6,   firmware, posX,    posY,   altitude, lastSeen, close x , close y
            drones.append(Drone(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10], line[11], line[12]))
        except:
            pass

    return drones






def WriteDroneDatabase(filename, database): # database means an array of Drone objects
    # Write the database to a file
    file = open(filename, "w")
    file.truncate(0) # Clear the file
    file.write("serialNumber,model,manufacturer,mac,ipv4,ipv6,firmware,positionX,positionY,altitude,lastSeen, closestPosition x, closestPosition y") # Write the header back

    # Convert the list of drones to a string
    databaseString = ""
    for drone in database:
        for field in drone.__dict__.values(): # Loop through the fields of the drone
            databaseString += str(field) + "," # And seperate them with commas
        databaseString += "\n"

    file.write("\n" + databaseString)


def WritePilotDatabase(filename, pilotDatabase): # pilotDatabase means an array of Pilot objects
    # Write the database to a file
    file = open(filename, "w")
    file.truncate(0) # Clear the file
    file.write("name,phone,email,droneSerialNumber,lastViolation,lastSeen,closestPosition x,closestPosition y") # Write the header back

    # Convert the list of pilots to a string
    databaseString = ""
    for pilot in pilotDatabase:
        for field in pilot.__dict__.values(): # Loop through the fields of the pilot
            databaseString += str(field) + "," # And seperate them with commas
        databaseString += "\n"

    file.write("\n" + databaseString)




# Will update a drones position in the database
# If the drone is not in the database, it will be added
#
# drone = an xml element containing the drone's data
# droneDatabase = an array of Drone objects
# timestamp = the current time (unix seconds)
def UpdateDroneInDatabase(drone, droneDatabase, timestamp): 
    # Parse the xml
    serial = drone[0].text
    model = drone[1].text
    manufacturer = drone[2].text
    mac = drone[3].text
    ipv4 = drone[4].text
    ipv6 = drone[5].text
    firmware = drone[6].text
    positionX = drone[7].text
    positionY = drone[8].text
    altitude = drone[9].text
    
    
    found = False
    for knownDrone in droneDatabase: # Loop through the drones in the database and check
        if knownDrone.serialNumber.upper() == serial.upper(): # if the drone is already in the database
            # If it is, then we update the fields
            knownDrone.positionX = positionX
            knownDrone.positionY = positionY
            knownDrone.altitude = altitude
            knownDrone.lastSeen = timestamp
            found = True


    if not found:
        # If the drone is not in the database, then we add it
        droneDatabase.append(Drone(serial, model, manufacturer, mac, ipv4, ipv6, firmware, positionX, positionY, altitude, timestamp, 1, 1)) # 1,1, is a placeholder for the closest position

    return droneDatabase


# Will update a pilot's position in the database
# If the pilot is not in the database, it will be added
# 
# pilotDatabase = an array of Pilot objects
# timestamp = the current time (unix seconds)
# drone = a Drone object
# distance = the current distance of the drone to the nest
def UpdatePilotInDatabase(pilotDatabase, timestamp, drone, distance):

    found = False
    for knownPilot in pilotDatabase: # Loop through the pilots in the database and check
        if knownPilot.droneSerialNumber == drone.serialNumber: # if the pilot is already in the database
            # If it is, then we update the fields
            knownPilot.lastSeen = timestamp
            if (distance < noFlyZoneRadius):
                knownPilot.lastViolation = timestamp
            knownPilot.closestPositionX = drone.closestPositionX
            knownPilot.closestPositionY = drone.closestPositionY
            found = True
    
    if not found:
        # If the pilot is not in the database, then we add it
        data = reaktorAPI.GetPilotData(drone.serialNumber) # Get new data from the API
        
        try: data = json.loads(data) # Convert the data to json for easy manipulation
        except:
            data = { # The pilot is unknown
                "firstName": "Unknown",
                "lastName": "Unknown",
                "phoneNumber": "Unknown",
                "email": "Unknown"
            }
        
        # Add the pilot to the database
        pilotDatabase.append(Pilot(data["firstName"] + " " + data["lastName"], data["phoneNumber"], data["email"], drone.serialNumber, timestamp, timestamp, drone.closestPositionX, drone.closestPositionY))


    return pilotDatabase





def CalculateDistanceToNest(position):
    # Calculate the distance to the nest
    # distance = sqrt((x1 - x2)^2 + (y1 - y2)^2)
    x1 = float(position[0])
    x2 = nestPosition[0]
    y1 = float(position[1])
    y2 = nestPosition[1]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)





while True:
    startTime = time.time() # This is used to later get an accurate 2s update rate


    """
    Update the drone database
    """

    data = reaktorAPI.GetDroneData() # Get new data from the API
    database = LoadDroneDatabase("Database/drones.csv") # Load the drone database

    data = ET.fromstring(data) # Convert the data to an XML tree for easy manipulation
    
    captureTime = data[1].attrib["snapshotTimestamp"] # Extract the timestamp
    captureTime = datetime.strptime(captureTime, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() # and then convert it to unixtime

    for drone in data[1]: # Update all the drones in the database
        database = UpdateDroneInDatabase(drone, database, captureTime)

    # Clear drones no longer being tracked
    for drone in database:
        if drone.lastSeen != captureTime:
            database.remove(drone)

    WriteDroneDatabase("Database/drones.csv", database) # Then write the changes
    LoadDroneDatabase("Database/drones.csv") # And reload the database for no fly zone checking

    """
    Check for drones violating the no-fly zone
    """

    os.system("cls") # Clear the console
    print("\033[92m" + "Reaktor Drone Tracker" + "\033[0m")
    print("\033[92m" + "Backend running..." + "\033[0m")

    pilotDatabase = LoadPilotDatabase("Database/pilots.csv") # Load the pilot database
    
    for drone in database: # Loop through all the drones in the database
        
        # Update their closest positions
        distance = CalculateDistanceToNest([drone.positionX, drone.positionY])
        closestDistance = CalculateDistanceToNest([drone.closestPositionX, drone.closestPositionY])
        if (distance < closestDistance):
            drone.closestPositionX = drone.positionX
            drone.closestPositionY = drone.positionY
            closestDistance = distance

        if closestDistance < noFlyZoneRadius: # and check if they have been within the no-fly zone
            # If they have, then we update/add the pilot to the database
            print(drone.serialNumber + " : " + str(round(distance/1000,2)) + "m - has violated!")
            pilotDatabase = UpdatePilotInDatabase(pilotDatabase, captureTime, drone, distance) # Update the pilot database

        else:
            # If they are not, then we just print the distance
            print(drone.serialNumber + " : " + str(round(distance/1000,2)) + "m")

    # Clear pilots no longer being tracked and exceeding the storage time
    for pilot in pilotDatabase:
        if round(float(pilot.lastSeen)) < round(float(captureTime)) - int(pilotStorageTime):
            pilotDatabase.remove(pilot)

    # Then write the changes
    WriteDroneDatabase("Database/drones.csv", database) 
    WritePilotDatabase("Database/pilots.csv", pilotDatabase)
    
    
    # Match the API update rate
    print("Compute time: " + str(round(time.time() - startTime, 3)) + "s")
    while time.time() - startTime < apiUpdateRate:
        print("\033[93m" + "Waiting " + str(round(apiUpdateRate - (time.time() - startTime), 1)) + "s" + "\033[0m", end="\r")
    #time.sleep(apiUpdateRate - (time.time() - startTime))