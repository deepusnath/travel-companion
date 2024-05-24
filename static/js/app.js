function initialize() {
    var inputStart = document.getElementById('start');
    var inputDestination = document.getElementById('destination');
    new google.maps.places.Autocomplete(inputStart);
    new google.maps.places.Autocomplete(inputDestination);
}

google.maps.event.addDomListener(window, 'load', initialize);

function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

document.getElementById('routeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    showLoading();
    // Add your route calculation logic here
});
