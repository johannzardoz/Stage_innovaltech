#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
print "Content-Type: text/html\n"
print """
<!DOCTYPE html>
<html>
 <head>
 <meta charset="UTF-8">
 <title>Une page Web</title>
 </head>

 <body>
 <h1>Une page Web avec CGI-Python</h1>
 <p>Heure courante {}</p>
 </body>
</html>
""".format(time.strftime('%H:%M:%S'))