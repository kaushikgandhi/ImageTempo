<script>
  //var info = document.getElementById('info');
  var lat = geoip_latitude();
  var lon = geoip_longitude();
  var city = geoip_city();
  var out = '<h3>Information from your IP</h3>'+
            '<ul>'+
            '<li>Latitude: ' + lat + '</li>'+
            '<li>Longitude: ' + lon + '</li>'+
            '<li>City: ' + city + '</li>'+
            '<li>Region: ' + geoip_region() + '</li>'+
            '<li>Region Name: ' + geoip_region_name() + '</li>'+
            '<li>Postal Code: ' + geoip_postal_code() + '</li>'+
            '<li>Country Code: ' + geoip_country_code() + '</li>'+
            '<li>Country Name: ' + geoip_country_name() + '</li>'+
            '</ul>'
  alert(out);
</script>