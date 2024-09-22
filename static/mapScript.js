let customCRS; // Declare customCRS outside the event listener
let map; // Declare map outside the event listener
//let mapBaseName;

document.addEventListener("DOMContentLoaded", function () {
    customCRS = L.CRS.Simple;

    // Assuming 'map' is your Leaflet map object
    map = L.map('map', {
        crs: customCRS,
        minZoom: -5,
        maxZoom: 5,
    });

    // Set the initial view and zoom level
    map.setView([0, 0], 0);

    // Add the custom control for displaying cursor coordinates
    const coordinatesControl = L.control.coordinates().addTo(map);


    function loadMap(mapBaseName) {
        //console.log('Selected map base name:', mapBaseName);

        // Clear existing layers from the map
        map.eachLayer(layer => {
            if (layer !== map) {
                map.removeLayer(layer);
            }
        });

        const fileNames = [`/static/assets/maps/${mapBaseName}.txt`, `/static/assets/maps/${mapBaseName}_1.txt`, `/static/assets/maps/${mapBaseName}_2.txt`, `/static/assets/maps/${mapBaseName}_3.txt`];
        const bounds = L.latLngBounds(); // Create bounds object to include all markers

        fileNames.forEach((fileName, index) => {
            fetch(fileName)
                .then(response => response.text())
                .then(content => {
                    const markerBounds = parseAndAddMarkers(content, `map_${index}`);
                    bounds.extend(markerBounds.getSouthWest());
                    bounds.extend(markerBounds.getNorthEast());
                    updateLayerVisibility();
                })
                .catch(error => {
                    console.error(`Error fetching or parsing file ${fileName}:`, error);
                });
        });

        // Fit the map to the bounds of all markers
        //console.log('Bounds:', bounds);
        if (bounds.isValid()) {

            map.fitBounds(bounds);
        } else {
            console.error('Invalid bounds:', bounds);
        }

    }
    loadMap(mapBaseName)
    // Add a custom control to display cursor coordinates
    L.Control.Coordinates = L.Control.extend({
        options: {
            position: 'bottomright', // change the position of the control
            // define labels for x and y coordinates
            latitudeText: 'Latitude:',
            longitudeText: 'Longitude:',
        },

        onAdd: function (map) {
            this._div = L.DomUtil.create('div', 'leaflet-control-coordinates');
            return this._div;
        },

        onRemove: function (map) {
            // Nothing to do here
        },

        updateCoordinates: function (lat, lng) {
            coordinatesControl._container.innerHTML =
            //this._div.innerHTML =
                `<b>${this.options.latitudeText}</b> ${lat.toFixed(5)}<br><b>${this.options.longitudeText}</b> ${lng.toFixed(5)}`;
        },
    });

    L.control.coordinates = function (options) {
        return new L.Control.Coordinates(options);
    };

    L.control.coordinates().addTo(map);

    // Attach an event listener to update the cursor coordinates
    map.on('mousemove', function (e) {
        const { lat, lng } = e.latlng;
        coordinatesControl._container.innerHTML = `Latitude: ${lat.toFixed(4)}, Longitude: ${lng.toFixed(4)}`;
    })
});

function parseAndAddMarkers(content, layerName) {
    const lines = content.split('\n');
    const bounds = L.latLngBounds();

    lines.forEach(line => {
        const parts = line.trim().split(/\s+/);
        const type = parts[0];

        if (type === 'L') {
            const lineCoordinates = [
                L.latLng(-parseFloat(parts[2]), parseFloat(parts[1]), parseFloat(parts[3])),
                L.latLng(-parseFloat(parts[5]), parseFloat(parts[4]), parseFloat(parts[6])),
            ];

            const color = `rgb(${parseInt(parts[7])}, ${parseInt(parts[8])}, ${parseInt(parts[9])})`;

            const line = L.polyline(lineCoordinates, { color, name: 'map' }); // Set name to 'map' for lines
            line.addTo(map);

            // Extend bounds with line coordinates
            bounds.extend(lineCoordinates[1]);
            bounds.extend(lineCoordinates[0]);


            //console.log('Line Bounds:', bounds.toBBoxString());
        } else if (type === 'P') {
            const pointCoordinates = L.latLng(-parseFloat(parts[2]), parseFloat(parts[1]), parseFloat(parts[3]));

            const color = `rgb(${parseInt(parts[4])}, ${parseInt(parts[5])}, ${parseInt(parts[6])})`;

            const point = L.circleMarker(pointCoordinates, { color, name: 'map' }); // Set name to 'map' for points
            point.addTo(map);
            point.bindPopup(parts.slice(7).join(' '));

            // Extend bounds with point coordinates
            bounds.extend(pointCoordinates);

            //console.log('Point Bounds:', bounds.toBBoxString());
        }
    });

    //console.log('Final Bounds:', bounds.toBBoxString());
    return bounds;
}

/////////
const layerVisibility = {
    base: true,
    map: true,
    map_1: true,
    map_2: true,
    map_3: true,
};

function toggleLayer(layerName) {
    if (layerName in layerVisibility) {
        layerVisibility[layerName] = !layerVisibility[layerName];
        updateLayerVisibility();
    }
}

// Function to update layer visibility on the map
function updateLayerVisibility() {
    map.eachLayer(layer => {
        if (layer !== map && layer.options && layer.options.name) {
            const layerName = layer.options.name;
            if (layerName in layerVisibility) {
                if (layerVisibility[layerName]) {
                    map.addLayer(layer);
                } else {
                    map.removeLayer(layer);
                }
            }
        }
    });

}

         
