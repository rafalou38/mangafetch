eel
	.get_sources()()
	.then(async (sources) => {
		let current = await eel.get_current_source()()
		const list = $(".sources");
		for (const source of sources) {
			let li = document.createElement("li");
			li.classList.add("mdc-list-item");
            if (source == current){
                li.classList.add("mdc-list-item--selected");
            }
			li.dataset.value = source;
			li.innerHTML = /*html*/ `
			<span class="mdc-list-item__ripple"></span>
			<span class="mdc-list-item__text">${source}</span>
		`;
			list.appendChild(li);
		}
		init.select();
	});

async function update_source(){
	let sources = await eel.get_sources()()
	let current = await eel.get_current_source()()
	$(".mdc-select").mdc.selectedIndex = sources.indexOf(current)
}


$(".mdc-select").addEventListener("MDCSelect:change", (e) => {
  eel.set_source(e.detail.value);
  if (document.URL.indexOf("index") !== -1) {
    last_query = null;
    search($("#rechercher").value);
  }
});
