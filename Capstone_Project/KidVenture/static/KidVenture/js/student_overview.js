// Filter table rows based on search input
function filterTable() {
    let input = document.getElementById("search-bar").value.toLowerCase();
    let rows = document.querySelectorAll(".student-row");

    rows.forEach(row => {
        let studentName = row.cells[0].textContent.toLowerCase();
        let className = row.cells[1].textContent.toLowerCase();
        let selectedClass = document.getElementById("class-filter").value.toLowerCase();
        
        let matchesClass = (selectedClass === "all" || className === selectedClass);
        let matchesSearch = studentName.includes(input) || className.includes(input);

        row.style.display = (matchesClass && matchesSearch) ? "" : "none";
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

// Export only visible table rows as CSV
function exportTableToCSV() {
    let table = document.getElementById("student-table");
    let rows = document.querySelectorAll(".student-row");
    let visibleRows = Array.from(rows).filter(row => row.style.display !== "none"); // Export only visible rows

    if (visibleRows.length === 0) {
        alert("No data to export!");
        return;
    }

    let csvContent = [];
    
    // Add table headers
    let headers = Array.from(table.querySelectorAll("thead th")).map(th => `"${th.textContent}"`);
    csvContent.push(headers.join(","));

    // Add visible rows
    visibleRows.forEach(row => {
        let rowData = Array.from(row.cells).map(cell => `"${cell.textContent}"`);
        csvContent.push(rowData.join(","));
    });

    let csvString = csvContent.join("\n");
    let blob = new Blob([csvString], { type: "text/csv" });
    let url = URL.createObjectURL(blob);
    let link = document.createElement("a");
    link.href = url;
    link.download = "student_overview.csv";
    link.click();
}

// Confirm student removal
function confirmRemoveStudent() {
    return confirm("Are you sure you want to remove this student from the class?");
}

// Filter students by class selection
function filterByClass() {
    filterTable(); // Call the filtering function so it applies both search & class filtering
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("class-filter").addEventListener("change", filterByClass);
    document.getElementById("search-bar").addEventListener("keyup", filterTable);
});
