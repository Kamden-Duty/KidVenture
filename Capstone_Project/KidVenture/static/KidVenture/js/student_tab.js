// main.js

// Helper to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      document.cookie.split(';').forEach(c => {
        const [k, v] = c.trim().split('=');
        if (k === name) cookieValue = decodeURIComponent(v);
      });
    }
    return cookieValue;
  }
  
  // Run once DOM is ready
  document.addEventListener("DOMContentLoaded", () => {
    // —— Account panel toggle
    const accountBtn    = document.getElementById("accountBtn");
    const closeBtn      = document.getElementById("closeBtn");
    const accountPanel  = document.getElementById("accountPanel");
  
    accountBtn.addEventListener("click", () => {
      accountPanel.classList.add("open");
    });
    closeBtn.addEventListener("click", () => {
      accountPanel.classList.remove("open");
    });
  
    // —— Notification dropdown & “mark all as read”
    const notificationBtn   = document.getElementById("notificationbtn");
    const notificationPanel = document.getElementById("notificationDropdown");
    const markAllBtn        = document.getElementById("mark-all-read");
    const notifCountBadge   = document.getElementById("notif-count");
  
    notificationBtn.addEventListener("click", () => {
      notificationPanel.classList.toggle("show");
    });
  
    if (markAllBtn) {
      markAllBtn.addEventListener("click", e => {
        e.preventDefault();
        fetch("/notifications/mark-all-read/", {    // or use: fetch("{% url 'mark_all_read' %}")
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
          }
        })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            // dim out each item
            document.querySelectorAll(".notification-item").forEach(li => {
              li.classList.remove("unread");
              li.classList.add("read");
            });
            // hide badge
            if (notifCountBadge) notifCountBadge.style.display = "none";
          }
        })
        .catch(console.error);
      });
    }
  
    // —— Inbox toggle
    const inboxIcon  = document.getElementById("inboxIcon");
    const inboxPanel = document.getElementById("inboxPanel");
  
    if (inboxIcon && inboxPanel) {
      inboxIcon.addEventListener("click", () => {
        inboxPanel.classList.toggle("open");
      });
    }
  });
  
  // allow closing inbox from inline onclicks
  window.closeInbox = function () {
    const inboxPanel = document.getElementById("inboxPanel");
    if (inboxPanel) inboxPanel.classList.remove("open");
  };
  
  // —— Tab switching logic (runs immediately)
  document.addEventListener("DOMContentLoaded", () => {
    const tabs         = document.querySelectorAll(".tab-link");
    const contents     = document.querySelectorAll(".tab-content");
    const progressCards = document.getElementById("progress-cards");
    const freeplayCards = document.getElementById("freeplay-cards");
  
    // activate “Home” by default
    const homeTab     = document.querySelector("[data-tab='home-tab']");
    const homeContent = document.getElementById("home-tab");
    if (homeTab && homeContent) {
      homeTab.classList.add("active");
      homeContent.classList.remove("hidden");
    }
  
    tabs.forEach(tab => {
      tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        contents.forEach(c => c.classList.add("hidden"));
  
        tab.classList.add("active");
        const tabId = tab.getAttribute("data-tab");
        document.getElementById(tabId).classList.remove("hidden");
  
        // show/hide progress vs freeplay
        if (progressCards)
          progressCards.classList.toggle("hidden", tabId !== "progress-tab");
        if (freeplayCards)
          freeplayCards.classList.toggle("hidden", tabId !== "activities-tab");
      });
    });
  });