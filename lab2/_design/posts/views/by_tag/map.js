function(doc) {
  if( doc.doc_type == "Post" && doc.tags ) {
    for(var i in doc.tags) {
      emit(doc.tags[i], doc);
    }
  }
}
