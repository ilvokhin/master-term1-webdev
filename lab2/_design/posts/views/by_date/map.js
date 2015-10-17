function(doc) {
  if( doc.doc_type == "Post" && doc.date ) {
    emit(doc.date, doc);
  }
}
