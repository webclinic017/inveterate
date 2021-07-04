<!doctype html>
<html>
    <head>
	<title>[% nodename %] - Proxmox Console</title>
	<link rel="stylesheet" href="/xtermjs/xterm.css?version=4.7.0-3" />
	<link rel="stylesheet" href="/xtermjs/style.css?version=4.7.0-3" />
	<script src="/xtermjs/xterm.js?version=4.7.0-3" ></script>
	<script src="/xtermjs/xterm-addon-fit.js?version=4.7.0-3" ></script>
	<script src="/xtermjs/util.js?version=4.7.0-3" ></script>
    </head>
    <body>
	<div id="status_bar"></div>
	<div id="wrap">
	<div id="terminal-container"></div>
	</div>
	<script type="text/javascript">
	    if (typeof(PVE) === 'undefined') PVE = {};
	    PVE.UserName = '[% username %]';
	    PVE.CSRFPreventionToken = '[% token %]';
	</script>
	<script src="/xtermjs/main.js?version=4.7.0-3" defer ></script>
    </body>
</html>
