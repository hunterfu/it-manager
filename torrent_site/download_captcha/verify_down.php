<?php session_start(); ?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="Author" content="51know.info" />
<title><?php echo $_REQUEST['torrent_name'] ?></title>
<style type="text/css">
body { font-family: sans-serif; font-size: 0.8em; padding: 5px; }
#result { border: 1px solid green; width: 600px; margin: 5px; padding: 5px; font-weight: bold; white-space:normal;}
#change-image { font-size: 0.8em; }
</style>
</head>
<body onload="document.getElementById('captcha-form').focus()">

<?php
/** Validate captcha */
if (!empty($_REQUEST['captcha']) && !empty($_SESSION['captcha']) && trim(strtolower($_REQUEST['captcha'])) == $_SESSION['captcha']) 
{
	$style = "background-color: #CCFF99";
	$request_captcha = htmlspecialchars($_REQUEST['captcha']);
	$torrent_name = $_REQUEST['torrent_name'];
	$torrent_dir = $_REQUEST['torrent_dir'];
	echo <<<HTML
		<div id="result" style="$style">
		$torrent_name <br><br>
		Your Can download use direct link <a href="down_file.php?download_file=$torrent_dir">download here</a>
		</div>
HTML;
	#unset($_SESSION['captcha']);
}
else
{
/** 种子信息 **/
$torrent_name=$_REQUEST['torrent_name'];
$torrent_dir=$_REQUEST['torrent_dir'];
?>

<p><b>Please Enter Text From Image:</b></p>
<form method="GET">
<img src="captcha.php" id="captcha" border="0"/>


<!-- CHANGE TEXT LINK -->
<a href="#" onclick="document.getElementById('captcha').src='captcha.php?'+Math.random(); document.getElementById('captcha-form').focus();"
    id="change-image"><br>Not readable? Refresh text.
</a>
<br/><br/>

<input type="hidden" name="torrent_name" value="<?php echo $torrent_name ?>" />
<input type="hidden" name="torrent_dir" value="<?php echo $torrent_dir ?>" />
<input type="text" name="captcha" id="captcha-form"/><br><br>
<input type="submit" value="download Torrent"/>

</form>
<?php } ?>
</body>
</html>
