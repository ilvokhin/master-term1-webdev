function getCounterName(id, enjoyType) {
  var className = '';
  if( enjoyType == 'like_post' ) {
    className = 'like-counter-' + id;
  }
  else {
    className = 'star-counter-' + id;
  }
  return className;
}

function getTextName(id, enjoyType) {
  var textName = '';
  if( enjoyType == 'like_post' ) {
    textName = 'like-text-' + id;
  }
  else {
    textName = 'star-text-' + id;
  }
  return textName;
}

function enjoyPost(id, enjoyType) {
  var request = new XMLHttpRequest();
  var requestPath = '/' + enjoyType + '/' + id;
  request.open('GET', requestPath);
  request.onload = function() {
    if( request.status != 200 ) {
      console.log('Request failed: ' + request.statusText)
      return;
    }
    var counter_elem = document.getElementById(getCounterName(id, enjoyType));
    var text_elem = document.getElementById(getTextName(id, enjoyType));
    if( enjoyType == 'like_post' ) {
      if( text_elem.innerHTML == 'like' ) {
        text_elem.innerHTML = 'unlike';
        counter_elem.innerHTML = parseInt(counter_elem.innerHTML, 10) + 1;
      }
      else {
        text_elem.innerHTML = 'like';
        counter_elem.innerHTML = parseInt(counter_elem.innerHTML, 10) - 1;
      }
    }
    else {
      if( text_elem.innerHTML == 'star' ) {
        text_elem.innerHTML = 'unstar';
        counter_elem.innerHTML = parseInt(counter_elem.innerHTML, 10) + 1;
      }
      else {
        text_elem.innerHTML = 'star';
        counter_elem.innerHTML = parseInt(counter_elem.innerHTML, 10) - 1;
      }
    }
  }
  request.send(null);
}

function likePost(id) {
  enjoyPost(id, 'like_post');
}

function starPost(id) {
  enjoyPost(id, 'star_post');
}
