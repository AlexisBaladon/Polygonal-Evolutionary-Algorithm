const userId = Date.now().toString(36)
document.getElementById('transform-form').action += `?user_id=${userId}`

const imageInput = document.getElementById('image');
const imagePreview = document.getElementById('image-preview');

imageInput.addEventListener('change', function () {
const file = imageInput.files[0];

if (file) {
    const reader = new FileReader();

    reader.onload = function (e) {
        imagePreview.src = e.target.result;
    };

    reader.readAsDataURL(file);
} else {
    imagePreview.src = '';
}
});

// Event handler for tournament size
const selection = document.getElementsByName('selection')[0];
selection.onchange = function() {
    const tournamentSize = document.getElementById('tournament-size-subgroup');
    if (selection.value === 'tournament') {
        tournamentSize.style.display = 'flex';
    } else {
        tournamentSize.style.display = 'none';
    }
}