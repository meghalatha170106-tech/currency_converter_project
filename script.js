function swapCurrency() {
    let from = document.getElementsByName("from_currency")[0];
    let to = document.getElementsByName("to_currency")[0];

    let temp = from.value;
    from.value = to.value;
    to.value = temp;
}

function toggleDarkMode() {
    document.body.classList.toggle("dark");
}

function addFavorite() {
    alert("Favorite added!");
}

const ctx = document.getElementById('myChart');
if (ctx) {
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["1","2","3","4"],
            datasets: [{
                label: 'Currency Trend',
                data: [10,20,15,30]
            }]
        }
    });
}

function searchTable() {
    const searchInput = document.getElementById("search");
    if (!searchInput) return;

    let input = searchInput.value.toLowerCase();
    let rows = document.querySelectorAll("table tr");

    rows.forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(input) ? "" : "none";
    });
}

document.querySelectorAll("input, select").forEach(el => {
    el.addEventListener("change", () => {
        const form = document.querySelector("form");
        if (form) form.submit();
    });
});

function changeLanguage(lang) {
    // replace text dynamically
}

setInterval(() => {
    location.reload();
}, 10000);

if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.body.classList.add('dark');
}


