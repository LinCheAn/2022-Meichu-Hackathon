<?php 

$command = escapeshellcmd('./srchDB.py '.$_REQUEST['srch']);
$output = shell_exec($command);
echo $output;

?>