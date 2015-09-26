
// server db
function CouchDbViewer(dbName, forceTimeout) {
  this.dbName = dbName;
  this.forceTimeout = forceTimeout;
  this.requestPath = '/' + this.dbName + '/_all_docs';
}

CouchDbViewer.prototype.getData = function (successCallback, timeoutCallback) {
  var request = new XMLHttpRequest();
  request.ontimeout = timeoutCallback;

  request.open('GET', this.requestPath);

  if( this.forceTimeout ) {
    request.timeout = 1;
  }

  request.onload = function() {
    if( request.status != 200 ) {
      console.log('CouchDB request failed: ' + request.statusText);
      return;
    }
    successCallback(request.responseText);
  }

  request.send(null);
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
      if( request.result ) {
        successCallback(request.result.val);
      }
      else {
        // not success at all, we create new empty storage
        successCallback('');
      }
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
function CouchDbCache(dbName, makeTableCallback, forceTimeout) {
  this.couchDb = new CouchDbViewer(dbName, forceTimeout);
  this.localCache = new LocalCache(dbName);
  this.makeTableCallback = makeTableCallback;
}

CouchDbCache.prototype.getData = function() {
  console.log('Get cached data from db: ' + this.couchDb.dbName);

  localCache = this.localCache;
  makeTable = this.makeTableCallback;

  successCallback = function(data) {
    localCache.put(data);
    makeTable(data);
  }

  timeoutCallback = function() {
    console.log('Timeout occurs should use cache');
    localCache.get(makeTable);
  }

  this.couchDb.getData(successCallback, timeoutCallback);
}

function makeTable(rawCouchData) {
  // we can get nothing, if request failed and cache is empty,
  // anyway we should draw some dummy table
  if( !rawCouchData ) {
    console.log('Got empty data, make dummy table');
    rawCouchData = '{"total_rows":1,"rows":[{"id":"empty","key":"empty","value":"empty"}]}';
  }

  var parsedCouchData = JSON.parse(rawCouchData);

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

  var parentElem = 'db-table';
  document.getElementById(parentElem).appendChild(table);
}

function makeTablesList(parentName, rawData) {
  var select = document.getElementById(parentName);
  var data = JSON.parse(rawData);

  for(var i = 0; i < data.length; i++) {
    var option = document.createElement('option');
    option.innerHTML = data[i];
    option.value = data[i];
    select.appendChild(option);
  }
}

function loadCouchTables(successCallback) {
  var request = new XMLHttpRequest();
  var requestPath = '/_all_dbs';

  request.open('GET', requestPath);

  request.onload = function() {
    if( request.status != 200 ) {
      console.log('CouchDB request failed: ' + request.statusText);
      return;
    }
    successCallback('tables-list', request.responseText);
  }

  request.send(null);
}

function loadData() {
  var tablesList = document.getElementById('tables-list');
  var loadList = document.getElementById('load-list');

  var selectedTable = tablesList.options[tablesList.selectedIndex].value;
  var selectedLoad = loadList.options[loadList.selectedIndex].value;

  // clear table (dirty hack)
  var dbTable = document.getElementById('db-table');
  dbTable.innerHTML = '';

  // make request
  var forceTimeout = (selectedLoad == "local");
  var couchDb = new CouchDbCache(selectedTable, makeTable, forceTimeout);
  couchDb.getData();
}

loadCouchTables(makeTablesList);
makeTablesList('load-list', '["online", "local"]');

var loadButton = document.getElementById('load');
loadButton.onclick = loadData;

// make empty table
makeTable('');
