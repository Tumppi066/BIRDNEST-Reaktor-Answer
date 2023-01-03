import requests

dataUrl = "https://assignments.reaktor.com/birdnest/drones"
pilotUrl = "https://assignments.reaktor.com/birdnest/pilots/" # */ drone serial number


def GetDroneData():
    # Get new drone data from the API
    data = requests.get((dataUrl)).text
    return data # return (xml) data

def GetPilotData(serialNumber):
    # Get pilot data from the API
    try: 
        data = requests.get((pilotUrl + serialNumber)).text
    except: 
        return "Error 404" # return error if the pilot is unknown

    return data # return the (json) data 



