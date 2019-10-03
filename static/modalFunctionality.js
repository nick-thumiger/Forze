//let apiURL = 'http://127.0.0.1:5100';
let apiURL = 'https://forze.pythonanywhere.com';

let currentEditCategory = null;
let currentEditType = null;
let currentEditID = null;
let attributesLength = null;

//open history modal
let triggerHistoryModal = (id) => {
    let modal_container = document.getElementById('history-modal-target');

    let url = apiURL+`/get_history/${id}`;

    fetch(url)
	.then((e) => {
		if (e.status === 200) {
			return e.json();
		} else {
            throw new Error("An error has occured");
		}
    })
    .then((e) => {
        if (e['response'].length === 0) {
            _innerHTML = `
                <p>There have been no changes to this item's history</p>
            `;
        } else {
            _innerHTML = `
            <table style="width : 100%">
                <tr>
                    <th style="width : 2%"></th>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Quantity</th>
                    <th>Date</th>
                    <th style="width : 2%"></th>
                </tr>
                `;

            e['response'].map(e => {
                _innerHTML += `<tr>
                <td></td>`;
                e.map(k => {
                    _innerHTML += `<td>${k}</td>`;
                })
                _innerHTML += `
                <td></td>
                </tr>`;
            })
        }

        modal_container.innerHTML = _innerHTML;
    })
	.catch((e) => console.error(e));
}

//Opens the modal that enables the user to edit an entry
let triggerEditModal = (category, id, type) => {
    currentEditCategory = category;
    currentEditType = type;
    currentEditID = id;

    let url = apiURL+`/get_item/${category}/${id}`;

    fetch(url)
	.then((e) => {
		if (e.status === 200) {
			return e.text();
		} else {
            throw new Error("An error has occured");
		}
    })
    .then(e => {
        return JSON.parse(e);
    })
    .then(e => {
        // console.log('yeet');
        i = 0;
        e.response.shift();

        e.response.map(k => {
            let t = document.getElementById(`edit_${i}`);
            t.setAttribute('value', k);

            i += 1;
        })
    })
    .catch((e) => {
        console.error(e);
    });
}

//Deletes the current thing that you are editing
let submitDelete = () => {
    const payload = {
        'table' : currentEditCategory,
        'item_id' : currentEditID
    }

    const settings = {
        'method' : "POST",
        'headers' : { "Content-Type" : "application/json" },
        'body' : JSON.stringify(payload)
    }

    let url = apiURL+`/delete_item`;

    fetch(url, settings)
    .then((e) => {
        if (e.status === 200) {
            return e.text();
        } else {
            throw new Error("An error has occured");
        }
    })
    .then(e => {
        console.log(e);
        location.reload();
    })
    .catch((e) => console.error(e));
}

//Edits the entry
let submitEdit = () => {
    console.log(currentEditType);

    let loop = true;
    let i = 0;

    let columns = [];
    let values = [];

    while (loop) {
        let t  = document.getElementById(`edit_${i}`);
        let k  = document.getElementById(`edit_target_${i}`);

        if (t === null) {
            break;
        }

        let columnName = k.textContent;
        let columnValue;

        try {
            columnValue = t.value;
        } catch {
            columnValue = t.options[t.selectedIndex].value;
        }

        if (checkInput(columnName, columnValue, `edit_error_message`)) {
            return;
        }

        columnName = columnName.replace(new RegExp(' ', 'g'),"_");
        columnName = columnName.toLowerCase();

        console.log(columnName);
        console.log(columnValue);

        columns.push(columnName);
        values.push(columnValue);

        i += 1;
    }

    // values.pop();
    // columns.pop();

    const payload = {
        'columns' : columns,
        'values' : values,
        'table' : currentEditCategory,
        'item_id' : currentEditID
    }

    const settings = {
        'method' : "POST",
        'headers' : { "Content-Type" : "application/json" },
        'body' : JSON.stringify(payload)
    }

    let url = apiURL+`/edit_item`;

    fetch(url, settings)
    .then((e) => {
        if (e.status === 200) {
            return e.text();
        } else {
            throw new Error("An untraceable error has occurred on our backend.");
        }
    })
    .then(e => {
        console.log(e);
        location.reload();
    })
    .catch(e => {
        document.getElementById(`edit_error_message`).textContent = e;
        console.error(e)
    });
}

let triggerAddModal = (category, type) => {
    console.log(type);
    currentEditCategory = category;
    currentEditType = type;
}

