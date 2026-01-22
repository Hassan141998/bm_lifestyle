// Main JS file for BM Lifestyle

document.addEventListener('DOMContentLoaded', function () {
    console.log('BM Lifestyle initialized.');

    // Enable bootstrap tooltips if any
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
});
