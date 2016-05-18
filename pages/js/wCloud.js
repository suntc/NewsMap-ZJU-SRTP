// Global variables need here:
// var svg = d3.select("")...

var hitTest = function(elem, other_elems){	
	var overlapping = function(BBox_a, BBox_b){
	var aWidth  = BBox_a.width,
		bWidth  = BBox_b.width,
		aHeight = BBox_a.height,
		bHeight = BBox_b.height,		
		aLeft  = BBox_a.x,
		bLeft  = BBox_b.x,
		aTop   = BBox_a.y,
		bTop   = BBox_b.y;
		
		if(aLeft + aWidth > bLeft && bLeft + bWidth > aLeft)
			if(aTop + aHeight > bTop && bTop + bHeight > aTop)
				return true; 
		return false;
	};
	var i = 0;
	for (i = 0; i < other_elems.length; i++){
		if(overlapping(elem, other_elems[i])){
			return true;
		}
	}
	return false;
};
	
// this function should be bounded in an other function
var drawWordCloud = function(x, y, r, word_array, topic_name)
{	
	var BBox = function(x, y, w, h){
		this.x = x;
		this.y = y;
		this.width  = w;
		this.height = h;
	}
	
	/*for (var i = 0; i < word_array.length; i++) 
		word_array[i].weight = parseFloat(word_array[i].weight, 10);

	word_array.sort(function(a, b) { 
		if (a.weight < b.weight) {return 1;} 
		else if (a.weight > b.weight) {return -1;} 
		else {	return 0;} 
	});*/
	
	var maxWidth = 354 * 1.8;

	var wScale = d3.scale.linear().range([30,5]).domain([word_array[0].weight, word_array[word_array.length - 1].weight]); 	
	
	var step = 2.0,
		already_placed_words = [],
		aspect_ratio = 1;

	var temp = [{"id":topic_name,
					"x" : x, 
					"y" : y,
					"r" : r}];
	
	var dragCloud = function(d){
					d3.select(this).attr("transform", 
						"translate(" + ( d.x = Math.max(r - x, Math.min(svg_width  - r - x, d3.event.x - x)) ) + "," 
									 + ( d.y = Math.max(r - y, Math.min(svg_height - r - y, d3.event.y - y)) ) + ")");
				}
	var textCloud = svg.append("g")
				.data(temp)
				.attr("id", topic_name);
					
		textCloud.append("circle")
			.attr("transform","translate(" + x + "," + y + ")")
			.attr("fill","white")
			.attr("r", r);
			
	    textCloud
			.selectAll("text." + topic_name)
			.data(word_array)
			.enter()
			.append("text")
			.attr("class", topic_name)
			.each(drawOneWord);
						
	function drawOneWord(word,index)
	{	
		var $this = this;
		var word_id   = topic_name + "_word_",
		angle  = 2 * Math.PI * Math.random(),
		radius = 0.0,
		inner_html = word.text;
		weight = Math.min(wScale(word.weight),maxWidth/inner_html.length);

		d3.select(this)
			.attr("class", word_id)
			.attr("font-size", weight + "px")
			.attr("fill","#00a3d9")
			.style("cursor","pointer")
			.text(inner_html);
		
		var word_width  = this.getBBox().width,
			word_height = this.getBBox().height,
			left    =  x - word_width / 2,
			top     =  y + word_height / 2,
			diagnal	= Math.sqrt(word_width * word_width + word_height * word_height) / 2;		
				
		var hasPlaced = true;
		var posX = left,
			posY = top;
			bbox = new BBox(left, top - word_height, word_width, word_height);
			
		while(hitTest(bbox, already_placed_words))
		{
			radius += step;
			if(radius + diagnal > r){
				d3.select(this).remove();
				hasPlaced = false;
				break;
			}
			angle += (index % 2 === 0 ? 1 : -1) * step;
			bbox.x = posX = left + (radius * Math.cos(angle)) * aspect_ratio;
			posY   = top  + radius * Math.sin(angle);
			bbox.y = posY - word_height;
		}
		if(hasPlaced) {
			already_placed_words.push(bbox);
			//word.x = posX;
			//word.y = posY;
			d3.select(this)
			  .attr("transform","translate(" + posX + "," + posY + ")");
		}	
	};
}