var namespace = '/tweets',
    marker = '',
    tweetCounts = 0,
    CONFIG = {
        defaultMap: {
            // Metro manila coordinates
            zoom: 9,
            lat: 14.5833,
            lng: 120.984222
        },
        newMap: {
            zoom: {
                viewport: 9,
                location: 17
            }
        },
        infoWindow: {
            maxWidth: 200,
            content: function(data) {
                var arr = [
                    '<img src="'+ data.user.profile_image_url +'" style="float:left; padding: 5px;" />',
                    '<strong>'+ data.user.screen_name +'</strong>: '+ data.text
                ];

                return arr.join('');
            }
        },
        socketUrl: document.domain + ':' + location.port + namespace
    };

$(function() {
    // Initialize map
    var map = new google.maps.Map($('#map')[0], {
        zoom: CONFIG.defaultMap.zoom,
        center: {
            lat: CONFIG.defaultMap.lat,
            lng: CONFIG.defaultMap.lng
        },
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }),

    // Define one infoWindow variable
    infoWindow = new google.maps.InfoWindow({
        maxWidth: CONFIG.infoWindow.maxWidth
    }),

    // Geocoder definition
    geocoder = new google.maps.Geocoder(),

    // Initialize socket connection
    socket = io.connect(CONFIG.socketUrl);
    console.log(CONFIG.socketUrl);

    // Stream tweets
    socket.on('tweet', function(data) {
        if (data.coordinates !== null) {
            var loc1 = data.coordinates.coordinates[1],
                loc0 = data.coordinates.coordinates[0];

            // Make marker global so that it can be accessed when changing locations to remove all existing markers
            marker = new google.maps.Marker({
                position: new google.maps.LatLng(loc1, loc0),
                animation: google.maps.Animation.DROP,
                map: map
            });

            if (marker) {
                // Static tweet counts
                $('#tweet-counts span').text(tweetCounts += 1);    
            }

            // Remove marker after 1m
            setTimeout(function() {
                marker.setMap(null);
                delete marker;
            }, 60000);

            // Show infoWindow
            google.maps.event.addListener(marker, 'mouseover', function() {
                infoWindow.setContent(CONFIG.infoWindow.content(data));
                infoWindow.open(map, this);
            });
        }
    });

    // Initialize autocomplete for search
    var autocomplete = new google.maps.places.Autocomplete(
        ($('#autocomplete')[0]),
        {types: ['geocode']}
    );

    // User selects an address from the dropdown
    autocomplete.addListener('place_changed', function(data, i) {
        var place = autocomplete.getPlace();

        console.log(place.formatted_address);

        if (!place.geometry) {
            window.alert('Autocomplete\'s returned place contains no geometry');
        } else if (place.geometry.viewport) {
            // Refresh map display w/ the new location
            map.fitBounds(place.geometry.viewport);
            map.setZoom(CONFIG.newMap.zoom.viewport);
        } else {
            // Refresh map display w/ the new location
            // More spefific locations
            map.setCenter(place.geometry.location);
            map.setZoom(CONFIG.newMap.zoom.location);
        }

        geocoder.geocode({'address': place.formatted_address}, function(results, status) {
            if (status === google.maps.GeocoderStatus.OK) {
                if (!results[0].geometry.bounds) {
                    alert('Location geometry bounds not found');
                } else {
                    var bounds = results[0].geometry.bounds,
                        boundsObj = {
                            'sw': {
                                'lng': bounds.j.j,
                                'lat': bounds.N.N
                            },
                            'ne': {
                                'lng': bounds.j.N,
                                'lat': bounds.N.j
                            }
                        };

                    console.log(boundsObj);

                    $.ajax({
                        type: 'POST',
                        contentType: 'application/json',
                        dataType: 'json',
                        url: '/change_location',
                        data: JSON.stringify(boundsObj),
                        success: function(data) {
                            console.log('server response');
                            console.log(data);

                            // Close all existing markers and infoWindow
                            infoWindow.close()
                            if (marker) {
                                marker.setMap(null);
                                delete marker;                                
                            }
                        }
                    });
                }
            } else {
                alert('Geocode was not successful for the following reason: ' + status);
            }

        });
    });

    // Show search autocomplete
    $('input').focus(function() {
        if (navigator.geolocation) { 
            navigator.geolocation.getCurrentPosition(function(position) {
                var geolocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };

                var circle = new google.maps.Circle({
                    center: geolocation,
                    radius: position.coords.accuracy
                });
                autocomplete.setBounds(circle.getBounds());
            });
        }
    });    
});