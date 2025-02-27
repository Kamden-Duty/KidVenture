document.querySelectorAll(".tab-link").forEach((button) => {
    button.addEventListener("click", () => {
        document.querySelectorAll(".tab-link").forEach((btn) => btn.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach((section) => btn.classList.add("hidden"));

        button.classList.add("active");
        const target = document.getElementById(button.dataset.tab);
        target.classList.remove("hidden");
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".tab-link");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((t) => t.classList.remove("active"));

            // Add 'hidden' class to all tab contents
            contents.forEach((content) => content.classList.add("hidden"));

            // Activate clicked tab
            tab.classList.add("active");

            // Show corresponding tab content
            const tabId = tab.getAttribute("data-tab");
            document.getElementById(tabId).classList.remove("hidden");
        });
    });
});