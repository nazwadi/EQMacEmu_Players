document.addEventListener('DOMContentLoaded', function () {
    let minX = 0;
    let minY = 0;
    let maxX = 0;
    let maxY = 0;

    const konvaContainer = document.getElementById('konva-container');
    const stage = new Konva.Stage({
        container: konvaContainer,
        width: konvaContainer.clientWidth,
        height: konvaContainer.clientHeight,
        scale: { x: 0.5, y: 0.5 } // Set the initial zoom level
    });

    stage.position({
        x: stage.width() / 2,
        y: stage.height() / 2,
    });

    if (typeof creatureSpawnPoints !== 'undefined') {
        if (creatureSpawnPoints.length > 0) {
            const firstSpawnPoint = creatureSpawnPoints[0];
            stage.position({
                x: stage.width() / 2 - firstSpawnPoint.x * stage.scaleX(),
                y: stage.height() / 2 - firstSpawnPoint.y * stage.scaleY(),
            });
        }
    }

    const layer = new Konva.Layer(); // Move the layer declaration here
    stage.add(layer);

    // Add event listener for line weight slider
    const lineWeightSlider = document.getElementById('lineWeight');
    lineWeightSlider.addEventListener('input', function () {
        const newLineWeight = parseInt(lineWeightSlider.value);

        // Update the line weight for all lines on the Konva layer
        layer.find('Line').forEach(line => {
            line.strokeWidth(newLineWeight);
        });

        // Redraw the layer
        layer.draw();
    });

    // Add event listener for show/hide points toggle
    const showPointsToggle = document.getElementById('showPoints');
    showPointsToggle.addEventListener('change', function () {
        const showPoints = showPointsToggle.checked;

        // Set visibility for all circles on the Konva layer
        layer.find('Circle').forEach(circle => {
            if (circle.isCreatureSpawnPoint) {
                // Adjust the visibility based on the showPoints status
                circle.visible(showPoints);
            } else {
                // Adjust visibility for non-creature points based on the showPoints status
                circle.visible(showPoints);
            }
        });

        // Set visibility for all labels on the Konva layer
        layer.find('Text').forEach(label => {
            // Adjust visibility for labels based on the showPoints status
            label.visible(showPoints);
        });

        // Redraw the layer
        layer.draw();
    });

    // Redraw layer
    layer.draw();

    // path points
    // Plot creature paths
    const pathLineColor = 'cyan';
    const pathLineStrokeWidth = 2;

    // Ensure creaturePathPoints is defined
    if (typeof creaturePathPoints !== 'undefined') {
        Object.values(creaturePathPoints).forEach(creaturePath => {
            for (let i = 1; i < creaturePath.length; i++) {
                const startPoint = creaturePath[i - 1];
                const endPoint = creaturePath[i];

                //console.log('Start Point:', startPoint);
                //console.log('End Point:', endPoint);

                const konvaLine = new Konva.Line({
                    points: [startPoint.x, startPoint.y, endPoint.x, endPoint.y],
                    stroke: pathLineColor,
                    strokeWidth: pathLineStrokeWidth,
                    lineCap: 'round',
                    lineJoin: 'round',
                    dash: [5, 5],
                });

                layer.add(konvaLine);
            }
        });

        // Ensure that paths are drawn in the correct order
        layer.draw();
    }

    stage.add(layer);

    /* const mapBaseName = JSON.parse('{{ content[0].short_name|tojson }}'); */
    //let minX = Infinity;
    //let minY = Infinity;
    //let maxX = -Infinity;
    //let maxY = -Infinity;


    let lastPosX;
    let lastPosY;

    function loadMap(mapBaseName) {
        const fileNames = [
            `/static/assets/maps/${mapBaseName}.txt`,
            `/static/assets/maps/${mapBaseName}_1.txt`,
            `/static/assets/maps/${mapBaseName}_2.txt`,
            `/static/assets/maps/${mapBaseName}_3.txt`
        ];

        // Use Promise.all to wait for all file loading to complete
        Promise.all(fileNames.map(fileName => loadFile(fileName)))
            .then(() => {
                //console.log('Overall bounds:', minX, minY, maxX, maxY);

                // Set initial visibility for all circles and labels on the Konva layer
                layer.find('Circle').forEach(circle => {
                    circle.visible(false);
                });

                layer.find('Text').forEach(label => {
                    label.visible(false);
                });

                // Redraw the layer
                layer.draw();
                drawGraticule(layer, 200, stage, minX, minY, maxX, maxY);
            });
    }

    function loadFile(fileName) {
        return fetch(fileName)
            .then(response => response.text())
            .then(content => {
                const { lines, points } = createLinesAndPointsFromContent(content);

                // Draw lines on the Konva layer
                lines.forEach(line => {
                    const konvaLine = new Konva.Line({
                        points: line.points,
                        stroke: line.color,
                        strokeWidth: 2,
                        lineCap: 'round',
                        lineJoin: 'round',
                    });
                    layer.add(konvaLine);
                });

                // Draw points on the Konva layer
                points.forEach(point => {
                    const konvaCircle = new Konva.Circle({
                        x: point.x,
                        y: point.y,
                        radius: 5, // Adjust the radius as needed
                        fill: point.color,
                    });

                    layer.add(konvaCircle);

                    // Add label
                    const label = new Konva.Text({
                        x: point.x, // Adjust label position
                        y: point.y, // Adjust label position
                        text: (point.description).replace(/_/g, ' '),
                        fontSize: 12,
                        fill: point.color,
                        align: 'left', // Align the text to the left of the position
                    });

                    // Adjust label position relative to the circle's center
                    label.x(point.x + 10);
                    label.y(point.y);

                    layer.add(label);
                });
                // Redraw the layer
                layer.draw();

            })
            .catch(error => {
                console.error(`Error fetching or parsing file ${fileName}:`, error);
            });
    }


    function updateOverallBounds(lines, points) {
        const allCoordinates = [
            ...lines.flatMap(line => line.points),
            ...points.flatMap(point => [point.x, point.y]),
        ];

        minX = Math.min(minX, ...allCoordinates.filter((_, index) => index % 2 === 0));
        minY = Math.min(minY, ...allCoordinates.filter((_, index) => index % 2 !== 0));
        maxX = Math.max(maxX, ...allCoordinates.filter((_, index) => index % 2 === 0));
        maxY = Math.max(maxY, ...allCoordinates.filter((_, index) => index % 2 !== 0));
    }

    function convertColorToKonvaFormat(rgbColor) {
        const parts = rgbColor.match(/\d+/g);
        if (!parts) {
            return 'black'; // Default to black if the color is not in the expected format
        }

        const [r, g, b] = parts;
        return `rgb(${r}, ${g}, ${b})`;
    }


    function createLinesAndPointsFromContent(content) {
        const lines = [];
        const points = [];
        const linesData = content.split('\n');

        linesData.forEach(lineData => {
            const parts = lineData.trim().split(/\s+/);
            const type = parts[0];

            if (type === 'L') {
                const x1 = parseFloat(parts[1]);
                const y1 = parseFloat(parts[2]);
                const x2 = parseFloat(parts[4]);
                const y2 = parseFloat(parts[5]);

                // Update overall bounds
                minX = Math.min(minX, x1, x2);
                minY = Math.min(minY, y1, y2);
                maxX = Math.max(maxX, x1, x2);
                maxY = Math.max(maxY, y1, y2);

                const color = convertColorToKonvaFormat(`rgb(${parts[7]}, ${parts[8]}, ${parts[9]})`);

                lines.push({
                    points: [x1, y1, x2, y2],
                    color: color,
                });
            } else if (type === 'P') {
                const x = parseFloat(parts[1]);
                const y = parseFloat(parts[2]);
                const description = parts.slice(8).join(' ');

                // Update overall bounds
                minX = Math.min(minX, x);
                minY = Math.min(minY, y);
                maxX = Math.max(maxX, x);
                maxY = Math.max(maxY, y);
                // console.log("max:", maxX, "max:", maxY)
                const color = convertColorToKonvaFormat(`rgb(${parts[4]}, ${parts[5]}, ${parts[6]})`);

                points.push({
                    x: x,
                    y: y,
                    color: color,
                    description: description,
                });
            }
        });

        return { lines: lines, points: points };
    }

    // Graticule function
    function drawGraticule(layer, gridSize, stage, minX, minY, maxX, maxY) {
        // console.log("They callin me")
        const gridLineColor = 'rgba(0, 0, 0, 0.2)';
        const gridLineWidth = 1;

        // Calculate the scaled grid size
        const scaledGridSize = gridSize * stage.scaleX();

        // Calculate the starting point of the graticule
        const startXAt = minX + Math.abs(minX % scaledGridSize);
        const startYAt = minY + Math.abs(minY % scaledGridSize);

        // Draw vertical lines
        let xMark = startXAt;
        while (xMark < maxX) {
            const konvaLine = new Konva.Line({
                points: [xMark, minY, xMark, maxY],
                stroke: gridLineColor,
                strokeWidth: gridLineWidth,
            });
            layer.add(konvaLine);

            xMark += scaledGridSize;
        }

        // Draw horizontal lines
        let yMark = startYAt;
        while (yMark < maxY) {
            const konvaLine = new Konva.Line({
                points: [minX, yMark, maxX, yMark],
                stroke: gridLineColor,
                strokeWidth: gridLineWidth,
            });
            layer.add(konvaLine);

            yMark += scaledGridSize;
        }
        layer.find('Line').forEach(line => {
            line.moveToBottom();
        });
    }

    // Add event listener for zooming
    konvaContainer.addEventListener('wheel', function (e) {
        e.preventDefault();

        // Get the current mouse pointer position relative to the container
        const mouseX = e.clientX - konvaContainer.getBoundingClientRect().left;
        const mouseY = e.clientY - konvaContainer.getBoundingClientRect().top;

        // Calculate new scale based on wheel movement
        const scaleChange = e.deltaY > 0 ? 0.9 : 1.1; // Adjust the scale change factor as needed
        const newScaleX = stage.scaleX() * scaleChange;
        const newScaleY = stage.scaleY() * scaleChange;

        // Calculate the new position to keep the mouse pointer at the same position after zooming
        const newX = mouseX - (mouseX - stage.x()) * scaleChange;
        const newY = mouseY - (mouseY - stage.y()) * scaleChange;

        // Set new scale and position for the stage
        stage.scale({ x: newScaleX, y: newScaleY });
        stage.position({
            x: newX,
            y: newY,
        });

        // Redraw the layer
        layer.draw();
    });

    // Add event listeners for panning
    konvaContainer.addEventListener('mousedown', function (e) {
        lastPosX = e.clientX;
        lastPosY = e.clientY;
    });

    konvaContainer.addEventListener('mousemove', function (e) {
        if (lastPosX !== undefined && lastPosY !== undefined) {
            const deltaX = e.clientX - lastPosX;
            const deltaY = e.clientY - lastPosY;

            const newPos = {
                x: stage.x() + deltaX / stage.scaleX(),
                y: stage.y() + deltaY / stage.scaleY(),
            };

            stage.position(newPos);

            lastPosX = e.clientX;
            lastPosY = e.clientY;

            layer.draw();
        }
    });

    konvaContainer.addEventListener('mouseup', function () {
        lastPosX = undefined;
        lastPosY = undefined;
    });
    function loadCreatureSpawnPoints(layer, spawnPoints) {
        spawnPoints.forEach(point => {
            const konvaRing = new Konva.Ring({
                x: point.x,
                y: point.y,
                innerRadius: 10,
                outerRadius: 25,
                fill: '#cedff2',
                stroke: 'black',
                strokeWidth: 4,
            });

            // Set isCreatureSpawnPoint property to true
            konvaRing.isCreatureSpawnPoint = true;

            layer.add(konvaRing);


            var period = 4000;

            var anim = new Konva.Animation(function (frame) {
                var scale = Math.sin((frame.time * 2 * Math.PI) / period) + 0.001;
                // scale x and y
                konvaRing.scale({ x: scale, y: scale });

            }, layer);

            anim.start();

            // Add label or other details if needed...
        });

        // Move creature spawn points to the front
        layer.find('.isCreatureSpawnPoint').forEach(ring => {
            ring.moveToTop();
        });

        // Set visibility to true for creature spawn points
        layer.find('.isCreatureSpawnPoint').forEach(ring => {
            ring.visible(true);
        });

        // Redraw the layer after adding all points
        layer.draw();
    }

    loadMap(mapBaseName);
    if (typeof creatureSpawnPoints !== 'undefined') {
        loadCreatureSpawnPoints(layer, creatureSpawnPoints);
    }
});
