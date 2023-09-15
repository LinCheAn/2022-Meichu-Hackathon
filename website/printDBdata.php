<?php 

$command = escapeshellcmd('./showAllDB.py');
$output = shell_exec($command);
echo $output;

?>