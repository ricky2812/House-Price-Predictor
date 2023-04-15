
window.onload = onPageLoad;
localpredict = 'localhost:5000/predict_home_price'
locallocation = 'localhost:5000/get_location_names'

function onClickedEstimatePrice() {
    console.log("Estimate price button clicked");
    var sqft = document.getElementById("uiSqft");
    var bhk = getBHKValue();
    var location = document.getElementById("uiLocations");
    var estPrice = document.getElementById("uiEstimatedPrice");
    var city = GetCityName();
    var form = new FormData();

    form.append("total_sqft", sqft.value);
    form.append("location", location.value);
    form.append("bhk", bhk);
    form.append("city", city);

    var settings = {
    // "url": "/api/predict_home_price",
    "url": localpredict,
    "method": "POST",
    "timeout": 0,
    "processData": false,
    "mimeType": "multipart/form-data",
    "contentType": false,
    "data": form
    };

    $.ajax(settings).done(function (response) {
    console.log(response);
    var data = JSON.parse(response);
    estPrice.innerHTML = "<h2>" + data.estimated_price.toString() + "</h2>";
    });
    
    // show the estimated price
}  

function getBHKValue(){
    var uiBHK = document.getElementsByName("uiBHK");
    for(var i in uiBHK)
    {
        if(uiBHK[i].checked)
        {
            return parseInt(i)+1;
        }
    }
    return -1; // Invalid Value
}


function GetCityName(){
    var uicity = document.getElementsByName("uicity");
    for(var i in uicity)
    {
        if(uicity[i].checked)
        {
            return uicity[parseInt(i)].value;
        }
    }
    return -1; // Invalid Value
}


function onCityChanged(){
    var sqft = document.getElementById("uiSqft").value;
    var bhk = getBHKValue();
    var city = GetCityName();
    
    console.log("bhk",bhk);
    console.log("sqft",sqft);
    console.log("city",city);
    getlocations(city);
}


function onPageLoad(){
    console.log( "document loaded" );
    var sqft = document.getElementById("uiSqft").value;
    var bhk = getBHKValue();
    var city = GetCityName();

    updateInfo();
    loadInfo()
    //print info in every change
    $('#uiSqft').change(loadInfo);
    $('#uiBHK').change(loadInfo);
    $('#uicity').change(updateInfo);
    $('#uiLocations').change(loadInfo);
    
}



function getlocations(city){
    // var url = "/api/get_location_names";
    var url = locallocation;
    var form = new FormData();
    form.append("city", city);
    var settings = {
    "url": url,
    "method": "POST",
    "timeout": 0,
    "processData": false,
    "mimeType": "multipart/form-data",
    "contentType": false,
    "data": form
    };
    $.ajax(settings).done(function (response) {
        var data = JSON.parse(response);
        var list = data["locations"]
        $('#uiLocations').empty();
        $('#uiLocations').append('<option value="None" selected disabled>Choose a Location</option>');
        for(var i in list){
            var opt = new Option(list[i]);
            $('#uiLocations').append(opt);
        }
    });
}

function loadInfo(){
    var sqft = document.getElementById("uiSqft").value;
    var bhk = getBHKValue();
    var city = GetCityName();
    var location = document.getElementById("uiLocations").value;

    console.log("bhk",bhk);
    console.log("sqft",sqft);
    console.log("city",city);
    if(location == ""){ location = "None"; }
    console.log("location",location);
}

function updateInfo(){
    loadInfo();
    var city = GetCityName();
    getlocations(city);
}
