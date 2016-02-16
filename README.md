Google Map Twitter Stream

A Google Map app that streams real time tweets of a certain location. Markers drops within the area of the selected location, the default location is Metro Manila, but you can change it by selecting a location on the search box above the map. To see the tweets, hover your cursor on any of the marker and the tweet will show in the infowindow.


API

SocketIO url
(IP/Domain)/tweets

To change the location of twitter stream
// Geometric Bounds
// Ex.

curl -H "Content-Type: application/json" -X POST -d '{'sw':{'lng':'','lat':''},'ne':{'lng':'','lat':''}}' (IP/Domain)/change_location
