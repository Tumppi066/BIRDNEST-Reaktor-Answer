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
    closestPosition = [0,0]

    # Set the drone's fields during initialization
    def __init__(self, serialNumber, model, manufacturer, mac, ipv4, ipv6, firmware, positionX, positionY, altitude, lastSeen, closestPosition):
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
        self.closestPosition = closestPosition

# Main pilot class
class Pilot:
    name = ""
    phone = ""
    email = ""
    closestDistance = 0 # millimeters
    droneSerialNumber = "" # The serial number of the drone the pilot was controlling
    lastSeen = ""
    closestPosition = []

    # Set the pilot's fields during initialization
    def __init__(self, name, phone, email, droneSerialNumber, lastSeen, closestPosition):
        self.name = name
        self.phone = phone
        self.email = email
        self.droneSerialNumber = droneSerialNumber
        self.lastSeen = lastSeen
        self.closestPosition = closestPosition

def LoadPilotDatabase(filename):
    # Load the database from a file
    data = open(filename, "r").readlines() # A for loop is faster for reading, but this is more readable
    data.pop(0) # Remove the first line (column names)

    pilots = []

    for line in data:
        line = line.split(",")
        try:
            # Fields :          name,    phone,   email,   serial, lastSeen, closestPosition
            pilots.append(Pilot(line[0], line[1], line[2], line[3], line[4], line[5]))
        except:
            return []

    return pilots

def LoadDroneDatabase(filename):
    # Load the database from a file
    data = open(filename, "r").readlines() # A for loop is faster for reading, but this is more readable
    data.pop(0) # Remove the first line (column names)

    drones = []

    for line in data:
        line = line.split(",")
        try:
            # Fields :          serial,  model,manufacturer, mac,   ipv4,    ipv6,   firmware, posX,    posY,   altitude, lastSeen
            drones.append(Drone(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]))
        except:
            return []

    return drones


def WriteDroneDatabase(filename, database):
    # Write the database to a file
    file = open(filename, "w")
    file.truncate(0) # Clear the file
    file.write("serialNumber,model,manufacturer,mac,ipv4,ipv6,firmware,positionX,positionY,altitude,lastSeen") # Write the header back

    # Convert the list of drones to a string
    databaseString = ""
    for drone in database:
        for field in drone.__dict__.values(): # Loop through the fields of the drone
            databaseString += str(field) + ","
        databaseString += "\n"

    file.write("\n" + databaseString)

def WritePilotDatabase(filename, pilotDatabase):
    # Write the database to a file
    file = open(filename, "w")
    file.truncate(0) # Clear the file
    file.write("name,phone,email,droneSerialNumber,lastSeen") # Write the header back

    # Convert the list of pilots to a string
    databaseString = ""
    for pilot in pilotDatabase:
        for field in pilot.__dict__.values(): # Loop through the fields of the pilot
            databaseString += str(field) + ","
        databaseString += "\n"

    file.write("\n" + databaseString)

def UpdateDroneInDatabase(drone, database, timestamp):
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
    for knownDrone in database:
        if knownDrone.serialNumber == serial:
            knownDrone.positionX = positionX
            knownDrone.positionY = positionY
            knownDrone.altitude = altitude
            knownDrone.lastSeen = timestamp
            found = True
    
    if not found:
        database.append(Drone(serial, model, manufacturer, mac, ipv4, ipv6, firmware, positionX, positionY, altitude, captureTime, [1,1]))

    # Clear drones no longer being tracked
    for drone in database:
        if drone.lastSeen != timestamp:
            database.remove(drone)

    return database

def UpdatePilotInDatabase(pilotDatabase, timestamp, drone):

    found = False
    for knownPilot in pilotDatabase:
        if knownPilot.droneSerialNumber == drone.serialNumber:
            knownPilot.lastSeen = timestamp
            found = True
    
    if not found:
        data = reaktorAPI.GetPilotData(drone.serialNumber) # Get new data from the API
        data = json.loads(data) # Convert the data to json for easy manipulation
        pilotDatabase.append(Pilot(data["firstName"] + "" + data["lastName"], data["phoneNumber"], data["email"], drone.serialNumber, timestamp, drone.closestPosition))

    # Clear pilots no longer being tracked and exceeding the storage time
    for pilot in pilotDatabase:
        if pilot.lastSeen > timestamp - pilotStorageTime:
            pilotDatabase.remove(pilot)

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

    data = reaktorAPI.GetNewData() # Get new data from the API
    database = LoadDroneDatabase("Database/drones.csv") # Load the drone database

    data = ET.fromstring(data) # Convert the data to an XML tree for easy manipulation
    
    captureTime = data[1].attrib["snapshotTimestamp"] # Extract the timestamp
    captureTime = datetime.strptime(captureTime, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() # and then convert it to unixtime

    for drone in data[1]: # Update all the drones in the database
        database = UpdateDroneInDatabase(drone, database, captureTime)

    WriteDroneDatabase("Database/drones.csv", database) # Then write the changes


    """
    Check for drones violating the no-fly zone
    """

    os.system("cls") # Clear the console
    pilotDatabase = LoadPilotDatabase("Database/pilots.csv") # Load the pilot database
    for drone in database:
        distance = CalculateDistanceToNest([drone.positionX, drone.positionY])
        if distance < CalculateDistanceToNest(drone.closestPosition):
            drone.closestPosition = [drone.positionX, drone.positionY]

        if distance < noFlyZoneRadius:
            print(drone.serialNumber + " : " + str(round(distance/1000,2)) + "m - violation!")
            pilotDatabase = UpdatePilotInDatabase(pilotDatabase, captureTime, drone) # Update the pilot database

        else:
            print(drone.serialNumber + " : " + str(round(distance/1000,2)) + "m")

    WritePilotDatabase("Database/pilots.csv", pilotDatabase) # Then write the changes
    
    
    # Match the API update rate
    print("Compute time: " + str(round(time.time() - startTime, 3)) + "s")
    time.sleep(apiUpdateRate - (time.time() - startTime))