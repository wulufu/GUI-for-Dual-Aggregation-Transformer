const mapsDialog = document.getElementById("mapsDialog");
const enhancingDialog = document.getElementById("enhancingDialog");
const successDialog = document.getElementById("successDialog");
const fileSelect = document.getElementById("fileSelect");
const searchBox = document.getElementById("searchBox");
let map = undefined;

const okButton = document.getElementById("okButton");
okButton.addEventListener("click", () => {
    successDialog.close();
});

const enhanceButton = document.getElementById("enhanceButton");
enhanceButton.addEventListener("click", () => {
    mapsDialog.showModal();
    eel.getImage(map.getCenter(), map.getZoom());
});

const localImageTab = document.getElementById("localImageTab");
localImageTab.addEventListener("click", () => {
    localImageTab.classList.add("selected");
    satelliteTab.classList.remove("selected");
    map.getDiv().style.display = "none";
    fileSelect.style.display = "block";
});

const satelliteTab = document.getElementById("satelliteTab");
satelliteTab.addEventListener("click", async () => {
    if (map === undefined) {
        await initMap();
        searchBox.style.display = "block";
    }

    satelliteTab.classList.add("selected");
    localImageTab.classList.remove("selected");
    fileSelect.style.display = "none";
    map.getDiv().style.display = "block";
});

const radioButtons = document.querySelectorAll(".radioButton");
let selectedRadioButton = document.querySelector(".radioButton.selected");
radioButtons.forEach(radioButton => {
    radioButton.addEventListener("click", e => {
        const clickedRadioButton = e.target;

        selectedRadioButton.classList.remove("selected");
        clickedRadioButton.classList.add("selected");
        selectedRadioButton = clickedRadioButton;
    });
});

async function initMap() {
    // Load the Maps JavaScript API dynamically
    (g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})({
        key: "AIzaSyAz7DIMRFMREUS1oea5JnwxDck_veuDqWI"
    });

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
    const search = new SearchBox(searchBox);
    map.controls[ControlPosition.TOP_LEFT].push(searchBox);

    // Listen for the event fired when the user selects a prediction and retrieve
    // more details for that place.
    search.addListener("places_changed", () => {
        const places = search.getPlaces();

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
