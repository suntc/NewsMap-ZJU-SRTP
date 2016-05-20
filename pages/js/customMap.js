/*
 {"type":"FeatureCollection","features":[
	{"type":"Feature","id":"01","properties":{"name":"Alabama","value":94.65},"geometry":{"type":"Polygon","coordinates":[[[-8
*/

function medians(values) {
	mids = []
    values.sort( function(a,b) {return a - b;} );
    var upper1_8 = Math.floor(values.length * 7 / 8);
    var upper2_8 = Math.floor(values.length * 6 / 8);
    var upper3_8 = Math.floor(values.length * 5 / 8);
    var half = Math.floor(values.length/2);
    var upper5_8 = Math.floor(values.length * 3 / 8);
    var upper6_8 = Math.floor(values.length * 2 / 8);
    var upper7_8 = Math.floor(values.length * 1 / 8);

    if(values.length % 2)
        median = values[half];
    else
        median = (values[half-1] + values[half]) / 2.0;
    mids.push(values[upper1_8],values[upper2_8],values[upper3_8],median,values[upper5_8],values[upper6_8],values[upper7_8]);
    return mids;
}

function choroplethMap(mapid,mapdata)
{
	var map = L.map(mapid).setView([37.8, -96], 4);
	L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpandmbXliNDBjZWd2M2x6bDk3c2ZtOTkifQ._QA7i5Mpkd_m30IGElHziw', {
			maxZoom: 18,
			attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
				'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
				'Imagery © <a href="http://mapbox.com">Mapbox</a>',
			id: 'mapbox.street'
		}).addTo(map);

	// control that shows state info on hover
	var info = L.control();

	info.onAdd = function (map) {
			this._div = L.DomUtil.create('div', 'info');
			this.update();
			return this._div;
		};

	info.update = function (props) {
		this._div.innerHTML = '<h4>' + mapdata.title + '</h4>' +  (props ?
			'<b>' + props.name + '</b><br />' + props.value + ' ' + mapdata.metric
			: 'Hover over a state');
	};

	info.addTo(map);
	geovalues = []
	for (var i = 0; i < mapdata.geodata.features.length; ++i){
		geovalues.push(mapdata.geodata.features[i].properties.value);
	}
	mids = medians(geovalues);
	// get color depending on population density value
	function getColor(d) {
		return d > mids[0]	 ? '#800026' :
		       d > mids[1] 	 ? '#BD0026' :
		       d > mids[2] 	 ? '#E31A1C' :
		       d > mids[3]	 ? '#FC4E2A' :
		       d > mids[4]   ? '#FD8D3C' :
		       d > mids[5]   ? '#FEB24C' :
		       d > mids[6]   ? '#FED976' :
		                 	   '#FFEDA0';
	}

	function style(feature) {
		return {
			weight: 2,
			opacity: 1,
			color: 'white',
			dashArray: '3',
			fillOpacity: 0.7,
			fillColor: getColor(feature.properties.value)
		};
	}

	function highlightFeature(e) {
		var layer = e.target;

		layer.setStyle({
			weight: 5,
			color: '#666',
			dashArray: '',
			fillOpacity: 0.7
		});

		if (!L.Browser.ie && !L.Browser.opera) {
			layer.bringToFront();
		}

		info.update(layer.feature.properties);
	}

	var geojson;

	function resetHighlight(e) {
		geojson.resetStyle(e.target);
		info.update();
	}

	function zoomToFeature(e) {
		map.fitBounds(e.target.getBounds());
	}

	function onEachFeature(feature, layer) {
		layer.on({
			mouseover: highlightFeature,
			mouseout: resetHighlight,
			click: zoomToFeature
		});
	}

	geojson = L.geoJson(mapdata.geodata, {
		style: style,
		onEachFeature: onEachFeature
	}).addTo(map);

	map.attributionControl.addAttribution('Population data &copy; <a href="http://census.gov/">US Census Bureau</a>');

	/*
	var legend = L.control({position: 'bottomright'});

	legend.onAdd = function (map) {

		var div = L.DomUtil.create('div', 'info legend'),
			grades = [0, 10, 20, 50, 100, 200, 500, 1000],
			labels = [],
			from, to;

		for (var i = 0; i < grades.length; i++) {
			from = grades[i];
			to = grades[i + 1];

			labels.push(
				'<i style="background:' + getColor(from + 1) + '"></i> ' +
				from + (to ? '&ndash;' + to : '+'));
		}

		div.innerHTML = labels.join('<br>');
		return div;
	};
	*/
	legend.addTo(map);
	return map;
}