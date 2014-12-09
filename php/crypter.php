<?php
/*
 * Web interface for encrypting strings using the crypter command line client. The web host
 * must have crypter installed, and a valid private key configuration in /etc/crypter/crypter.cfg.
 */

if (!$_REQUEST['encrypt']) {

?><!DOCTYPE html>
<html lang="en">
	<head>
		<title>Configuration Encrypter</title>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
		<script type="text/javascript">
			$(function() {
				$('#doencrypt').click(function() {
					$.post("", { encrypt: $('#encrypt').val() }).done(function(data) {
						$('#encrypted').val(data.encrypted);
					});
				});
			});
		</script>
		<style>
			html, body {
				font-family: sans-serif;
				font-size: 12px;
				margin: 0;
				padding: 0;
				border: 0;
			}
			body {
				margin: 10px;
				background-color: #EEE;
			}
			h1 {
				font-size: 16px;
			}
			p {
				margin-bottom: 0;
			}
		</style>
	</head>
	<body>
		<h1>Configuration Encrypter</h1>
		<form action="crypter.php" onsubmit="return false;">
			<p>Value to encrypt:</p>
			<textarea id="encrypt" name="encrypt" rows="5" cols="80"></textarea>
			<br />
			<button id="doencrypt">Encrypt Value</button>
			<p>Encrypted output:</p>
			<textarea id="encrypted" rows="15" cols="80"></textarea>
		</form>
	</body>
</html><?

} else {

	$proc = proc_open('/usr/local/bin/crypter --encrypt -', array(
		0 => array('pipe', 'r'), // stdin
		1 => array('pipe', 'w'), // stdout
		2 => array('pipe', 'w')), // stderr
		$pipes);

	if (is_resource($proc)) {

		fwrite($pipes[0], trim($_REQUEST['encrypt']));
		fclose($pipes[0]);

		$encrypted = trim(stream_get_contents($pipes[1]));
		fclose($pipes[1]);

		$error = trim(stream_get_contents($pipes[2]));
		fclose($pipes[2]);

		$retval = proc_close($proc);

		$result = array(
			'request' => $_REQUEST['encrypt'],
			'encrypted' => $encrypted
		);

		header('Content-Type: application/json');
		echo json_encode($result);

	} else {
		echo 'Command could not be executed.';
	}

}
