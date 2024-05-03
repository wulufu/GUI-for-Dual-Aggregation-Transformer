"use strict";

const fileSelectTab = document.getElementById("fileSelectTab");
const satelliteTab = document.getElementById("satelliteTab");
const filePath = document.getElementById("filePath");
const radioButtons = document.querySelectorAll(".radioButton");
const dialogs = document.querySelectorAll("dialog");

let selectedRadioButton = document.querySelector(".radioButton.selected");
let currentTab = document.querySelector(".tab.selected");
let python;
let map;

initPython();
initTabs();
initButtonPanel();
initDialogs();
initFileSelect();

// Allows methods defined in Python to be called in JavaScript.
function initPython() {
    window.addEventListener("pywebviewready", () => {
        python = window.pywebview.api;
    });
}

// Adds functionality to tabs that allows for switching between the file
// select window and satellite image window.
function initTabs() {
    const fileSelect = document.getElementById("fileSelect");

    fileSelectTab.addEventListener("click", () => {
        // No need to do anything if we are already on this tab
        if (currentTab === fileSelectTab) {
            return;
        }
    
        fileSelectTab.classList.add("selected");
        satelliteTab.classList.remove("selected");
        map.getDiv().style.display = "none";
        fileSelect.style.display = "flex";
        currentTab = fileSelectTab;
    });
    
    satelliteTab.addEventListener("click", async () => {
        // No need to do anything if we are already on this tab
        if (currentTab === satelliteTab) {
            return;
        }
    
        // Loading of map is delayed until the first time we visit this tab
        if (!map) {
            showDialog("loading", "Connecting to Google Maps...");

            try {
                await initMap();
            } catch {
                showDialog("popup", "Could not connect to Google Maps.");
                return;
            }
        }
    
        satelliteTab.classList.add("selected");
        fileSelectTab.classList.remove("selected");
        fileSelect.style.display = "none";
        map.getDiv().style.display = "block";
        currentTab = satelliteTab;
        closeDialogs();
    });
}

// Adds functionality to the buttons displayed next to the map or file select.
// The enhance button activates DAT using the enhance level represented by the
// currently selected radio button.
function initButtonPanel() {
    const enhanceButton = document.getElementById("enhanceButton");

    enhanceButton.addEventListener("click", async () => {
        if (currentTab === satelliteTab) {
            await enhanceMapsImage()
        } else if (!filePath.value) {
            showDialog("popup", "A file location must be chosen.");
        } else {
            await enhanceImageFile();
        }
    });

    for (let radioButton of radioButtons) {
        radioButton.addEventListener("click", event => {
            const clickedRadioButton = event.target;
    
            selectedRadioButton.classList.remove("selected");
            clickedRadioButton.classList.add("selected");
            selectedRadioButton = clickedRadioButton;
        });
    }
}

// Asks Python to get an image from the Google Maps API at the location that
// is currently visible on the map and enhance it. Loading dialogs are shown
// while waiting, and a save dialog is shown when finished. An error dialog
// may be displayed if something goes wrong.
async function enhanceMapsImage() {
    const enhanceLevel = getEnhanceLevel();
    const mapCenter = map.getCenter();
    const mapZoom = map.getZoom();

    try {
        await python.enhance_maps_image(mapCenter, mapZoom, enhanceLevel);
    } catch (error) {
        showDialog("popup", `An unexpected error has occurred. ${error}`);
    }
}

// Asks Python enhance the image located at the currently selected file path
// using DAT. A loading dialog is shown while waiting, and a save dialog is
// shown when finished. Errors that occur are handled in Python.
async function enhanceImageFile() {
    const enhanceLevel = getEnhanceLevel();

    try {
        await python.enhance_image_file(filePath.value, enhanceLevel);
    } catch (error) {
        showDialog("popup", `An unexpected error has occurred. ${error}`);
    }
}

// Get the enhance level indicated by the currently selected radio button.
function getEnhanceLevel() {
    const radioButton = selectedRadioButton.getAttribute("id");

    switch(radioButton) {
        case "x2Button":
            return 2;
        case "x3Button":
            return 3;
        case "x4Button":
            return 4;
    }
}

// Adds functionality to buttons contained within dialogs, and prevents ESC
// from being used to close dialogs.
function initDialogs() {
    const saveImageButton = document.getElementById("saveImageButton");
    const closeButtons = document.querySelectorAll(".dialogClose");

    for (let dialog of dialogs) {
        dialog.addEventListener("cancel", event => {
            event.preventDefault();
        });
    }

    for (let button of closeButtons) {
        button.addEventListener("click", event => {
            event.target.parentNode.close();
        });
    }
    
    saveImageButton.addEventListener("click", async () => {
        try {
            if (currentTab === satelliteTab) {
                await python.save_enhanced_image("map.png");
            } else {
                await python.save_enhanced_image(filePath.value);
            }
        } catch (error) {
            showDialog("popup", `An unexpected error has occurred. ${error}`);
        }
    });
}

