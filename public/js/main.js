var last_anim;


function update_stars() {
	$$(".review").forEach((e) => {
		let stars = e.querySelectorAll(".star");
		let rate = eval(e.querySelector(".note").innerText);
		if(rate ){
			e.style.display = "flex";
			rate = rate.map(0, 10, 0, 5);
			let rounded = Math.floor(rate);
			let rest = (rate - rounded) * 100;

			for (var i = Math.floor(rate) + 1; i < stars.length; ++i) {
				stars[i].style.backgroundImage =
					"linear-gradient(90deg, gold -100%, gray -100%)";
			}
			for (var y = Math.floor(rate) - 1; y >= 0; --y) {
				stars[y].style.backgroundImage =
					"linear-gradient(90deg, gold 100%, gray -100%)";
			}
			let star = stars[rounded];
			if (star) {
				star.style.backgroundImage = `linear-gradient(90deg, gold ${rest.map(
					0,
					100,
					20,
					80
				)}%, gray -100%)`;
			}
		}else{
			e.style.display = "none";
		}
	});
}
function show_details() {
	load_infos(this);
}

function animate_details() {
	if (last_anim) {
		last_anim.reverse();
	}
	var tl = gsap.timeline({
		defaults: { ease: "none" },
		onComplete: show_details.bind(JSON.parse(this.dataset.info)),
		onReverseComplete: () => {
			this.setAttribute("style", "");
			$(".content").style.overflow = "hidden";
			$(".load").style.opacity = 1;
		},
	});
	let preview = $(".details");
	let bcr = this.getBoundingClientRect();
	preview.setAttribute("style", "");
	preview.style.top = bcr.top + "px";
	preview.style.left = bcr.left + "px";
	preview.style.width = bcr.width + "px";

	preview.style.height = bcr.height + "px";
	preview.style.height = bcr.height + "px";
	this.style.pointerEvents = "none";
	this.style.transform = "";

	tl.to(this, {
		rotationY: 90,
		duration: 0.5,
	});
	tl.fromTo(
		preview,
		{
			rotationY: 90,
			opacity: 1,
		},
		{
			rotationY: 0,
			opacity: 1,
			duration: 0.5,
		},
		"+=.3"
	);
	tl.to(
		preview,
		{
			opacity: 1,
			margin: "auto",
			boxShadow: "0px 0px 0px 0px rgba(0, 0, 0, 0)",
			pointerEvents: "all",
			top: 0,
			width: "80%",
			height: "100%",

			minWidth: "450px",
			left: "50%",
			x: "-50%",
		},
		">"
	);
	tl.to(
		".cover",
		{
			opacity: 0.4,
		},
		"<"
	);
	tl.to(
		".cover",
		{
			pointerEvents: "all",
			duration: 0,
		},
		">"
	);
	tl.to(
		preview,
		{
			overflow: "auto",
			duration: 0,
		},
		">"
	);

	last_anim = tl;
	$(".cover").onclick = () => {
		$(".content").style.overflow = "hidden";
		$(".load").style.opacity = 1;
		tl.reverse().then(() => {
			this.setAttribute("style", "");
		});
	};
}

// eel.expose(add_results);
function add_results(results) {
	// console.log("adding results");
	const container = $(".search-results");
	let list = false
	if(results && !results[0].image){
		container.style.display = "block"
		list = true;
	}else{
		container.style.display = "flex"
	}
	for (const result of results) {

		let card = document.createElement("li");
		if (!list){
			card.innerHTML = /*html*/ `
				<div class="my-card__media mdc-card__media mdc-card__media" style='background-image: url("${result.image}")'>
				</div>
				<div class="mdc-card__content">
					<h6 class="mdc-typography--headline6">${result.name}</h6>
					<div class="review">
						<div class="material-icons star">star</div
						><div class="material-icons star">star</div
						><div class="material-icons star">star</div
						><div class="material-icons star">star</div
						><div class="material-icons star">star</div>
						<span class="note mdc-typography">${result.stars}</span>
					</div>
				</div>
				`;

			if (!result.stars) {
				card.querySelector(".review").remove();
			}
			card.classList.add("mdc-card");
			card.classList.add("mdc-card--outlined");
			card.classList.add("mdc-ripple-surface");
		}else{
			card.innerHTML = /*html*/ `
			  <span class="mdc-list-item__ripple"></span>
			  <span class="mdc-list-item__text">${result.name}</span>
			`
			card.classList.add("mdc-list-item");
			card.classList.add("mdc-ripple-surface");
		}
		container.appendChild(card);
		init.ripple(card)
		card.dataset.info = JSON.stringify(result);
		card.onclick = animate_details.bind(card);
	}
	update_stars();
	return true;
}
function clear_results() {
	const container = $(".search-results");
	container.innerHTML = "";
}
// search("fairy tail");
// show_details();

