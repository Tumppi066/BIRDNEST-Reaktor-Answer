let dronesURL = "https://birdnest.tumppi066.xyz/api/drones";
let pilotsURL = "https://birdnest.tumppi066.xyz/api/pilots";
let runtimeURL = "https://birdnest.tumppi066.xyz/api/runtime";
let violationCount = 0;



function getApiData(url)
{
    // This function will call the api
    // and return the data
    
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, false);
    xhr.send(null); // Send an empty request
    if (xhr.readyState === 4) {
        if (xhr.status === 200) {
            return xhr.responseText;
        } 
        else {
            console.error(xhr.statusText);
            return "error";
        }   
    }
    else
    {
        console.error(xhr.readyState);
        return "error";
    }
}

function getPilotData()
{
    // This function will parse the pilot data
    let response = getApiData(pilotsURL);
    response = response.replace(',\\n"]', "").replace('["', ""); // Remove python array brackets
    response = response.split("\\n"); // Then split to get each line
    return response;
}

function getRuntimeData()
{
    // This function will parse the runtime data
    response = getApiData(runtimeURL);
    response.replace("[", "").replace("]", ""); // Remove python array brackets
    return response;
}

// distance (2d) = sqrt((x2-x1)^2 + (y2-y1)^2)
function calculateDistance(x,y){
    return Math.sqrt(Math.pow(250000-x,2) + Math.pow(250000-y,2));
}

// This will create a new element for the table
// Pilot = [name, phone, email, drone serial, time, close x, close y]
function createPilotTableElement(pilot){
    // Split the line to get each value
    pilot = pilot.split(","); 
    // Round the distance to 2 decimals
    distance = (Math.floor(calculateDistance(pilot[6], pilot[7])/10))/100

    // Create the element
    let element = "<tr><td>" + new Date(Math.floor(pilot[4]*1000)).toLocaleString() + "</td>"           // Time In NDZ
                             + "<td>" + new Date(Math.floor(pilot[5]*1000)).toLocaleString() + "</td>"  // Last Seen
                             + "<td>" + distance + " meters</td><td>"                                   // Distance
                             + pilot[0] + "</td><td>"                                                   // Name
                             + pilot[1] + "</td><td>"                                                   // Phone
                             + pilot[2] + "</td></tr>";                                                 // Email
    
    return element;
}

// Will check if the pilot is already in the table
// If not, it will create a new element
// Pilot = [name, phone, email, drone serial, time, close x, close y]
// Number = The number of the element in the table
// Table = The table element
function updatePilotTableElement(pilot, number, table){ 
    // Check if the table element already exists
    let element = table.children[number];
    if(element == undefined){
        // If not, we create it
        element = createPilotTableElement(pilot);
        table.innerHTML += element;
    }
    else
    {
        // If it does, we update the information
        pilot = pilot.split(",");
        distance = (Math.floor(calculateDistance(pilot[6], pilot[7])/10))/100
        element.children[0].children[0].innerHTML = new Date(Math.floor(pilot[4]*1000)).toLocaleString(); // Time In NDZ
        element.children[0].children[1].innerHTML = new Date(Math.floor(pilot[5]*1000)).toLocaleString(); // Last Seen
        element.children[0].children[2].innerHTML = distance + " meters";                                 // Distance
    }
}

// This function will update the table
function updatePilots(){
    // Get the data from the api
    data = getPilotData(); 
    // Update the violation count
    violationCount = data.length - 1; 


    let table = document.getElementById("table");
    for(i = 1; i < data.length; i++){
        // Update each element
        updatePilotTableElement(data[i], i, table);
    }

    let element = table.children[1]; // Get the first table element
    let name = element.children[0].children[3].innerHTML; // And then the name of the first pilot in the table

    let dataName = data[1].split(",")[0]; // Get the name of the first pilot from the data
    if(name != dataName){
        element.remove(); // If the name is different, we remove the first element
    }
        
}

// This function will update the information
// (violation count and current time)
function updateInformation(){

    let violationCounter = document.getElementById("Violations");
    violationCounter.innerHTML = "Violations in the past 10 minutes : " + violationCount;

    let time = document.getElementById("Time");
    time.innerHTML = new Date().toLocaleString();

    let runtime = document.getElementById("Runtime");
    let backendRuntime = getRuntimeData();
    runtime.innerHTML = "Backend Runtime : " + Math.floor(backendRuntime.replace("[", "").replace("]","")/3600*100)/100 + " hours";

}


window.onload = function() {
    // Call the main functions every 2 seconds
    setInterval(updatePilots, 2000);
    setInterval(updateInformation, 2000);
}
