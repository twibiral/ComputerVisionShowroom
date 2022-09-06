const image = document.getElementById("image");
const image_selector = document.getElementById("image-selector");
const noise_selector = document.getElementById("noise-selector");
const filter_selector = document.getElementById("filter-selector");

update_image();

function update_image() {
    console.log("Updating image.");
    image.src = `/static/generated/${image_selector.value}_${noise_selector.value}_${filter_selector.value}.png`;
}