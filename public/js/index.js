var current_page = 1;
var result       = []
var pages        = 0
var last_query    = undefined;
var query        = "";
async function search(q) {
	clear_results();
	query = q;
	current_page = 1;
	load_more();
}

async function load_more() {
	if (current_page <= pages || last_query !== query){
		$(".expand_more").style.display = "none"
		r = await eel.search(query, current_page)();
		[result, pages] = r
		add_results(result);
		console.log(pages, current_page);

		$(".expand_more").style.display = "grid"
		current_page += 1;
		last_query = query
		if (current_page > pages) {
			$(".expand_more").style.display = "none"
		}
	}
}

$("#rechercher").onchange = (e) => {
	search(e.target.value);
};

$(".expand_more").onclick = load_more;

search("");
