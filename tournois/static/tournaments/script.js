

var map;

var markerIcon = L.icon({
    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    tooltipAnchor: [16, -28],
    shadowSize: [41, 41]
});



function success(pos){
    
    
    map = L.map('mapid',{
        minZoom: 3, 
        maxZoom: 15


    }
    
    ).setView([pos.coords.latitude, pos.coords.longitude], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    

    localisations.forEach(function(localisation) {
    var longitude = localisation.fields.latitude;
    var latitude = localisation.fields.longitude;
    L.marker([latitude, longitude])
    .addTo(map)
    .bindPopup(localisation.fields.name)
    .openPopup();
    });
    L.marker([pos.coords.latitude, pos.coords.longitude], {icon: markerIcon})
    .addTo(map)
    .bindPopup('Vous êtes ici!')
    .openPopup();
    L.control.scale().addTo(map);
    
}

function error(err){
    console.log(err);
    // Check if the error code is PERMISSION_DENIED
    if (err.code === err.PERMISSION_DENIED) {
        alert('Location is not enabled. Please enable location services to use this feature.');
    } else {
        alert('An error occurred while getting the location: ' + err.message);
    }
}

var watchID = navigator.geolocation.watchPosition(success, error, {
    enableHighAccuracy: true,
    timeout: 5000
});


//navigator.geolocation.clearWatch(watchID);