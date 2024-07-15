<meta charset="UTF-8">
<script src="jquery.js"></script>
<link href="style.css?i=1" rel="stylesheet">

<label class="file_upload">
	<input type="file" id="image_input" accept="image/*" multiple="true">                                                                                                                                          
	<div id="browser" class="button">Загрузить фото в браузер</div>
</label>			


<form id="add_ob">
	<div class="photo_div" id="photos"></div>
</form>


<div id="button" class="button" style="display:none;" onClick="add_ob()">Передача данных на сервер</div>
<div id="res" class="photo_div"></div>


<script>

var MAX_WIDTH = 800; // макс. ширина большого фото
var MAX_HEIGHT = 800; // макс. высота большого фото

var MAX_WIDTH_PREVIEW = 200; // макс. ширина превьюшки
var MAX_HEIGHT_PREVIEW = 200; // макс. высота превьюшки

var yes_preview = 1; // 1 - загружаются большие фото и превьюшки; 0 - только большие фото
var max_file = 10; // максимально разрешенное количество загружаемых фото;

var x = 0;
var cou_browser = 0;
var cou = 0;
var posled =0;
var razn = 0;

var imgInput = document.getElementById('image_input');
imgInput.addEventListener('change', function (e) {
	
	if (e.target.files) {
	
		if(cou_browser < max_file)
		document.getElementById('browser').innerHTML = 'Идет загрузка в браузер ...';
		else
		document.getElementById('browser').innerHTML = 'Лимит загрузки ('+max_file+' фото) исчерпан';
		
		document.getElementById('button').style.display = '';
		
		var arr = e.target.files;
		cou = arr.length;
		razn = x - cou_browser;
		if(cou_browser + cou < max_file)
		posled = cou_browser + cou + razn;
		else
		posled = max_file + razn;

		$.each(arr, function(i, fil) {  
		var imageFile = fil;
		var reader = new FileReader();
		reader.onload = function (e) {
			
			if(cou_browser >= max_file)
				{
				return false;
				}

			cou_browser++;
			x++;
			var j = x;
			//////////////////////
			var img = document.createElement("img");

			var div = document.createElement("div");
			div.id = 'div_'+j;
			div.classList.add("photo_item");
			document.querySelector('#photos').appendChild(div);
			
			var imgt = document.createElement("img");
			imgt.id = 'preview_'+j;
			document.getElementById('div_'+j).appendChild(imgt);
			
			var input = document.createElement("input");
			input.id = 'images_'+j;
			input.name = "images[]";
			input.type = "hidden";
			document.getElementById('div_'+j).appendChild(input);
			
			var del = document.createElement("div");
			del.classList.add("photo_del");
			del.addEventListener('click', function () {dimg(j); });
			document.getElementById('div_'+j).appendChild(del);
			///////////////////
			
			////////// preview /////////
			if(yes_preview)
				{
				var input_preview = document.createElement("input");
				input_preview.id = 'images_preview_'+j;
				input_preview.name = "images_preview[]";
				input_preview.type = "hidden";
				document.getElementById('div_'+j).appendChild(input_preview);
				}
			
			img.onload = function (event) {
				var canvas = document.createElement("canvas");
				canvas.id = 'canvas_'+j;

				var width = img.width;
				var height = img.height;
				
				if (width > height) 
					{
					if (width > MAX_WIDTH) 
						{
						height = height * (MAX_WIDTH / width);
						width = MAX_WIDTH;
						}
					} 
				else 
					{
					if (height > MAX_HEIGHT) 
						{
						width = width * (MAX_HEIGHT / height);
						height = MAX_HEIGHT;
						}
					}

				canvas.width = width;
				canvas.height = height;

				var ctx = canvas.getContext("2d");
				ctx.drawImage(img, 0, 0, width, height);
				var dataurl = canvas.toDataURL('image/jpeg');
				
				document.getElementById('images_'+j).value = dataurl;
				document.getElementById("preview_"+j).src = dataurl;
				
				////////// preview ///////////
				if(yes_preview)
					{
					var canvas = document.createElement("canvas");
					canvas.id = 'canvas_preview_'+j;
	
					var width = img.width;
					var height = img.height;
					
					if (width > height) 
						{
						if (width > MAX_WIDTH_PREVIEW) 
							{
							height = height * (MAX_WIDTH_PREVIEW / width);
							width = MAX_WIDTH_PREVIEW;
							}
						} 
					else 
						{
						if (height > MAX_HEIGHT_PREVIEW) 
							{
							width = width * (MAX_HEIGHT_PREVIEW / height);
							height = MAX_HEIGHT_PREVIEW;
							}
						}
	
					canvas.width = width;
					canvas.height = height;
	
					var ctx = canvas.getContext("2d");
					ctx.drawImage(img, 0, 0, width, height);
					var dataurl = canvas.toDataURL('image/jpeg');
					document.getElementById('images_preview_'+j).value = dataurl;
					}
				if(x==posled)
					{
					document.getElementById('browser').innerHTML = 'Загрузить фото в браузер';
					}
				}
			img.src = e.target.result;
			}
		reader.readAsDataURL(imageFile);
		}); 
	}
});



function add_ob() {
	document.getElementById('button').innerHTML = 'Идет загрузка на сервер ...';
	
	var msg = $('#add_ob').serialize();
	$.ajax({
		type: 'POST',
		url: "ajax.php",
		data: msg,
		success: function(data) {
		$('#res').html(data);
		}
	});
}

function dimg(id) {
	var elem = document.getElementById('div_'+id);
	elem.remove();
	cou_browser--;
	document.getElementById('browser').innerHTML = 'Загрузить фото в браузер';
	}
	
</script>