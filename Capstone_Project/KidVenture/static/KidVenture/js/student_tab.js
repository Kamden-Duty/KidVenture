// Account panel toggle
const accountBtn = document.getElementById("accountBtn");
const notificationbtn = document.getElementById("notificationbtn");
const accountPanel = document.getElementById("accountPanel");
const notificationPanel = document.getElementById("notificationDropdown");
const closeBtn = document.getElementById("closeBtn");

accountBtn.addEventListener("click", () => {
  accountPanel.classList.add("open");
});
closeBtn.addEventListener("click", () => {
  accountPanel.classList.remove("open");
});

notificationbtn.addEventListener("click", () => {
  notificationPanel.classList.toggle("show");
});

// Inbox toggle
const inboxIcon = document.getElementById("inboxIcon");
const inboxPanel = document.getElementById("inboxPanel");

inboxIcon.addEventListener("click", () => {
  inboxPanel.classList.toggle("open");
});

window.closeInbox = function () {
  inboxPanel.classList.remove("open");
};

// Tab switching
document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab-link");
  const contents = document.querySelectorAll(".tab-content");
  const viewProgressButtons = document.querySelectorAll(".view-progress-btn");
  const progressCards = document.getElementById("progress-cards");
  const freeplayCards = document.getElementById("freeplay-cards");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      contents.forEach((content) => content.classList.add("hidden"));
      tab.classList.add("active");
      const tabId = tab.getAttribute("data-tab");
      document.getElementById(tabId).classList.remove("hidden");

      // Show or hide progress cards based on the active tab
      if (tabId === "progress-tab") {
        progressCards.classList.remove("hidden");
      } else {
        progressCards.classList.add("hidden");
      }

      if (tabId === "activities-tab") {
        freeplayCards.classList.remove("hidden");
      }
      else {
        freeplayCards.classList.add("hidden");
      }
    });
  });

  // viewProgressButtons.forEach((button) => {
  //   button.addEventListener("click", () => {
  //     document.querySelectorAll(".tab-link").forEach(tab => tab.classList.remove("active"));
  //     document.querySelectorAll(".tab-content").forEach(content => content.classList.add("hidden"));
  
  //     // Activate progress tab
  //     document.querySelector("[data-tab='progress-tab']").classList.add("active");
  //     document.getElementById("progress-tab").classList.remove("hidden");

  //     // Show progress cards
  //     progressCards.forEach((card) => card.classList.remove("hidden"));
  
  //     document.getElementById("progress-tab").scrollIntoView({ behavior: 'smooth' });
  //   });
  // });
});