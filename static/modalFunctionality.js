let apiURL = 'http://127.0.0.1:5100';

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
    // console.log('yeet');
    // let modal_container = document.getElementById('edit-modal-target');

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
            // console.log(i);
            // console.log(t);
            // t.innerHTML = `<span>${k}</span>`

            i += 1;
        })
        console.log(e);


    })
    .catch((e) => console.error(e));
}
