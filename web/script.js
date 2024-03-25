const mapsDialog = document.getElementById("mapsDialog");
const enhancingDialog = document.getElementById("enhancingDialog");
const successDialog = document.getElementById("successDialog");

const okButton = document.getElementById("okButton");
okButton.addEventListener("click", () => {
    successDialog.close();
});

const enhanceButton = document.getElementById("enhanceButton");
enhanceButton.addEventListener("click", () => {
    mapsDialog.showModal();
    eel.getImage(map.getCenter(), map.getZoom());
});

const radioButtons = document.querySelectorAll(".radioButton");
let selectedButton = radioButtons[0];
selectedButton.style.border = "15px inset orange";
radioButtons.forEach(button => {
    button.addEventListener("click", () => {
        selectedButton.style.border = "15px outset black";
        button.style.border = "15px inset orange";
        selectedButton = button;
    });
});

let map;
initMap();

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
        minZoom: 3,
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

        if (places.length === 0) {
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

eel.expose(enhanceImage);
function enhanceImage() {
    mapsDialog.close();
    enhancingDialog.showModal();
    const enhanceLevel = selectedButton.getAttribute("id");
    eel.execute_enhance(`options/Test/test_single_${enhanceLevel}.yml`);
}

eel.expose(finishEnhance)
function finishEnhance() {
    enhancingDialog.close();
    successDialog.showModal();
}