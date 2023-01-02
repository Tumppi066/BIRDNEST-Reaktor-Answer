dronesURL = "http://127.0.0.1:8000/drones"
pilotsURL = "http://127.0.0.1:8000/pilots"

function getData()
{
    var xhr = new XMLHttpRequest();
    xhr.open("GET", pilotsURL, false);
    xhr.send(null);
    if (xhr.readyState === 4) {
        if (xhr.status === 200) {
            response = xhr.responseText.replace(',\\n"]', "");
            response = response.replace('["', "");
            response = response.split("\\n");
            return response;
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

function calculateDistance(x,y){
    return Math.sqrt(Math.pow(250000-x,2) + Math.pow(250000-y,2));
}

function createPilotTableElement(pilot){
    pilot = pilot.split(",");
    let element = "<tr><td>" + new Date(Math.floor(pilot[4]*1000)).toLocaleString() + "</td><td>" + Math.round(calculateDistance(pilot[5], pilot[6])/1000) + " meters</td><td>" + pilot[0] + "</td><td>" + pilot[1] + "</td><td>" + pilot[2] + "</td></tr>";
    return element;
}

function updateDisplay(){
    let categories = "<tr><th>Latest time in NDZ</th><th>Closest Distance</th><th>Full Name</th><th>Phone Number</th><th>Email</th></tr>";
    let table = document.getElementById("table");
    table.innerHTML = categories;
    data = getData();
    for(i = 1; i < data.length; i++){
        table.innerHTML += createPilotTableElement(data[i]);
    }
}

window.onload = function() {
    setInterval(updateDisplay, 2000);
}
