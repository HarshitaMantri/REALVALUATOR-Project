function getBathValue() {
  var uiBathrooms = document.getElementsByName("uiBathrooms");
  for (var i = 0; i < uiBathrooms.length; i++) {
    if (uiBathrooms[i].checked) {
      return parseInt(uiBathrooms[i].value);
    }
  }
  return -1;
}

function getBHKValue() {
  var uiBHK = document.getElementsByName("uiBHK");
  for (var i = 0; i < uiBHK.length; i++) {
    if (uiBHK[i].checked) {
      return parseInt(uiBHK[i].value);
    }
  }
  return -1;
}

function onClickedEstimatePrice() {
  var sqft = document.getElementById("uiSqft");
  var bhk = getBHKValue();
  var bathrooms = getBathValue();
  var location = document.getElementById("uiLocations");
  var estPrice = document.getElementById("uiEstimatedPrice");

  // Validation
  if (!location || !location.value) {
    estPrice.innerHTML = "<h2>Error: Please select a location</h2>";
    return;
  }
  
  if (!sqft || !sqft.value || parseFloat(sqft.value) <= 0) {
    estPrice.innerHTML = "<h2>Error: Please enter a valid area</h2>";
    return;
  }

  if (bhk <= 0 || bathrooms <= 0) {
    estPrice.innerHTML = "<h2>Error: Please select BHK and Bath</h2>";
    return;
  }

  var url = "http://127.0.0.1:5000/api/predict_home_price";

  // Show loading message
  estPrice.innerHTML = "<h2>Calculating...</h2>";
  
  $.ajax({
    url: url,
    type: 'POST',
    data: {
      total_sqft: parseFloat(sqft.value),
      bhk: bhk,
      bath: bathrooms,
      location: location.value
    },
    success: function(data) {
      console.log("Response data:", data);
      if (data.error) {
        estPrice.innerHTML = "<h2>Error: " + data.error + "</h2>";
      } else if (data.estimated_price !== null && data.estimated_price !== undefined) {
        estPrice.innerHTML = "<h2>" + data.estimated_price.toString() + " Lakh</h2>";
      } else {
        estPrice.innerHTML = "<h2>Error: Invalid response from server</h2>";
      }
    },
    error: function(xhr, status, error) {
      console.error("Request failed:", status, error);
      console.error("Status code:", xhr.status);
      console.error("Response:", xhr.responseText);
      
      var errorMsg = "could not get price";
      try {
        var errorData = JSON.parse(xhr.responseText);
        if (errorData.error) {
          errorMsg = errorData.error;
        }
      } catch (e) {
        if (xhr.status === 0) {
          errorMsg = "Server is not responding. Please check if the server is running.";
        } else if (xhr.status === 404) {
          errorMsg = "API endpoint not found. Please check the server configuration.";
        } else if (xhr.status === 500) {
          errorMsg = "Server error. Check server logs for details.";
        }
      }
      estPrice.innerHTML = "<h2>Error: " + errorMsg + "</h2>";
    }
  });
}

function onPageLoad() {
  var url = "http://127.0.0.1:5000/api/get_location_names";
  $.get(url, function(data) {
      if (data) {
          $('#uiLocations').empty();
          for(var i in data.locations) {
              $('#uiLocations').append(new Option(data.locations[i]));
          }
      }
  });

  var btn = document.getElementById("uiEstimatePrice");
  if (btn) {
    btn.addEventListener("click", onClickedEstimatePrice);
  }
}

window.onload = onPageLoad;