function filterByClass() {
    let selectedClass = document.getElementById("class-filter").value;
    let rows = document.querySelectorAll(".student-row");

    rows.forEach(row => {
        let rowClassId = row.getAttribute("data-class-id");

        let matches = selectedClass === "all" || rowClassId === selectedClass;

        row.style.display = matches ? "" : "none";
    });

    filterByActivity();
    applyAlternatingRowColors();
}


function filterByActivity() {
    let selectedActivity = document.getElementById("activity-filter").value.toLowerCase();
    let rows = document.querySelectorAll(".student-row");
    let visibleRows = [];

    rows.forEach(row => {
        let rowActivity = row.getAttribute("data-activity")?.toLowerCase() || "";
        if (selectedActivity === "all" || rowActivity === selectedActivity) {
            row.style.display = "";
            visibleRows.push(row);
        } else {
            row.style.display = "none";
        }
    });

    applyAlternatingRowColors();
}

function filterTable() {
    let selectedClass = document.getElementById("class-filter").value;
    let selectedActivity = document.getElementById("activity-filter").value.toLowerCase();
    let searchText = document.getElementById("search-bar").value.toLowerCase();
    let rows = document.querySelectorAll(".student-row");
    let visibleRows = [];

    rows.forEach(row => {
        let rowClass = row.getAttribute("data-class");
        let rowActivity = row.getAttribute("data-activity")?.toLowerCase() || "";
        let studentName = row.querySelector("td").textContent.toLowerCase();

        let classMatch = selectedClass === "all" || rowClass === selectedClass;
        let activityMatch = selectedActivity === "all" || rowActivity === selectedActivity;
        let nameMatch = studentName.includes(searchText);

        if (classMatch && activityMatch && nameMatch) {
            row.style.display = "";
            visibleRows.push(row);
        } else {
            row.style.display = "none";
        }
    });

    applyAlternatingRowColors();
}

// Function to apply the correct alternating row colors
function applyAlternatingRowColors() {
    let visibleRows = [...document.querySelectorAll(".student-row")].filter(row => row.style.display !== "none");

    visibleRows.forEach((row, index) => {
        if (index % 2 === 0) {
            row.style.backgroundColor = "#b0c9c4"; // Cool Gray (odd rows)
           
        } else {
            row.style.backgroundColor = "#cadec8"; // Soft Mint (even rows)
        }
    });
}


function exportTableToCSV() {
    let csv = [];
    let rows = document.querySelectorAll("table tr");

    rows.forEach(row => {
        // Only include rows that are visible
        if (row.style.display === "none") return;

        let cols = row.querySelectorAll("th, td");
        let rowData = [];

        cols.forEach(col => {
            let text = col.innerText.replace(/,/g, ""); // Remove commas to avoid breaking CSV
            rowData.push(text);
        });

        csv.push(rowData.join(","));
    });

    let csvString = csv.join("\n");
    let blob = new Blob([csvString], { type: "text/csv" });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "progress_report.csv";
    link.click();
}


document.addEventListener("DOMContentLoaded", function () {
    const classFilter = document.getElementById("class-filter");
    const activityFilter = document.getElementById("activity-filter");
    const searchBar = document.getElementById("search-bar");

    classFilter.addEventListener("change", function () {
        const classId = this.value;
        activityFilter.innerHTML = '<option value="all">All Activities</option>';
        activityFilter.disabled = true;

        if (classId !== "all") {
            fetch(`/get_class_activities/${classId}/`)
                .then(response => response.json())
                .then(data => {
                    data.activities.forEach(activity => {
                        let option = document.createElement("option");
                        option.value = activity;
                        option.textContent = activity;
                        activityFilter.appendChild(option);
                    });
                    activityFilter.disabled = false;
                })
                .catch(error => console.error("Error fetching activities:", error));
        }

        filterByClass(); // Ensure students are shown immediately when selecting a class
    });

    activityFilter.addEventListener("change", filterByActivity);
    searchBar.addEventListener("keyup", filterTable);
});