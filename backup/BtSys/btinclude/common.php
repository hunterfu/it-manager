<?
// +--------------------------------------------------------------------------+
// | Project:    CMS BT MODULE                                    	      |
// | Function :  Common Function 					      |
// +--------------------------------------------------------------------------+

// return datetime
function get_date_time()
{
    return date("Y-m-d H:i:s", time());
}

// error msg string
$error_msg="";

//error handler function
function customError($errno, $errstr,$errfile,$errline)
{ 
 global $error_msg;
 $error_msg=$errstr;
 echo "level:[$errno]==$errfile:[$errline]==$errstr\n";
}

//set error handler
set_error_handler("customError",E_WARNING);
#set_error_handler("customError",E_ALL);

// sql execute error msg
function sqlerr($file = '', $line = '')
{
  print("<table border=0 bgcolor=blue align=left cellspacing=0 cellpadding=10 style='background: blue'>" .
    "<tr><td class=embedded><font color=white><h1>SQL Error</h1>\n" .
  "<b>" . htmlspecialchars(mysql_error()) . ($file != '' && $line != '' ? "<p>in $file, line $line</p>" : "") . "</b></font></td></tr></table>");
  die;
}
?>
