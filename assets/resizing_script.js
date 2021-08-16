if (!window.dash_clientside) {
	window.dash_clientside = {};
}
window.dash_clientside.clientside = {
	resize: function(value) {
		// console.log(width);
		setTimeout(function() {
			window.dispatchEvent(new Event('resize'));
		}, 300);
		return null;
	}
};