console.log("Javascript OK");

var base_url = "";
if (window.location.href.substr(0, 22) == "http://127.0.0.1:8000/") {
    base_url = "http://127.0.0.1:8000";
}
else {
    base_url = "http://51.158.69.199";
}


$(document).ready(function(){

var location_input=$('input[id="id_search"]');
location_input.autocomplete({
    source: base_url + "/api/get_products/",
    minLength: 2,
    });

//   keeps same width as box
jQuery.ui.autocomplete.prototype._resizeMenu = function () {
    var ul = this.menu.element;
    ul.outerWidth(this.element.outerWidth());
  }

});

