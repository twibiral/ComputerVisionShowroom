update_image();

function update_image() {
    const original_image = document.getElementById("image");
    const filtered_image = document.getElementById("filtered");
    const use_bw_images = document.getElementById("use-bw-images-cb");
    const show_original = document.getElementById("show-original-cb");

    const image_selector = document.getElementById("image-selector");
    const noise_selector = document.getElementById("noise-selector");
    const filter_selector = document.getElementById("filter-selector");

    console.log("Updating image.");
    const bw_or_color = use_bw_images.checked ? "_bw" : "";
    filtered_image.src = `generated/${image_selector.value}${bw_or_color}_${noise_selector.value}_${filter_selector.value}.png`;

    original_image.src = `generated/${image_selector.value}.png`;
    if (show_original.checked) {
        original_image.parentElement.removeAttribute("hidden");
        original_image.parentElement.style.display = "block";
    } else {
        original_image.parentElement.attributes.setNamedItem(document.createAttribute("hidden"));
        original_image.parentElement.style.display = "none";
    }
}
