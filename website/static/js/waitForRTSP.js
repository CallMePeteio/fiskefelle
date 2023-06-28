var img = document.getElementById('rtspStreamImg');

function loadImage() {
    var random = Math.random();
    img.src = '/rtspStream?' + random;
}

img.onerror = function() {
    setTimeout(loadImage, 500);
};

loadImage();