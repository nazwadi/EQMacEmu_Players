document.addEventListener('DOMContentLoaded', function () {
    // https://github.com/Leaflet/Leaflet/issues/9067
    const mapContainer = document.getElementById('map')
    const map = L.map(mapContainer, {
        crs: L.CRS.Simple,
        minZoom: -5,
        maxZoom: 5,
        attributionControl: false
    });

    L.Util.extend(L.CRS.Simple, {transformation: new L.Transformation(-1, 0, -1, 0)});

    const bounds = [
        [0, 0],
        [1000, 1000]
    ]
    map.setView([0, 0], -1)

    const pointsLayer = L.layerGroup().addTo(map)
    const linesLayer = L.layerGroup().addTo(map)
    let points = []
    let lines = []
    let zMin = Number.POSITIVE_INFINITY
    let zMax = Number.NEGATIVE_INFINITY

    function loadMap(mapBaseName) {
        const fileNames = [
            `/static/assets/maps/${mapBaseName}.txt`,
            `/static/assets/maps/${mapBaseName}_1.txt`,
            `/static/assets/maps/${mapBaseName}_2.txt`,
            `/static/assets/maps/${mapBaseName}_3.txt`
        ]

        Promise.all(fileNames.map(fileName => loadFile(fileName))).then(() => {
            initializeSliders()
            updateMapBasedOnZRange()
        })
    }

    function loadFile(fileName) {
        return fetch(fileName)
            .then(response => response.text())
            .then(content => {
                const { lines: fileLines, points: filePoints } =
                    createLinesAndPointsFromContent(content)
                points.push(...filePoints)
                lines.push(...fileLines)
            })
            .catch(error => {
                console.error(`Error fetching or parsing file ${fileName}:`, error)
            })
    }

    function createLinesAndPointsFromContent(content) {
        const lines = []
        const points = []
        const linesData = content.split('\n')

        linesData.forEach(lineData => {
            const parts = lineData.trim().split(/\s+/)
            const type = parts[0]

            if (type === 'L') {
                const x1 = parseFloat(parts[1])
                const y1 = parseFloat(parts[2])
                const z1 = parseFloat(parts[3])
                const x2 = parseFloat(parts[4])
                const y2 = parseFloat(parts[5])
                const z2 = parseFloat(parts[6])

                lines.push({
                    points: [
                        [-y1, -x1],
                        [-y2, -x2]
                    ],
                    z: Math.max(z1, z2),
                    color: rgbToHex(parts[7], parts[8], parts[9])
                })

                zMin = Math.min(zMin, z1, z2)
                zMax = Math.max(zMax, z1, z2)
            } else if (type === 'P') {
                const x = parseFloat(parts[1])
                const y = parseFloat(parts[2])
                const z = parseFloat(parts[3])
                const description = parts.slice(8).join(' ')

                points.push({
                    x: x,
                    y: -y,
                    z: z,
                    color: rgbToHex(parts[4], parts[5], parts[6]),
                    description: description
                })

                zMin = Math.min(zMin, z)
                zMax = Math.max(zMax, z)
            }
        })

        return { lines: lines, points: points }
    }

    function initializeSliders() {
        const container = document.getElementById('z-filter-container')

        const zSlider = document.createElement('div')
        zSlider.id = 'slider-square'
        zSlider.className = 'slider-styled'
        container.appendChild(zSlider)

        noUiSlider.create(zSlider, {
            start: [zMin, zMax],
            connect: true,
            range: {
                min: zMin,
                max: zMax
            },
            tooltips: false,
            format: {
                to: function (value) {
                    return value.toFixed(2)
                },
                from: function (value) {
                    return Number(value)
                }
            }
        })
        zSlider.style.width = '100px'
        zSlider.noUiSlider.on('update', updateMapBasedOnZRange)
    }

    const ZFilterControl = L.Control.extend({
        onAdd: function () {
            const container = L.DomUtil.create('div', 'leaflet-bar')
            container.id = 'z-filter-container'

            const label = L.DomUtil.create('label', '', container)
            label.innerHTML = 'Z Range:'

            return container
        }
    })

    map.addControl(new ZFilterControl({ position: 'bottomleft' }))

    function updateMapBasedOnZRange() {
        const zSlider = document.getElementById('slider-square').noUiSlider
        const zRange = zSlider.get()
        const zMin = parseFloat(zRange[0])
        const zMax = parseFloat(zRange[1])

        pointsLayer.clearLayers()
        linesLayer.clearLayers()

        points.forEach(point => {
            if (point.z >= zMin && point.z <= zMax) {
                /* const marker = L.circleMarker([point.y, point.x], {
                          color: point.color,
                          radius: 5,
                          weight: 1,
                      }).addTo(pointsLayer);
                      marker.bindTooltip(point.description); */
            }
        })

        lines.forEach(line => {
            if (line.z >= zMin && line.z <= zMax) {
                const polyline = L.polyline(line.points, {
                    color: line.color,
                    weight: 1,
                    smoothFactor: 0,
                    lineJoin: 'round'
                }).addTo(linesLayer)
            }
        })
    }

    /* map.on('mousemove', function (e) {
        const coordDisplay = document.getElementById('coord-display');
        coordDisplay.innerText = `X: ${e.latlng.lng}, Y: ${e.latlng.lat}`;
    });
  
    map.on('zoom', function () {
        const infoDisplay = document.getElementById('coord-display');
        infoDisplay.innerText = `Zoom Level: ${map.getZoom()}`;
    }); */

    function componentToHex(c) {
        c = typeof c === 'string' ? parseInt(c) : c
        var hex = c.toString(16)
        return hex.length == 1 ? '0' + hex : hex
    }

    function rgbToHex(r, g, b) {
        return '#' + componentToHex(r) + componentToHex(g) + componentToHex(b)
    }

    // Initialize map with default map name
    loadMap(mapBaseName)
    var gratOps = {
        interval: 200,
        showOriginLabel: false,
        redraw: 'move',
        zoomIntervals: [
            { start: -5, end: -5, interval: 2500 },
            { start: -4, end: -4, interval: 1000 },
            { start: -3, end: -2, interval: 500 },
            { start: -1, end: 0, interval: 200 },
            { start: 1, end: 1, interval: 100 },
            { start: 2, end: 3, interval: 50 },
            { start: 4, end: 10, interval: 10 }
        ]
    }
    L.simpleGraticule(gratOps).addTo(map)
    var mouseOps = {
        position: 'bottomright',
        emptyString: 'coords',
        separator: ', ',
        latFormatter: function (num) {
            var formatted = 'Y: ' + L.Util.formatNum(num, 1)
            return formatted
        },
        lngFormatter: function (num) {
            var formatted = 'X: ' + L.Util.formatNum(num, 1)
            return formatted
        }
    }
    L.control.mousePosition(mouseOps).addTo(map)
})
