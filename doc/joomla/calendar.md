Calendar
========

The calender in joomla makes an ajax request to uno.arscca.org

The calendar controller sends back html without an html or head tag.

The calendar controller sets CORS headers so cross-domain is kosher.

To test the javascript, browse to /joomla_test

Copy the contents of templates/joomla_test/home_page.jinja2
onto a page inside joomla. Then update the url to be an absolute url:
'http://uno.arscca.org/calendar/plain'

Add css to the Protostar template (filename: template.css)

Disable TinyMCE
---------------

When editing the script tags used to make the calendar work,
you will need to disable TinyMCE or it will remove your script tags.

Extensions -> Plugins -> TinyMCE
Then check the box next to Editor (TinyMCE) to disable the editor.
You can turn it back on later for other people to use.
