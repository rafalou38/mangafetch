async function search_bookmarks(q = "") {
  clear_results();
  results = [];
  var r = await eel.get_favorites(q)();
  result = r;
  add_results(r);
}

$("#rechercher").onchange = (e) => {
  search(e.target.value);
};

search_bookmarks();
