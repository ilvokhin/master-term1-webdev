function(doc) {
  if(doc.doc_type == "User" && doc.username) {
    emit(doc.username, doc);
  }
}
