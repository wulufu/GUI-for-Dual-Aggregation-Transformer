const enhanceX2 = document.getElementById("enhanceX2");
const enhanceX3 = document.getElementById("enhanceX3");
const enhanceX4 = document.getElementById("enhanceX4");
const radioTwo = document.getElementById("radioTwo");
const radioThree = document.getElementById("radioThree");
const radioFour = document.getElementById("radioFour");
const previewButton = document.getElementById("previewButton");
const downloadButton = document.getElementById("downloadButton");
let map;

initMap();
downloadButton.addEventListener("click", downloadImage);
previewButton.addEventListener("click", previewImage);
enhanceX2.addEventListener("click", () => setRadioButton(radioTwo, 2));
enhanceX3.addEventListener("click", () => setRadioButton(radioThree, 3));
enhanceX4.addEventListener("click", () => setRadioButton(radioFour, 4));

function downloadImage() {
    let option;

    if (radioTwo.checked) {
        option = "options/Test/test_single_x2.yml";
    } else if (radioThree.checked) {
        option = "options/Test/test_single_x3.yml";
    } else if (radioFour.checked) {
        option = "options/Test/test_single_x4.yml";
    } else {
        console.log("Error calling enhance: No enhance option selected.")
        return;
    }

    console.log(option);
    eel.execute_enhance(option);
}

function previewImage() {
    center = map.getCenter();
    zoom = map.getZoom();
    eel.getImage(center, zoom)
}

async function initMap() {
    const {Map} = await google.maps.importLibrary("maps");
    const {SearchBox} = await google.maps.importLibrary("places")
    const {ControlPosition} = await google.maps.importLibrary("core")
    const {LatLngBounds} = await google.maps.importLibrary("core")

    map = new Map(document.getElementById("map"), {
        center: {lat: 42.684, lng: -73.827},
        zoom: 15,
        mapTypeId: "satellite",
        tilt: 0,
        mapTypeControl: false,
        streetViewControl: false,
        keyboardShortcuts: false
    });

    // Create the search box and link it to the UI element.
    const input = document.getElementById("searchBox");
    const searchBox = new SearchBox(input);
  
    map.controls[ControlPosition.TOP_LEFT].push(input);

    // Listen for the event fired when the user selects a prediction and retrieve
    // more details for that place.
    searchBox.addListener("places_changed", () => {
        const places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }

        // For each place, get the icon, name and location.
        const bounds = new LatLngBounds();

        places.forEach((place) => {
            if (!place.geometry || !place.geometry.location) {
                console.log("Returned place contains no geometry");
                return;
            }

            if (place.geometry.viewport) {
                // Only geocodes have viewport.
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
    
        map.fitBounds(bounds);
    });
}

function setRadioButton(radioInput, buttonInput) {
    radioInput.checked = true;
    enhanceX2.style.color = "wheat";
    enhanceX3.style.color = "wheat";
    enhanceX4.style.color = "wheat";
    enhanceX2.style.border = "15px outset black";
    enhanceX3.style.border = "15px outset black";
    enhanceX4.style.border = "15px outset black";
    
    switch(buttonInput) {
        case 2:
            enhanceX2.style.border = "15px inset orange";
            // set value of the default enhance level
        break;
        case 3:
            enhanceX3.style.border = "15px inset orange";
            // set value of the default enhance level
        break;
        case 4:
            enhanceX4.style.border = "15px inset orange";
            // set value of the default enhance level
        break;
    }
}
