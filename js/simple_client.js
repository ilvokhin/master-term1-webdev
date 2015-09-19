function makeHttpRequest(type, path, data = '') {
  var request = new XMLHttpRequest();
  request.open(type, path, false);
  request.send(data);

  return request;
}
 
function makeTable(parentElem, rawCouchData) {
  var parsedCouchData = JSON.parse(rawCouchData);

  if( !parsedCouchData.total_rows ) {
    return;
  }  

  var table = document.createElement('table');
  
  // add header
  var header = document.createElement('thead');
  var firstElem = parsedCouchData.rows[0];

  for(var key in firstElem) {
    header.appendChild(document.createElement('th')).appendChild(document.createTextNode(key));
  }
  table.appendChild(header);

  // add rows
  for(var i = 0; i < parsedCouchData.total_rows; i++) {
    var currentRow = table.insertRow();
    var currentElem = parsedCouchData.rows[i];

    for(var prop in currentElem) {
      if( currentElem.hasOwnProperty(prop) ) {
        var cell = currentRow.insertCell();
        cell.appendChild(document.createTextNode(currentElem[prop]));
      }
    } 
  }

  document.getElementById(parentElem).appendChild(table);
}

request = makeHttpRequest('GET', '/test/_all_docs');
console.log(request.responseText);

makeTable('db-table', request.responseText);
