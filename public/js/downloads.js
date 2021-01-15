eel.expose(diplay_inividual_chapter_progresion);
var f = [];
var downloads = {};

function diplay_inividual_chapter_progresion(info) {
	// f.push(info)
	// console.log(JSON.stringify(f));

	if (!downloads[info.id]) {
		var li = document.createElement("li");
		downloads[info.id] = li;

		li.classList.add("list_item");
		li.dataset.id = info.th_id;
		li.dataset.outFile = info.out;
		li.addEventListener("click", reveal_file)
		li.innerHTML = /*html*/ `
		<div class="body">
			<img class="avatar" src="${info.cover}">
			<div class="content">
				<p class="first_line">${info.id}</p>
				<p class="second_line">${info.name}</p>
			</div>
			<button class="mdc-icon-button material-icons icon" onclick="stop_download('${info.th_id}')">delete</button>
		</div>
		<div role="progressbar" class="mdc-linear-progress mdc-linear-progress--animation-ready" aria-label="Example Progress Bar" aria-valuemin="0" aria-valuemax="1" aria-valuenow="0.3">
			<div class="mdc-linear-progress__buffer">
				<div class="mdc-linear-progress__buffer-bar"></div>
				<div class="mdc-linear-progress__buffer-dots"></div>
			</div>
			<div class="mdc-linear-progress__bar mdc-linear-progress__primary-bar">
				<span class="mdc-linear-progress__bar-inner"></span>
			</div>
			<div class="mdc-linear-progress__bar mdc-linear-progress__secondary-bar">
				<span class="mdc-linear-progress__bar-inner"></span>
			</div>
		</div>
		`;

		downloads[info.id] = li;
		$("ul").appendChild(li);

		init.linearProgress();
	} else {
		li = downloads[info.id];
		li.querySelector(".first_line").innerText = info.id;
		li.querySelector(".second_line").innerText = info.name;
		li.querySelector(".avatar").innerText = info.cover;
		li.dataset.id = info.th_id;
		li.dataset.outFile = info.out;
	}

	li.querySelector(".mdc-linear-progress").mdc.progress = info.percent;
}
function reveal_file(e){
	if (e.target.nodeName != "BUTTON")
		eel.reveal_file(e.currentTarget.dataset.outFile)
}
async function load_all() {
	let all = await eel.get_curent_downloads()()
	all.forEach((e)=>{
		diplay_inividual_chapter_progresion(e)
	})
}
async function stop_download(e) {
	eel.stop_download(e);
	$(`[data-id="${e}"]`).remove();
}
// eel.download_chapter("a", "b");
// eel.download_chapter(1, "hundred-demon-spectrum");
// eel.download_chapter(0, "sweet-home");
load_all()