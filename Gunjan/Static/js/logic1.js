var map = null;
var my_boundaries = {};
var data_layer;
var info_window;

//initialize map on document ready
$(document).ready(function(){
	var latlng = new google.maps.LatLng(20.723080, -73.984340); //you can use any location as center on map startup
	var myOptions = {
		zoom: 2,
		center: latlng,
		mapTypeControl: true,
		mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU},
		navigationControl: true,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	google.maps.event.addListener(map, 'click', function(){
		if(info_window){
			info_window.setMap(null);
			info_window = null;
		}
	});
	loadBoundariesFromGeoJson("https://raw.githubusercontent.com/matej-pavla/Google-Mapshttps://raw.githubusercontent.com/matej-pavla/Google-Maps-Examples/master/BoundariesExample/geojsons/us.states.geo.json");
});
function initializeDataLayer(){
	if(data_layer){
		data_layer.forEach(function(feature) {
			data_layer.remove(feature);
		});
		data_layer = null;
	}
	data_layer = new google.maps.Data({map: map}); //initialize data layer which contains the boundaries. It's possible to have multiple data layers on one map
	data_layer.setStyle({ //using set style we can set styles for all boundaries at once
		fillColor: 'white',
		strokeWeight: 1,
		fillOpacity: 0.1
	});

	data_layer.addListener('click', function(e) { //we can listen for a boundary click and identify boundary based on e.feature.getProperty('boundary_id'); we set when adding boundary to data layer
		var boundary_id = e.feature.getProperty('boundary_id');
		var boundary_name = "NOT SET";
		if(boundary_id && my_boundaries[boundary_id] && my_boundaries[boundary_id].name) boundary_name = my_boundaries[boundary_id].name;
		if(info_window){
			info_window.setMap(null);
			info_window = null;
		}
		info_window = new google.maps.InfoWindow({
			content: '<div>You have clicked a boundary: <span style="color:red;">' + boundary_name + '</span></div>',
			size: new google.maps.Size(150,50),
			position: e.latLng, map: map
		});
	});

	data_layer.addListener('mouseover', function(e) {
		data_layer.overrideStyle(e.feature, {
			strokeWeight: 3,
			strokeColor: '#ff0000'
		});
		var boundary_id = e.feature.getProperty('boundary_id');
		var boundary_name = "NOT SET";
		if(boundary_id && my_boundaries[boundary_id] && my_boundaries[boundary_id].name) boundary_name = my_boundaries[boundary_id].name;
		$('#bname').html(boundary_name);
	});

	data_layer.addListener('mouseout', function(e) {
		data_layer.overrideStyle(e.feature, {
			strokeWeight: 1,
			strokeColor: ''
		});
		$('#bname').html("");
	});
}

function loadBoundariesFromGeoJson(geo_json_url) {
	initializeDataLayer();
	$.getJSON(geo_json_url, function (data) {
		if (data.type == "FeatureCollection") { //we have a collection of boundaries in geojson format
			if (data.features) {
				for (var i = 0; i < data.features.length; i++) {
					var boundary_id = i + 1;
					var new_boundary = {};
					if (!data.features[i].properties) data.features[i].properties = {};
					data.features[i].properties.boundary_id = boundary_id; //we will use this id to identify boundary later when clicking on it
					data_layer.addGeoJson(data.features[i], {idPropertyName: 'boundary_id'});
					new_boundary.feature = data_layer.getFeatureById(boundary_id);
					if (data.features[i].properties.name) new_boundary.name = data.features[i].properties.name;
					if (data.features[i].properties.NAME) new_boundary.name = data.features[i].properties.NAME;
					my_boundaries[boundary_id] = new_boundary;
				}
			}
		}
	});
}
