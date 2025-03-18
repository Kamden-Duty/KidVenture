function filterByClass() {
    let selectedClass = document.getElementById("class-filter").value;
    let rows = document.querySelectorAll(".student-row");

    rows.forEach(row => {
        let studentClass = row.getAttribute("data-class");
        if (selectedClass === "all" || studentClass === selectedClass) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

function filterTable() {
    let input = document.getElementById("search-bar").value.toLowerCase();
    let rows = document.querySelectorAll(".student-row");

    rows.forEach(row => {
        let studentName = row.cells[0].textContent.toLowerCase();
        if (studentName.includes(input)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

// Export Table to CSV
function exportTableToCSV() {
    let csv = [];
    let rows = document.querySelectorAll("table tr");

    rows.forEach(row => {
        let cols = row.querySelectorAll("th, td");
        let rowData = [];
        cols.forEach(col => rowData.push(col.innerText));
        csv.push(rowData.join(","));
    });

    let csvString = csv.join("\n");
    let blob = new Blob([csvString], { type: "text/csv" });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "progress_report.csv";
    link.click();
}