let submitAdd = () => {
    let loop = true;
    let i = 0;

    let columns = [];
    let values = [];

    while (loop) {
        let t  = document.getElementById(`add_${i}`);
        let k  = document.getElementById(`add_target_${i}`);

        if (t === null) {
            break;
        }

        let columnName = k.textContent;
        let columnValue;

        try {
            columnValue = t.value;
        } catch {
            columnValue = t.options[t.selectedIndex].value;
        }

        if (checkInput(columnName, columnValue, `add_error_message`)) {
            return;
        }

        let temp = k.textContent;
        var re = new RegExp(" ", 'g');

        temp = temp.replace(re,"_");
        temp = temp.toLowerCase();

        values.push(t.value);
        columns.push(temp);

        i += 1;
    }

    columns.push("type");
    values.push(currentEditType);

    console.log(columns);
    console.log(values);

    const payload = {
        'columns' : columns,
        'values' : values,
        'table' : currentEditCategory
    }

    const settings = {
        'method' : "POST",
        'headers' : { "Content-Type" : "application/json" },
        'body' : JSON.stringify(payload)
    }

    let url = apiURL+`/add_item`;

    fetch(url, settings)
    .then((e) => {
        if (e.status === 200) {
            return e.text();
        } else {
            throw new Error("An error has occured");
        }
    })
    .then(e => {
        console.log(e);
        location.reload();
    })
    .catch((e) => console.error(e));
}

















//////////////////////////////////////////////////////////////////////////////////////////////////
let submitCondChange = () => {
	let loop = true;
	let i = 0;

	let columns = [];
	let hvals = [];
	let lvals = [];

	while (loop) {
		//t
		let L = document.getElementById(`addL_${i}`);
		let H = document.getElementById(`addH_${i}`);
		let k = document.getElementById(`add_target_${i}`);

		if (L === null || H === null) {
			break;
		}

		let lowVal;
		let highVal;

		try {
			lowVal = L.value;
		} catch {
			lowVal = L.options[L.selectedIndex].value;
		}

		try {
			highVal = H.value;
		} catch {
			highVal = H.options[H.selectedIndex].value;
		}

		if (L.value === 0 || H.value === 0) {
			continue;
		}

		let columnName = k.textContent;
		console.error(lowVal);
		console.error(highVal);
		if (isNaN(highVal) || isNaN(lowVal)) {
			errormessage = "Error: all fields should contain a number";
			document.getElementById(`edit_error_message`).textContent = errormessage;
			console.error(errormessage);
			return;
		} else if (highVal < lowVal) {
			errormessage = "Error: all 'high' values must be greater than or equal to their 'low' values";
			document.getElementById(`cond_error_message`).textContent = errormessage;
			console.error(errormessage);
			return;
		}

		//columnName = columnName.replace(new RegExp(' ', 'g'), "_");
		//columnName = columnName.toLowerCase();

		//console.log(columnName);
		//console.log(columnValue);

		columns.push(columnName);
		hvals.push(highVal);
		lvals.push(lowVal);

		i += 1;
	}

	// values.pop();
	// columns.pop();

	const payload = {
		'hvals': hvals,
		'lvals': lvals,
		'type': columns,
	}

	const settings = {
		'method': "POST",
		'headers': { "Content-Type": "application/json" },
		'body': JSON.stringify(payload)
	}

	let url = apiURL + `/condF`;

	fetch(url, settings)
		.then((e) => {
			if (e.status === 200) {
				return e.text();
			} else {
				throw new Error("An untraceable error has occurred on our backend.");
			}
		})
		.then(e => {
			console.log(e);
			location.reload();
		})
		.catch(e => {
			document.getElementById(`cond_error_message`).textContent = e;
			console.error(e)
		});
}

let submitAddType = () => {
    var e = document.getElementById("addTypeSelector");
    var category = e.options[e.selectedIndex].value;

    var type = document.getElementById("addType").value;

    const payload = {
        'category' : category,
        'type' : type
    }

    const settings = {
        'method' : "POST",
        'headers' : { "Content-Type" : "application/json" },
        'body' : JSON.stringify(payload)
    }

    let url = apiURL+`/add_type`;

    fetch(url, settings)
    .then(e => {
        if (e.status === 200) {
            return e.text();
        } else {
            throw new Error("An error has occured");
        }
    })
    .then(e => {
        console.log(e);
        location.reload();
    })
    .catch((e) => console.error(e));
}

let checkInput = (columnName, columnValue, error_message_id) => {
    let numberColumns = ['Weight Per Piece','Weight Total', 'Storage', 'Quantity'];

    // console.log(columnValue);
    // console.log(isNumber(columnValue));

    let errormessage = null;

    if (columnValue.length === 0) {
        errormessage = "Error: "+columnName+" attribute should not be empty";
    }

    if (numberColumns.includes(columnName)) {
       if (isNaN(columnValue)) {
        errormessage = "Error: "+columnName+" attribute should contain a number";
        } else if (parseInt(columnValue) < 0) {
            errormessage = "Error: "+columnName+" attribute should be positive";
        } else if (parseInt(columnValue) >= 100000) {
            errormessage = "Error: "+columnName+" attribute should be less than 100000";
        }
    } else {
        if (columnValue.length > 20) {
            errormessage = "Error: "+columnName+" attribute should be less than 20 characters";
        }
    }

    if (errormessage != null) {
        document.getElementById(error_message_id).textContent = errormessage;
        console.error(errormessage);
        return true;
    }

    return false;
}






