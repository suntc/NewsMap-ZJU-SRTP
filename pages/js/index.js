var mapWidgets = {
	map 	: undefined,
	myLayer : undefined,
	info 	: undefined,
	markers : [],
	hlwords : {},
	thememap: {},
};
var newsStatics = {
	url	: undefined,
	recNews		: {
		general		: undefined,
		location	: undefined,
		entity		: undefined,
		topic		: undefined,
	},
};
var svg = undefined;

$(document).ready(function () {
	mapInit();
	$('#submit').bind("click", parseArticle);
	$('#news-area .selectors').bind("click",recommend)
	$("svg g").bind("click",hlkeyword)
	//$("svg g text").bind("click",hlkeyword);
});



function mapInit() {
	// Provide your access token
	//L.mapbox.accessToken = 'pk.eyJ1Ijoic3VudGMiLCJhIjoiY2lnbHd2bm9lMDE3ZnRjbTN6NmFocW40ZiJ9.a4zXk7vRisoIJ4KT-CukXA';
	// Create a map in the div #map
	selector_selected.call($('#map-area .selectors[value="basicmap"]')[0]);
	mapWidgets.map = L.map('map').setView([37.8, -96], 4);
	L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpandmbXliNDBjZWd2M2x6bDk3c2ZtOTkifQ._QA7i5Mpkd_m30IGElHziw', {
			maxZoom: 18,
			attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
				'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
				'Imagery © <a href="http://mapbox.com">Mapbox</a>',
			id: 'mapbox.streets'
		}).addTo(mapWidgets.map);
	mapWidgets.info = L.control();
	mapWidgets.info.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
		this.update();
		return this._div;
	};
	mapWidgets.info.update = function (props) {
    	this._div.innerHTML = props;
	};
	mapWidgets.info.addTo(mapWidgets.map);
	mapWidgets.info.update("");
	svg = d3.select('#statics-area .tabs-item')
	//map = L.mapbox.map('map', 'mapbox.streets').setView([37.9, -77],4);
	//myLayer = L.mapbox.featureLayer().addTo(map);
	//myLayer.setGeoJSON(geojson);
	/*
	myLayer.on('mouseover', function(evt) {
	    evt.layer.openPopup();
	});
	myLayer.on('mouseout', function(evt) {
	    evt.layer.closePopup();
	});
*/
}

function scrollToAnchor(aid){
    var aTag = $("a[name='"+ aid +"']");
    $('html,body').animate({scrollTop: aTag.offset().top},'slow');
}

function hlkeyword()
{
	alert("ok");
}

function setText(txt)
{
	newsinfo = txt;
	$('#article-area #article-title').text(newsinfo["title"]);
	$('#article-area #article-date').text(newsinfo["date"]);
	$('#article-area #display').html(newsinfo["text"]);
	if (newsinfo["image"] != undefined){
		var pic = $("<div></div>").attr("id","article-pic");
		pic.css({
			"width"	: "60%",
			"height": "60%",
			"background-size": "cover",
			"margin": "20px 20%",
			"background-image": "url(" + newsinfo["image"] + ")",
		});
		$('#article-area #display').before(pic);
	}
}

function basicmap()
{
	$.ajax({
		url		: '/basicmap/',
		success	: function(data){
			basicMarker(data);
		}		
	});
}

function basicMarker(dat)
{
	/*
	data should be like
	{
		A: {position:[37.8, -96], description:"xxx"},
	}
	*/
	for (var key in dat)
	{
		marker = L.marker(dat[key].position).addTo(mapWidgets.map).bindPopup(key);
		marker.description = dat[key].description;
		mapWidgets.markers.push(marker);
		marker.on('mouseover',function(e){
			this.openPopup();
			mapWidgets.info.update(this.description);
		});
		marker.on('mouseout',function(e){
			this.closePopup();
			mapWidgets.info.update("");
		});
	}
}

function wordcloud()
{
	/*
	word_array should be like
	{
		A : {text: xxx, weight: 3},
		...
	}
	*/
	selector_selected.call($('#statics-area .selectors[value="wcloud"]')[0]);
	$.ajax({
		url		: '/wordcloud/',
		success	: function(word_array){
			drawWordCloud.call($("#statics-area .tabs-item[value='wcloud']")[0],177,177,177, word_array, "default");
			$('svg g text').on("click",function(e){
						$('.hl-word').each(function(d){ 
							$(this).replaceWith($(this).find('a').text());});
						$('#article-area #display').html($('#article-area #display').html().replace(new RegExp($(this).text(), 'g'),"<span class = 'hl-word' style = 'color:#EF0FFF'>" + $(this).text() +'</span>'))
						$('.hl-word').each(function(d){$(this).wrapInner('<a name="wid-' + d + '"/>' )});
						if ($("a[name = 'wid-0']")[0] != undefined){
							scrollToAnchor('wid-0');
						}	
					});
		}		
	});
}

