var map = null;
var myLayer = null;
var newsStatics = {
	url	: undefined,
	recNews		: {
		general		: undefined,
		location	: undefined,
		entity		: undefined,
		topic		: undefined,
	},
}
$(document).ready(function () {
	mapInit();
	$('#submit').bind("click", parseArticle);
	$('#news-area .selectors').bind("click",recommend)
});

function mapInit() {
	// Provide your access token
	L.mapbox.accessToken = 'pk.eyJ1Ijoic3VudGMiLCJhIjoiY2lnbHd2bm9lMDE3ZnRjbTN6NmFocW40ZiJ9.a4zXk7vRisoIJ4KT-CukXA';
	// Create a map in the div #map
	map = L.mapbox.map('map', 'mapbox.streets').setView([37.9, -77],4);
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

function setText(txt)
{
	newsinfo = txt;
	$('#display').text(newsinfo["title"] + "\n" + newsinfo["date"] + "\n" + newsinfo["text"]);
}

function appendArticle(art)
{
	/*tile, text, source, pubdate*/
	var item = $("<div></div>").attr("class","news-items");
	var pic = $("<div></div>").attr("class","news-pics");
	var content = $("<div></div>").attr("class","news-content");
	var title = $("<div></div>").attr("class","news-titles").text(art.title);
	var text = $("<div></div>").attr("class","news-briefs").text(art.text);
	var source = $("<div></div>").attr("class","news-source").text(art.source);
	var pubdate = $("<div></div>").attr("class","news-pubdate").text(art.pub_date);
	content.append(title).append(text);
	item.append(pic).append(content);
	return item;
}

function recommend()
{
	if (newsStatics.url == undefined)
		return;
	btnType = $(this).attr('value')
	rectype = "null";
	if (btnType == 'normal' && newsStatics.recNews.general == undefined){
		rectype = "general";
	}
	else if (btnType == 'type2' && newsStatics.recNews.location == undefined){
		rectype = "location";
	}
	else if (btnType == 'type3' && newsStatics.recNews.entity == undefined){
		rectype = "entity";
	}
	else if (btnType == 'type4' && newsStatics.recNews.topic == undefined){
		rectype = "topic";
	}
		
	if (rectype == "null")
		return;
	
	$.ajax({
		type	: 'POST',
		url		: '/recommend/',
		data	: {type: rectype},
		success	: function(data){
			if (rectype == 'general'){
				newsStatics.recNews.general = data;
			}
			else if (rectype == 'location'){
				newsStatics.recNews.location = data;
				for (i = 0; i < data.length; ++i){
					$("#news-area .tabs[value='type2']").append(appendArticle(data[i]));
					alert("ok");
				}
			}
			else if (rectype == 'entity'){
				newsStatics.recNews.entity = data;
				for (i = 0; i < data.length; ++i){
					$("#news-area .tabs[value='type3']").append(appendArticle(data[i]));
					alert("ok");
				}
			}
			else if (rectype == 'topic'){
				newsStatics.recNews.topic = data;
				for (i = 0; i < data.length; ++i){
					$("#news-area .tabs[value='type4']").append(appendArticle(data[i]));
					alert("ok");
				}
			}

			
		}
	});
}


function parseArticle(evt)
{
	evt.preventDefault();
	newsStatics.url = undefined;
	newsStatics.recNews = {
		general		: undefined,
		location	: undefined,
		entity		: undefined,
		topic		: undefined,
	};
	newsStatics.url = $('#url-input').val();
	$.ajax({
		type	: 'GET',
		url		: '/parse/',
		data	: {input : newsStatics.url},
		success	: function(data){
			setText(data);
			recommend(data["text"]);
		}
	});
}

