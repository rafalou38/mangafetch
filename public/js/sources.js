eel
	.get_sources()()
	.then((sources) => {
		const list = $(".sources");
		for (const source of sources) {
			let li = document.createElement("li");
			li.classList.add("mdc-list-item");
			li.dataset.value = source;
			li.innerHTML = /*html*/ `
			<span class="mdc-list-item__ripple"></span>
			<span class="mdc-list-item__text">${source}</span>
		`;
			list.appendChild(li);
		}
		let selected = $(".mdc-list-item");
		selected.classList.add("mdc-list-item--selected");
		selected.setAttribute("aria-selected", "true");
		init.select();
	});

$(".mdc-select").addEventListener("MDCSelect:change", (e) => {
	eel.set_source(e.detail.value);
	last_query = null;
	search($("#rechercher").value);
});
