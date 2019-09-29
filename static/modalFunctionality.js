let apiURL = 'http://127.0.0.1:5100';
//let apiURL = 'https://forze.pythonanywhere.com';

let currentEditCategory = null;
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
let triggerEditModal = (category, id) => {
    currentEditCategory = category;
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

        let num1 = parseFloat(e.response[e.response.length-1]);
        let num2 = parseFloat(e.response[e.response.length-2]);

        let quantity = parseInt(num1/num2);

        document.getElementById(`edit_${i}`).setAttribute('value', quantity);
    })
    .catch((e) => console.error(e));
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

        let temp = k.textContent;
        temp = temp.replace(new RegExp(' ', 'g'),"_");
        temp = temp.toLowerCase();

        console.log(temp);
        console.log(t.value);

        values.push(t.value);
        columns.push(temp);    

        i += 1;
    }

    let quantityValue  = values[values.length-1];
    values.pop();
    columns.pop();

    let totalValue = values[values.length-2]*quantityValue;
    values[values.length-1] = totalValue;

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
            throw new Error("An error has occured");
        }
    })
    .then(e => {
        console.log(e);
        location.reload();
    })
    .catch((e) => console.error(e));
}

let triggerAddModal = (category) => {
    currentEditCategory = category;
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

        let temp = k.textContent;
        var re = new RegExp(" ", 'g');

        temp = temp.replace(re,"_");
        temp = temp.toLowerCase();
        // console.log(temp)

        values.push(t.value);
        columns.push(temp);

        i += 1;
    }

    let quantityValue  = values[values.length-1];
    values.pop();
    columns.pop();

    let totalValue = values[values.length-2]*quantityValue;
    values[values.length-1] = totalValue;

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

//Opens the modal that enables the user to edit an entry
let triggerEditCondFormatting = () => {
	console.log("Tester");
	/* currentEditCategory = category;
	currentEditID = id;

	let url = apiURL + `/get_item/${category}/${id}`;

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

			let num1 = parseFloat(e.response[e.response.length - 1]);
			let num2 = parseFloat(e.response[e.response.length - 2]);

			let quantity = parseInt(num1 / num2);

			document.getElementById(`edit_${i}`).setAttribute('value', quantity);
		})
		.catch((e) => console.error(e));
	*/
}