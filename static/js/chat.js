document.addEventListener("DOMContentLoaded", () => {
  scrollMessagesToBottom();
  setupComposerLock();
  setupMobileSidebar();
  setupCompanionTools();
  setupInlinePlayers();
});

window.addEventListener("pageshow", scrollMessagesToBottom);

function scrollMessagesToBottom() {
  const messages = document.querySelector(".messages");
  if (!messages) return;
  requestAnimationFrame(() => {
    messages.scrollTop = messages.scrollHeight;
  });
}

function setupComposerLock() {
  const form = document.querySelector(".composer");
  if (!form) return;

  const textarea = form.querySelector("textarea");
  const fileInput = form.querySelector("input[type='file']");
  const button = form.querySelector("button[type='submit']");

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const label = fileInput.closest(".attach-button");
      if (label && fileInput.files.length) {
        label.classList.add("has-file");
        label.childNodes[0].textContent = "已選照片";
      }
    });
  }

  form.addEventListener("submit", (event) => {
    const hasText = textarea && textarea.value.trim();
    const hasFile = fileInput && fileInput.files.length;
    if (!hasText && !hasFile) {
      event.preventDefault();
      return;
    }
    if (button) {
      button.disabled = true;
      button.textContent = "回覆中";
    }
    if (textarea) {
      textarea.readOnly = true;
    }
  });
}

function setupMobileSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const openButton = document.querySelector("#mobileMenuButton");
  const scrim = document.querySelector("#mobileScrim");
  if (!sidebar || !openButton || !scrim) return;

  const close = () => {
    sidebar.classList.remove("is-open");
    scrim.classList.remove("is-visible");
  };

  openButton.addEventListener("click", () => {
    sidebar.classList.add("is-open");
    scrim.classList.add("is-visible");
  });
  scrim.addEventListener("click", close);
  document.querySelectorAll(".conversation-list a").forEach((link) => {
    link.addEventListener("click", close);
  });
}

function setupCompanionTools() {
  const panel = document.querySelector("#companionPanel");
  const title = document.querySelector("#toolPanelTitle");
  const collapseButton = document.querySelector("#collapseTools");
  const openToolDrawer = document.querySelector("#openToolDrawer");
  const titles = {
    media: "影音探索",
    photo: "照片理解"
  };

  if (openToolDrawer && panel) {
    openToolDrawer.addEventListener("click", () => {
      panel.classList.toggle("is-collapsed");
      if (collapseButton) {
        collapseButton.textContent = panel.classList.contains("is-collapsed") ? "展開" : "收合";
      }
    });
  }

  document.querySelectorAll("[data-tool-section-button]").forEach((button) => {
    button.addEventListener("click", () => {
      const tool = button.dataset.toolSectionButton;
      panel.classList.remove("is-collapsed");
      document.querySelectorAll("[data-tool-section]").forEach((section) => {
        section.classList.toggle("active", section.dataset.toolSection === tool);
      });
      if (title) title.textContent = titles[tool] || "工具抽屜";
    });
  });

  if (collapseButton && panel) {
    collapseButton.addEventListener("click", () => {
      panel.classList.toggle("is-collapsed");
      collapseButton.textContent = panel.classList.contains("is-collapsed") ? "展開" : "收合";
    });
  }

  setupYoutubeSearch();
  setupCompanionSearch();
}

function setupYoutubeSearch() {
  const queryInput = document.querySelector("#youtubeQuery");
  const searchButton = document.querySelector("#searchYoutube");
  const resultsBox = document.querySelector("#youtubeResults");
  const youtubeFrame = document.querySelector("#youtubeFrame");

  const playVideo = (video) => {
    if (!youtubeFrame) return;
    youtubeFrame.innerHTML = "";
    const iframe = document.createElement("iframe");
    iframe.src = `https://www.youtube.com/embed/${video.id}?autoplay=1&playsinline=1`;
    iframe.title = video.title;
    iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    iframe.allowFullscreen = true;
    youtubeFrame.appendChild(iframe);
  };

  const renderResults = (results) => {
    if (!resultsBox) return;
    resultsBox.innerHTML = "";
    if (!results.length) {
      resultsBox.innerHTML = "<p class='tool-copy'>沒有找到影片，換個關鍵字試試。</p>";
      return;
    }
    results.forEach((video) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "media-result";
      button.innerHTML = `
        <img src="${video.thumbnail}" alt="">
        <span>
          <strong>${escapeHtml(video.title)}</strong>
          <small>${escapeHtml(video.channel || "YouTube")}</small>
          <em>如果小窗不能播放，可用原影片連結開啟</em>
        </span>
      `;
      button.addEventListener("click", () => playVideo(video));
      resultsBox.appendChild(button);
    });
  };

  const search = async () => {
    const query = queryInput?.value.trim();
    if (!query) return;
    resultsBox.innerHTML = "<p class='tool-copy'>搜尋中...</p>";
    try {
      const response = await fetch(`/api/tools/youtube-search/?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      renderResults(data.results || []);
    } catch {
      resultsBox.innerHTML = "<p class='tool-copy'>搜尋暫時失敗，等一下再試。</p>";
    }
  };

  if (searchButton) searchButton.addEventListener("click", search);
  if (queryInput) {
    queryInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") search();
    });
  }

  document.querySelectorAll("[data-fill-query]").forEach((button) => {
    button.addEventListener("click", () => {
      if (queryInput) queryInput.value = button.dataset.fillQuery;
      search();
    });
  });
}

function setupCompanionSearch() {
  const input = document.querySelector("#companionQuery");
  const button = document.querySelector("#searchCompanion");
  const box = document.querySelector("#companionResults");

  const search = async () => {
    const query = input?.value.trim();
    if (!query) return;
    box.innerHTML = "<p class='tool-copy'>整理中...</p>";
    try {
      const response = await fetch(`/api/tools/companion-search/?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      box.innerHTML = "";
      (data.links || []).forEach((link) => {
        const anchor = document.createElement("a");
        anchor.href = link.url;
        anchor.target = "_blank";
        anchor.rel = "noopener noreferrer";
        anchor.className = "link-result";
        anchor.innerHTML = `<strong>${escapeHtml(link.label)}</strong><span>${escapeHtml(link.description)}</span>`;
        box.appendChild(anchor);
      });
    } catch {
      box.innerHTML = "<p class='tool-copy'>暫時無法產生搜尋卡。</p>";
    }
  };

  if (button) button.addEventListener("click", search);
  if (input) {
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") search();
    });
  }
}

function setupInlinePlayers() {
  document.querySelectorAll(".inline-media-item").forEach((button) => {
    button.addEventListener("click", () => {
      const card = button.closest(".inline-tool-card");
      const player = card?.querySelector("[data-inline-player]");
      if (!player) return;
      player.innerHTML = "";
      const iframe = document.createElement("iframe");
      iframe.src = `https://www.youtube.com/embed/${button.dataset.videoId}?autoplay=1&playsinline=1`;
      iframe.title = button.dataset.videoTitle || "YouTube";
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      iframe.allowFullscreen = true;
      player.appendChild(iframe);
    });
  });
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
