document.onreadystatechange = style_initialize;

function style_initialize() {
	if (document.readyState === 'complete') {
		var selectors = document.querySelectorAll('.selectors');
		for (var i in selectors) {
			var selector = selectors[i];
			selector.onclick = selector_selected;
		}
	}
}

function selector_selected() {
	console.log('selector selected');

	var selectors = this.parentNode.childNodes;
	var tabs = null;
	try {
		tabs = this.parentNode.parentNode.querySelector('.tabs-sets').childNodes;
	} catch (e) {

	}


	for (var i in selectors) {
		var node = selectors[i];
		if (node.classList !== undefined) {
			node.classList.remove('selectors-selected');
		}
	}

	for (var i in tabs) {
		var node = tabs[i];
		if (node.classList !== undefined) {
			node.classList.remove('tabs-selected');
		}
	}

	this.classList.add('selectors-selected');

	for (var i in tabs) {
		var node = tabs[i];
		try {
			if (node.attributes.value.value === this.attributes.value.value) {
				node.classList.add('tabs-selected');
				break;
			}
		} catch (e) {

		}
	}
}
