<?
function base64_to_jpeg($base64_string, $output_file) {
    $ifp = fopen( $output_file, 'wb' ); 
    $data = explode( ',', $base64_string );
    fwrite( $ifp, base64_decode( $data[ 1 ] ) );
    fclose( $ifp ); 
    return $output_file; 
	}

if($_POST['images'])
	{
	echo '<div class="photo_item">Большие фото-></div>';
	foreach($_POST['images'] as $index=>$po)
		{
		//base64_to_jpeg($po, $index.'.jpg');  // сохранить как файл
		echo '<div class="photo_item"><img src="'.$po.'"></div>';
		}
	}



if($_POST['images_preview'])
	{
	echo '<div class="photo_item">Превьюшки-></div>';
	foreach($_POST['images_preview'] as $index=>$po)
		{
		//base64_to_jpeg($po, $index.'_prev.jpg');  // сохранить как файл
		echo '<div class="photo_item"><img src="'.$po.'"></div>';
		}
	}
?>
<script>
	document.getElementById('button').innerHTML = 'Передача данных на сервер';
</script>