// Adds functionality to the file select window that allows it to receive
// files, either through drag and drop or File Explorer. Python handles
// getting these files and their full paths.
function initFileSelect() {
    const fileDropZone = document.getElementById("fileDropZone");
    const chooseFileButton = document.getElementById("chooseFileButton");
    const fileDropElements = document.querySelectorAll(".fileDropAllowed")

    // This button asks Python to open File Explorer and get an image file.
    chooseFileButton.addEventListener("click", async () => {
        try {
            await python.choose_image_file();
        } catch (error) {
            showDialog("popup", `An unexpected error has occurred. ${error}`);
        }
    });
    
    let enterTarget;

    // Allow the file drop zone to visually react to files dragged over it.
    for (let element of fileDropElements) {
        element.addEventListener("dragenter", event => {
            enterTarget = event.target;
            fileDropZone.classList.add("active");
        });
        
        element.addEventListener("dragleave", event => {
            if (event.target === enterTarget) {
                fileDropZone.classList.remove("active");
            }            
        });
        
        element.addEventListener("drop", () => {
            fileDropZone.classList.remove("active");
        });
    }

    preventDefaultDragBehavior();
}

// By default, dragging files into the browser will open them in a new tab.
// Running this functions prevents this from happening so that file drag and
// drop functionality can work as intended.
function preventDefaultDragBehavior() {
    document.addEventListener("dragover", event => {
        event.preventDefault();
        event.stopPropagation();
    });
}

// Shows a dialog with the message provided and different behavior depending on
// the type chosen. The different types work as follows...
//
// "loading": No buttons displayed, can't be closed by the user.
// "popup": A single button is displayed that lets the user close the dialog.
// "save": Special case displaying a dialog closing button and an image-saving
//         button that lets the user save the previously enhanced image.
function showDialog(dialogType, message) {
    const id = `${dialogType}Dialog`;
    const dialog = document.getElementById(id);
    const dialogText = document.querySelector(`#${id} .dialogText`);

    dialogText.textContent = message;
    closeDialogs();
    dialog.showModal();
}

function closeDialogs() {
    for (let dialog of dialogs) {
        dialog.close();
    }
}

// Connects to the Google Maps API to create an interactive map with search.
async function initMap() {
    // Load the Maps JavaScript API dynamically.
    (g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})({
        key: "AIzaSyAz7DIMRFMREUS1oea5JnwxDck_veuDqWI"
    });

    const {Map} = await google.maps.importLibrary("maps");
    const {ControlPosition} = await google.maps.importLibrary("core");

    // Create the map object within existing div element.
    map = new Map(document.getElementById("map"), {
        center: {lat: 42.684, lng: -73.827},
        restriction: {
            latLngBounds: {north: 85, south: -85, west: -180, east: 180},
            strictBounds: true,
        }, 
        zoom: 15,
        tilt: 0,
        mapTypeId: "satellite",
        zoomControl: true,
        mapTypeControl: false,
        scaleControl: false,
        streetViewControl: false,
        rotateControl: false,
        fullscreenControl: false,
        keyboardShortcuts: false
    });

    // Add custom controls to the map.
    const searchBox = await createSearchBox();
    const labelToggle = await createLabelToggle();
    map.controls[ControlPosition.TOP_LEFT].push(searchBox);
    map.controls[ControlPosition.TOP_RIGHT].push(labelToggle);
}

// Create and give functionality to search box element used in map.
async function createSearchBox() {
    const searchBox = document.createElement("input");
    searchBox.type = "text";
    searchBox.placeholder = "Search for a place...";
    searchBox.style.outline = "none";
    searchBox.style.margin = "8px";

    const {SearchBox} = await google.maps.importLibrary("places");
    const {LatLngBounds} = await google.maps.importLibrary("core");
    
    // Add functionality to search box.
    const search = new SearchBox(searchBox);

    // The search box retrieves more details about predictions it displays.
    search.addListener("places_changed", () => {
        const places = search.getPlaces();

        if (places.length === 0) {
            return;
        }

        // Get the actual location for each place.
        const bounds = new LatLngBounds();

        places.forEach((place) => {
            if (!place.geometry || !place.geometry.location) {
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

    return searchBox;
}

// Create and give functionality to label toggle button used in map.
async function createLabelToggle() {
    const labelToggle = document.createElement("button");
    labelToggle.textContent = "Toggle Labels"
    labelToggle.style.color = "#666666";
    labelToggle.style.margin = "8px";
    
    labelToggle.addEventListener("click", () => {
        if (map.getMapTypeId() === "satellite") {
            map.setMapTypeId("hybrid");
        } else {
            map.setMapTypeId("satellite");
        }
    });

    return labelToggle;
}

// This function is called by Python whenever the user chooses a new file so
// that the file path can be displayed in the GUI.
function updateCurrentFile(file) {
    filePath.value = file;
}