function appendArticle(art)
{
	/*tile, text, source, pubdate*/
	if (art.text.length > 300) {
		art.text = art.text.substring(0, 300) + "...";
 	}
	var item = $("<div></div>").attr("class","news-items");
	var pic = $("<div></div>").attr("class","news-pics");
	var content = $("<div></div>").attr("class","news-content");
	var title = $("<div></div>").attr("class","news-titles").text(art.title);
	var date = $("<div></div>").attr("class","news-dates").text(art.pub_date);
	var text = $("<div></div>").attr("class","news-briefs").text(art.text);
	var source = $("<div></div>").attr("class","news-source").text(art.source);
	var pubdate = $("<div></div>").attr("class","news-pubdate").text(art.pub_date);
	content.append(title).append(date).append(text);
	item.append(content);
	return item;
}

function calcinfo()
{
	$.ajax({
		url		: '/calcinfo/',
		success	: function(data){
			basicmap();
			thememap();
			wordcloud();
			recommend("general");
		}		
	});
}

function thememap()
{
	$.ajax({
		url		: '/thememap/',
		success	: function(data){
			for (var i = 0; i < data.length; ++i){
				var button = $("<div></div>").attr("class","selectors btn").attr("value","type" + (i+1)).text("类型"+(i+1));
				//button[0].onclick = selector_selected;
				var tab = $("<div></div>").attr("class","tabs").attr("value","type" + (i+1));
				var m = $("<div></div>").attr("id","type" + (i+1)).css({"width":"100%","height":"444px"});
				mapWidgets.thememap["type" + (i+1)] = data[i];
				$("#map-area .selectors-sets").append(button);
				tab.append(m);
				$("#map-area .tabs-sets").append(tab);
				button[0].onclick = genmap;
			}
			
		}		
	});
}

function genmap(){
	/*
		fetch map's information through $(this).attr('value')
		which is button's value type2, type3...

	*/
	mapid = $(this).attr('value');
	selector_selected.call(this);
	var tmap = choroplethMap(mapid,mapWidgets.thememap[mapid]);
	//mapWidgets.thememap.push(tmap);
	/*
	var tmap = L.map(mapid).setView([37.8, -96], 4);
	L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpandmbXliNDBjZWd2M2x6bDk3c2ZtOTkifQ._QA7i5Mpkd_m30IGElHziw', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
			'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			'Imagery © <a href="http://mapbox.com">Mapbox</a>',
		id: 'mapbox.streets'
	}).addTo(tmap);
*/
}


function recommend()
{
	if (newsStatics.url == undefined)
		return;
	if (typeof(arguments[0]) != "string"){
		btnType = $(this).attr('value');
	}
	else{
		btnType = arguments[0];
		selector_selected.call($('#news-area .selectors[value="' + arguments[0] + '"]')[0]);
	}
	rectype = "null";
	if (btnType == 'general' && newsStatics.recNews.general == undefined){
		rectype = "general";
	}
	else if (btnType == 'location' && newsStatics.recNews.location == undefined){
		rectype = "location";
	}
	else if (btnType == 'entity' && newsStatics.recNews.entity == undefined){
		rectype = "entity";
	}
	else if (btnType == 'topic' && newsStatics.recNews.topic == undefined){
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
				for (i = 0; i < data.length; ++i){
					$("#news-area .tabs[value='general']").append(appendArticle(data[i]));
				}
			}
			else if (rectype == 'location'){
				newsStatics.recNews.location = data;
				for (i = 0; i < data.length; ++i){
					$("#news-area .tabs[value='location']").append(appendArticle(data[i]));
				}
			}
			else if (rectype == 'entity'){
				newsStatics.recNews.entity = data;
				for (i = 0; i < data.length; ++i){
					$("#news-area .tabs[value='entity']").append(appendArticle(data[i]));
				}
			}
			else if (rectype == 'topic'){
				newsStatics.recNews.topic = data;
				for (i = 0; i < data.length; ++i){
					$("#news-area .tabs[value='topic']").append(appendArticle(data[i]));
				}
			}

			
		}
	});
}


function parseArticle(evt)
{
	evt.preventDefault();
	//clear
	newsStatics.url = undefined;
	newsStatics.recNews = {
		general		: undefined,
		location	: undefined,
		entity		: undefined,
		topic		: undefined,
	};
	mapWidgets.map.setView([37.8, -96], 4);
	$('#article-area #article-pic').remove();
	$("#news-area .tabs[value='general']").empty();
	$("#news-area .tabs[value='location']").empty();
	$("#news-area .tabs[value='entity']").empty();
	$("#news-area .tabs[value='topic']").empty();
	for (var i = 0; i < mapWidgets.markers.length; ++i){
		mapWidgets.map.removeLayer(mapWidgets.markers[i]);
	}
	mapWidgets.markers = [];
	mapWidgets.thememap = {};
	$('#map-area .selectors[value="basicmap"]').siblings().each(function(){$(this).remove()});
	$('#map-area .tabs[value="basicmap"]').siblings().each(function(){$(this).remove()});

	newsStatics.url = $('#url-input').val();
	$.ajax({
		type	: 'GET',
		url		: '/parse/',
		data	: {input : newsStatics.url},
		success	: function(data){
			setText(data);
			calcinfo();
		}
	});
}

