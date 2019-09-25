let apiURL = 'http://127.0.0.1:5100';

let triggerModal = (id) => {
    let modal_container = document.getElementById('modal-target');

    let url = apiURL+`/get_history/${id}`;

    console.log(url);

    fetch(url)
	.then((e) => {
		if (e.status === 200) {
			return e.json();
		} else {
            throw new Error("An error has occured");
		}
    })
    .then((e) => {
        console.log(e);

        console.log(e['response'].length);
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

        console.log(_innerHTML);
 
        modal_container.innerHTML = _innerHTML;
    })
	.catch((e) => console.error(e));

}


// console.log('yeet')