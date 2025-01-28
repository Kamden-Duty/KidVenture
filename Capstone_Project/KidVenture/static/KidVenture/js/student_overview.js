// static/js/student_overview.js

// Filter table rows based on search input
function filterTable() {
    let input = document.getElementById("search-bar").value.toLowerCase();
    let rows = document.querySelectorAll("#student-table tbody tr");

    rows.forEach(row => {
        let studentName = row.cells[0].textContent.toLowerCase();
        let className = row.cells[1].textContent.toLowerCase();
        row.style.display = (studentName.includes(input) || className.includes(input)) ? "" : "none";
    });
}

// Sort table by column index
function sortTable(columnIndex) {
    let table = document.getElementById("student-table");
    let rows = Array.from(table.rows).slice(1); // Exclude header row
    let isAscending = table.getAttribute("data-sort-asc") === "true";
    table.setAttribute("data-sort-asc", !isAscending);

    rows.sort((a, b) => {
        let aText = a.cells[columnIndex].textContent.trim().toLowerCase();
        let bText = b.cells[columnIndex].textContent.trim().toLowerCase();

        return isAscending
            ? (aText > bText ? 1 : -1)
            : (aText < bText ? 1 : -1);
    });

    rows.forEach(row => table.tBodies[0].appendChild(row));
}

// Export table data as CSV
function exportTableToCSV() {
    let table = document.getElementById("student-table");
    let rows = table.querySelectorAll("tr");
    let csvContent = Array.from(rows).map(row => {
        return Array.from(row.cells).map(cell => `"${cell.textContent}"`).join(",");
    }).join("\n");

    let blob = new Blob([csvContent], { type: "text/csv" });
    let url = URL.createObjectURL(blob);
    let link = document.createElement("a");
    link.href = url;
    link.download = "student_overview.csv";
    link.click();
}
