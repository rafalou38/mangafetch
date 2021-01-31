const init = {
	dataTable: _ => {
		$$(".mdc-data-table").forEach((e) => {
			e.mdc = mdc.dataTable.MDCDataTable.attachTo(e);
		});
	},
	ripple: (e) => {
		if (e)
			e.mdc = mdc.ripple.MDCRipple.attachTo(e);
	},
	textField: _ => {
		$$(".mdc-text-field").forEach((e) => {
			e.mdc = mdc.textField.MDCTextField.attachTo(e);
		});
	},
	button: _ => {
		$$(".mdc-button").forEach((e) => {
			e.mdc = mdc.ripple.MDCRipple.attachTo(e);
		});
	},
	linearProgress: _ => {
		$$(".mdc-linear-progress").forEach((e) => {
			e.mdc = mdc.linearProgress.MDCLinearProgress.attachTo(e);
		});
		$$(".mdc-linear-progress-indeterminate").forEach((e) => {
			e.mdc.determinate = false;
		});
	},
	select: _ => {

		$$(".mdc-select").forEach((e) => {
			if (e.mdc) e.mdc.destroy();
			e.mdc = mdc.select.MDCSelect.attachTo(e);
		});
	}
};

function init_all() {
	for (const type in init) {
		init[type]()
	}
}

// window.mdc.autoInit();
// update_chapters();
init_all()
