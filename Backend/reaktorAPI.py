import requests

dataUrl = "https://assignments.reaktor.com/birdnest/drones"
pilotUrl = "https://assignments.reaktor.com/birdnest/pilots/" # */ drone serial number


def GetNewData():
    data = requests.get((dataUrl)).text
    return data # return (xml) data

def GetPilotData(serialNumber):
    try: 
        data = requests.get((pilotUrl + serialNumber)).text
    except: 
        return "Error 404"
    return data # return (xml) data 



