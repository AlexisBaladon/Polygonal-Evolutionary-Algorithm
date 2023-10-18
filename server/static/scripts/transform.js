
let currentGeneration = 1
let generations = null
let userId = null

function initialize(ngen, userId_) {
    generations = ngen
    userId = userId_
    fetchNextGeneration(userId)
}

function appendImage(imageData, fitness) {
    const individualContainer = document.getElementById('individual-container');
    let imageContainer = document.getElementById('images-container')

    if (imageContainer == null) {
        imageContainer = document.createElement('div');
        imageContainer.id = 'images-container';
        individualContainer.appendChild(imageContainer);
    }
    
    const imageObject = document.createElement('img');
    imageObject.src = 'data:image/png;base64,' + imageData;
    imageObject.className = 'individual-image'

    const imageOverlay = document.createElement('div');
    imageOverlay.className = 'overlay';
    imageOverlay.textContent = 'Loss: ' + fitness.toString().slice(0, 6);
    
    const hoverImageContainer = document.createElement('div');
    hoverImageContainer.className = 'hover-image-container';
    
    hoverImageContainer.appendChild(imageOverlay);
    hoverImageContainer.appendChild(imageObject);
    imageContainer.appendChild(hoverImageContainer);
}

function createProgressBar() {
    const container = document.getElementById('individual-container')
    const progressBarContainer = document.createElement('div');
    progressBarContainer.className = 'loading-bar';
    const progressBar = document.createElement('div');
    progressBar.className = 'progress';
    progressBar.id = 'progress'
    
    const progressLabel = document.createElement('span');
    progressLabel.id = 'progress-label'
    progressLabel.textContent = 'Generation: 1/' + generations.toString();

    container.appendChild(progressLabel)
    container.appendChild(progressBar)
}

function updateProgressBar(currentGeneration) {
    const progress = document.getElementById('progress');
    const progressLabel = document.getElementById('progress-label');
    const percentage = (currentGeneration / generations) * 100;

    progress.style.width = percentage + '%';
    progressLabel.textContent = 'Generation: ' + currentGeneration.toString() + '/' + generations.toString();
}

function addImage(imageData, currentGeneration) {
    fitnesses = imageData.fitness.map((x) => x[0])
    imageData = imageData.images

    /* Sort Data by fitness */
    const fitnessData = [];
    for (let i = 0; i < fitnesses.length; i++) {
        fitnessData.push({fitness: fitnesses[i], image: imageData[i]});
    }
    fitnessData.sort(function(a, b) {return a.fitness - b.fitness;});
    fitnesses = fitnessData.map(a => a.fitness);
    imageData = fitnessData.map(a => a.image);

    /* Create progress bar */
    const imageContainer = document.getElementById('individual-container');
    const generationTitleElement = document.getElementById('progress');

    if (generationTitleElement == null) {
        while (imageContainer.children.length > 0) {
            imageContainer.removeChild(imageContainer.children[0]);
        }

        createProgressBar()
    }
    else {
        updateProgressBar(currentGeneration)
    }

    imageElements = Array.from(imageContainer.getElementsByTagName('img'));
    if (imageElements.length == 0) {
        imageData.forEach((img, i) => appendImage(img, fitnesses[i]))
    }
    else {
        imageElements.forEach((imageElement, i) => {
            imageElement.src = 'data:image/png;base64,' + imageData[i];
        })
        const overlays = Array.from(imageContainer.getElementsByClassName('overlay'));
        overlays.forEach((overlay, i) => {
            overlay.textContent = 'Loss: ' + fitnesses[i].toString().slice(0, 6);
        })
    }
}

function fetchNextGeneration(userId, currentGeneration=1) {
    fetch(`/transform?generation=${currentGeneration.toString()}&user_id=${userId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => addImage(data, currentGeneration))
    .then(() => {
        if (currentGeneration <= generations) {
            fetchNextGeneration(userId, currentGeneration + 1)
        }
    })
}
