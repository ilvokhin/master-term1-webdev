
// server db
function CouchDbViewer(dbName) {
  this.dbName = dbName;
  this.requestPath = '/' + this.dbName + '/_all_docs';
}

CouchDbViewer.prototype.getData = function (timeoutCallback) {
  var request = new XMLHttpRequest();
  request.ontimeout = timeoutCallback;

  request.open('GET', this.requestPath, false);
  //request.timeout = 1;
  request.send(data);

  if( request.status != 200 ) {
    console.log('CouchDB request failed: ' + request.statusText);
  }

  return request.responseText;
}

// local data storage
function LocalCache(dbName) {
  console.log('LocalCache: make local cache');
  this.dbName = dbName;
  this.indexedDb = window.indexedDB;
  this.cacheKey = 0;
}

LocalCache.prototype.makeStoreName = function() {
  return this.dbName + 'Store';
}

LocalCache.prototype.logError = function (err) {
  console.log('LocalCache error: ' + err);
}

LocalCache.prototype.access = function (accessCallback) {
  var request = indexedDB.open(this.dbName, 1);

  request.onerror = this.logError;

  request.onsuccess = function () {
    accessCallback(request.result);
    console.log('LocalCache: successfull access');
  }

  var storeName = this.makeStoreName();
  request.onupgradeneeded = function (e) {
    e.currentTarget.result.createObjectStore(storeName, {keyPath: 'key'});
    console.log('LocalCache: new store maked');
  }
}

LocalCache.prototype.get = function (successCallback) {
  var storeName = this.makeStoreName();
  var cacheKey = this.cacheKey;
  this.access(function(db) {
    var request = db.transaction([storeName], 'readonly').objectStore(storeName).get(cacheKey);
    request.onerror = this.logError;
    request.onsuccess = function() {
      successCallback(request.result.val);
    }
  });
}

LocalCache.prototype.put = function (data) {
  var storeName = this.makeStoreName();
  var cacheKey = this.cacheKey;
  this.access(function(db) {
    var request = db.transaction([storeName], 'readwrite').objectStore(storeName).put({key: cacheKey, val: data});
    request.onerror = this.logError;
  });
}

// local + server 
function CouchDbCache(dbName, makeTableCallback) {
  this.couchDb = new CouchDbViewer(dbName);
  this.localCache = new LocalCache(dbName);
  this.makeTableCallback = makeTableCallback;
}

CouchDbCache.prototype.getData = function() {
  console.log('Get cached data from db: ' + this.couchDb.dbName);

  localCache = this.localCache;
  makeTable = this.makeTableCallback;

  var data = this.couchDb.getData(function() {
    console.log('Timeout occurs should use cache');
    localCache.get(makeTable);
  });

  if( data ) {
    this.localCache.put(data);
    this.makeTableCallback(data);
  }

  return data;
}

function makeTable(rawCouchData) {
  var parentElem = 'db-table';
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

// make request
couchDb = new CouchDbCache('test', makeTable);
var data = couchDb.getData();
console.log(data);
