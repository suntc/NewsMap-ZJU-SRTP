var map = null;
var myLayer = null;

$(document).ready(function () {
	mapInit();
	$('#submit').bind("click", marker_gen);
});

function mapInit() {
	// Provide your access token
	L.mapbox.accessToken = 'pk.eyJ1Ijoic3VudGMiLCJhIjoiY2lnbHd2bm9lMDE3ZnRjbTN6NmFocW40ZiJ9.a4zXk7vRisoIJ4KT-CukXA';
	// Create a map in the div #map
	map = L.mapbox.map('map', 'mapbox.streets');
	myLayer = L.mapbox.featureLayer().addTo(map);
	/*var geojson = {
	    type: 'FeatureCollection',
	    features: [{
	        type: 'Feature',
	        properties: {
	            title: 'Washington, D.C.',
	            'marker-color': '#f86767',
	            'marker-size': 'large',
	            'marker-symbol': 'star',
	            url: 'http://en.wikipedia.org/wiki/Washington,_D.C.'
	        },
	        geometry: {
	            type: 'Point',
	            coordinates: [-77.03201, 38.90065]
	        }
	    },
	    {
	        type: 'Feature',
	        properties: {
	            title: 'Baltimore, MD',
	            'marker-color': '#7ec9b1',
	            'marker-size': 'large',
	            'marker-symbol': 'star',
	            url: 'http://en.wikipedia.org/wiki/Baltimore'
	        },
	        geometry: {
	            type: 'Point',
	            coordinates: [-76.60767, 39.28755]
	        }
	    }]
	};
	myLayer.setGeoJSON(geojson);
	myLayer.on('mouseover', function(evt) {
	    evt.layer.openPopup();
	});
	myLayer.on('mouseout', function(evt) {
	    evt.layer.closePopup();
	});*/
}

function marker_gen(evt) {
	evt.preventDefault();
	var input = $('#input').val();
	alert(input);
	$.ajax({
		type	: 'GET',
		url		: '/parse/',
		data	: input,
		success	: function(data) {
			alert(data);
			myLayer.setGeoJSON(data);
			myLayer.on('mouseover', function(evt) {
			    evt.layer.openPopup();
			});
			myLayer.on('mouseout', function(evt) {
			    evt.layer.closePopup();
			});
		}
	});
}
