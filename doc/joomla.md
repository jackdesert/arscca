ARSCCA Joomla Site
==================

login location: arscca.org/administrator

RallyX Guide
------------

Note markdown stored in doc/joomla/rallx_guide.md


Board
-----


Requesting website access be shared with Jack Desert.  He has volunteered to help keep the site up to date.  Nick to contact Park for the info.  Jack also asked if there was a way to fix our Facebook page so it would send out notifications any time something is posted.  This would need to be checked on a PC.  We were unable to find a way to do this over cell.

Home Page
---------

Click Content -> Featured Articles.
Edit the one called "2019 Season"


Schedule
--------

Content -> Articles
Search for "schedule"


Generate Reports
----------------

From AxWare, click Generate All Reports. This generates them temporarily in the
"announcer" folder.
While the report windows are still open, open Windows (file) Explorer
and find the four reports with the name matching the event.
Copy those four files to a thumb drive so you can post them later.


Post Results
------------

Create a new article category.
  title: <year> Solo II Event <event-number>
  parent: <YEAR> Results
  body: none
Create an article
  Category: the new category you created
  title: <year> Solo II Event <event-number> <final/summary/etc>
  toggle the editor to html
  paste in the contents


Ordering of Results withing a Category
--------------------------------------

Menus -> All Menu Items
Search for the "2019 Results" menu item.
Click "List Layouts"
For "Category Order" choose which order you want.
(I wanted Category Reverse, but that is not offered.)


Ordering Menu Items
-------------------

Menus -> Main Menu
Grab the handle at left and drag to position.


Add Link to Menu
----------------

Menus -> View All Menu Items.

Now find one of the menu items and look at its "Main Menu" and "Parent Item" settings.

Now click "+" to create a new menu item. Choose the item type carefully.

If you want to link to a single article, create that single article first.


Create a Featured Article
-------------------------

When creating an article, in the right column change Featured to Yes.


Redirect www to non-www
-----------------------

https://hostingmanager.godaddy.com/AccountPanel.aspx?accountUID=aa1c2d99-2f45-4cce-865b-764a067456ee

  - click **File Manager** to edit .htaccess

(Don't bother with .htaccess.txt because it doesn't do anything)

    # Added by Jack Desert 2020-03-11 to redirect www to non-www
    RewriteBase /
    RewriteCond %{HTTP_HOST} ^www\.(.*)$ [NC]
    RewriteRule ^(.*)$ http://%1/$1 [R=301,L]


Pretty Url
----------

Add this to htaccess to create a pretty url for /novice

    RewriteRule ^(novice)$ .//index.php?option=com_content&view=article&id=19&Itemid=107


    # Added by Jack Desert 2020-03-11 to build pretty urls
    RewriteRule ^(novice)$ ./index.php?option=com_content&view=article&id=19&Itemid=107
    RewriteRule ^(calendar)$ ./index.php?option=com_content&view=article&id=440&Itemid=102
    RewriteRule ^(results/2020)$ ./index.php?option=com_content&view=category&id=160&Itemid=103
    RewriteRule ^(results)$ http://arscca.org/index.php?option=com_content&view=category&id=8&Itemid=104
    RewriteRule ^(newsletter)$ ./index.php?option=com_content&view=article&id=467&Itemid=129
    RewriteRule ^(faq)$ ./index.php?option=com_content&view=article&id=468&Itemid=130
    RewriteRule ^(guides/rallyx)$ ./arscca.org/index.php?option=com_content&view=article&id=512&Itemid=133
    RewriteRule ^(rules)$ ./arscca.org/index.php?option=com_content&view=article&id=18&Itemid=105
    RewriteRule ^(board)$ ./arscca.org/index.php?option=com_content&view=article&id=22&Itemid=115
    RewriteRule ^(contact)$ ./index.php?option=com_content&view=article&id=521


Backlog
-------
- formatting of board meeting page
  - formatting of person: role
  - contact info for all??
- Add Facebook Group to menu
  - let's get an actual facebook group going first
  - the Schedule page makes reference to facebook, but it does not provide a link
- Create a FAQ
- Create a unified front to tell people how to interact: facebook, email board members
- Figure out where to advertise board meetnings
- put newsletters on website. At least the most recent one
