let apiURL = 'http://127.0.0.1:5100';

let currentEditCategory = null;
let currentEditID = null;
let attributesLength = null;

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

let triggerEditModal = (category, id) => {
    currentEditCategory = category;
    currentEditID = id;

    let url = apiURL+`/get_item/${category}/${id}`;

    fetch(url)
	.then((e) => {
		if (e.status === 200) {
			return e.json();
		} else {
            throw new Error("An error has occured");
		}
    })
    .then(e => {
        i = 0;
        e.response.shift();

        e.response.map(k => {
            let t = document.getElementById(`edit_${i}`);
            t.setAttribute('value', k);
        
            i += 1;
        })
    })
    .catch((e) => console.error(e));
}

let submitEdit = () => {
    let loop = true;
    let i = 0;

    while (loop) {
        let t  = document.getElementById(`edit_${i}`);
        let k  = document.getElementById(`edit_target_${i}`);

        if (t === null) {
            break;
        }

        const payload = {
            'test' : t.value,
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
        })
        .catch((e) => console.error(e));
    

        console.log(t.value);
        console.log(k.textContent);

        i += 1;
    }
    
    console.log(currentEditCategory);
    console.log(currentEditID);
}