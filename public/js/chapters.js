var chapters = [];
var open_manga = "";
const split_regex = /(\d[\d\-]*)(?:\/)*$/;
const split_regex2 = /(\d[\d\-]*.*?)(?:\/)$/;

function download_group(ichapters, manga) {
	addNotification(".downloads-tab");
	eel.download_group(ichapters, manga);
}
eel.expose(diplay_inividual_chapter_progresion);
function diplay_inividual_chapter_progresion(info) {}
function download_chapter(uri) {
	const regex = /-([^\d]+)-(\d)+/;
	const r = regex.exec(uri);
	const id = r[1];
	const chapter = r[2];

	addNotification(".downloads-tab");

	eel.download_chapter(chapter, id);
}
function update_table(chapters_list) {
	let table = $(".mdc-data-table__content");
	table.parentNode.parentNode.mdc.destroy();
	table.innerHTML = "";
	chapters_list.forEach((elem) => {
		// console.log(elem);
		let e = elem[0];
		let url = elem[1];
		let row = table.insertRow();
		row.classList.add("mdc-data-table__row");
		row.dataset["rowId"] = e;
		row.innerHTML = `
			<td class="mdc-data-table__cell mdc-data-table__cell--checkbox">
				<div class="mdc-checkbox mdc-data-table__row-checkbox">
					<input
						type="checkbox"
						class="mdc-checkbox__native-control"
						aria-labelledby="u0"
					/>
					<div class="mdc-checkbox__background">
						<svg class="mdc-checkbox__checkmark" viewBox="0 0 24 24">
							<path
								class="mdc-checkbox__checkmark-path"
								fill="none"
								d="M1.73,12.91 8.1,19.28 22.79,4.59"
							/>
						</svg>
						<div class="mdc-checkbox__mixedmark"></div>
					</div>
					<div class="mdc-checkbox__ripple"></div>
				</div>
			</td>
			<td
				class="mdc-data-table__cell"
				data-column-id="chapitre"
			>
				${e}
			</td>
			<td class="mdc-data-table__cell">
				<button class="mdc-button mdc-button--raised" onClick="download_chapter('${url}')">
					<div class="mdc-button__ripple"></div>
					<i
						class="material-icons mdc-button__icon"
						aria-hidden="true"
						>download</i
					>
					<span class="mdc-button__label">DOWNLOAD</span>
				</button>
			</td>
			<td class="mdc-data-table__cell">

					<button class="mdc-button mdc-button--raised" onClick="window.open('${url}',width=7000,height=8000)">
						<div class="mdc-button__ripple"></div>
						<i
							class="material-icons mdc-button__icon"
							aria-hidden="true"
							>import_contacts</i
						>
						<span class="mdc-button__label">READ</span>
					</button>
			</td>
		`;
	});
	init.dataTable();
	init.button();
}
function update_chapters() {
	let start = $("#start").value;
	let end = $("#end").value;
	let nlist = chapters;
	if ((start && end && eval(start) < eval(end)) !== false)
		nlist = chapters.slice(eval(start) - 1, eval(end));
	// console.log(nlist)
	update_table(nlist);
}
function check_selected(e) {
	let selected = e.target.mdc.getSelectedRowIds();
	console.log(selected);
	$(".download-selected").dataset.chapters = selected;
	if (selected.length) {
		$(".download-selected").removeAttribute("disabled");
		$(".how-much-selected").style.display = "block";
		$(".how-much-selected").innerHTML = selected.length + " selected";
	} else {
		$(".download-selected").setAttribute("disabled", "");
		$(".how-much-selected").style.display = "none";
	}
}
async function load_infos(manga) {
	$(".content").style.overflow = "hidden";
	$(".load").style.opacity = 1;

	const infos = await eel.get_info(manga.id)();
	const favorites = await eel.get_favorites_id()();

	// console.log(infos);
	const b = $(".bookmark");
	b.dataset.data = JSON.stringify(manga);
	if (favorites && favorites.indexOf(manga.id) != -1) {
		b.classList.add("bookmarked");
		// b.querySelector(".mdc-button__label").innerHTML = "bookmarked"
	} else {
		b.classList.remove("bookmarked");
	}
	open_manga = manga.id;

	chapters = [];
	for (const chapter of infos.chapters) {
		let r = split_regex.exec(chapter);
		let n;
		if (r) {
			n = [r[1], chapter];
		} else {
			r = split_regex2.exec(chapter);
			n = [r[1], chapter];
		}

		chapters.push(n);
		// console.log(chapters);
	}
	update_table(chapters);

	const details = $$("small.content");
	details[0].innerHTML = infos.author;
	details[1].innerHTML = infos.edition;
	details[2].innerHTML = infos.release;
	details[3].innerHTML = infos.status;
	details[4].innerHTML = infos.alternatif;
	details[5].innerHTML = infos.genres;

	$(".title").innerHTML = infos.title;
	$(".active_manga_review>.note").innerHTML = infos.note;

	$(".manga-couverture").setAttribute("src", infos.cover);
	$(".banner").style.backgroundImage = `url(${infos.banner})`;
	$(".description").innerHTML = infos.description;

	$(".load").style.opacity = 0;
	$(".content").style.overflow = "initial";

	update_stars();
}
function addNotification(selector) {
	let current = $(selector).style.getPropertyValue("--notif-text");
	current = current ? parseInt(current.replaceAll('"', "")) + 1 : 1;
	$(selector).style.setProperty("--notif-text", `"${current}"`);
}
function removeNotification(selector) {
	let current = $(".bookmarks-tab").style.getPropertyValue("--notif-text");
	current = current ? parseInt(current.replaceAll('"', "")) - 1 : 0;
	if (current <= 0) {
		$(".bookmarks-tab").style.removeProperty("--notif-text");
	} else {
		$(".bookmarks-tab").style.setProperty("--notif-text", `"${current}"`);
	}
}

$(".bookmark").onclick = async (e) => {
	const favorites = await eel.get_favorites_id()();
	const manga = JSON.parse($(".bookmark").dataset.data);
	if (favorites && favorites.indexOf(manga.id) != -1) {
		eel.remove_from_favorites(manga);
		$(".bookmark").classList.remove("bookmarked");
		removeNotification(".bookmarks-tab");
	} else {
		eel.add_to_favorites(manga);
		$(".bookmark").classList.add("bookmarked");
		addNotification(".bookmarks-tab");
	}
	// current = $(".bookmarks-tab").style.getPropertyValue("--notif-text")
	// current = current ? parseInt(current.replaceAll('"', "")) : 0
	// $(".bookmarks-tab").style.setProperty("--notif-text", `"${current + 1}"`)
};
$(".download-selected").addEventListener("click", (e) => {
	console.log(e.currentTarget.dataset.chapters.split(","), open_manga);
	download_group(e.currentTarget.dataset.chapters.split(","), open_manga);
});
$("#start").onkeyup = update_chapters;
$("#end").onkeyup = update_chapters;
document
	.querySelector(".mdc-data-table")
	.addEventListener("MDCDataTable:rowSelectionChanged", check_selected);
document
	.querySelector(".mdc-data-table")
	.addEventListener("MDCDataTable:selectedAll", check_selected);
document
	.querySelector(".mdc-data-table")
	.addEventListener("MDCDataTable:unselectedAll", check_selected);
