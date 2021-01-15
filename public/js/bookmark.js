async function search(q="") {
	clear_results();
	var r = await eel.get_favorites(q)();
	add_results(r)
}

$("#rechercher").onchange = (e) => {
	search(e.target.value);
};

search()