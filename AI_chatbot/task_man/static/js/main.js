// Task_Man — shared front-end behavior

function toggleSidebar() {
  document.querySelector(".sidebar")?.classList.toggle("open");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.innerText = str;
  return div.innerHTML;
}

// Very small markdown-ish renderer: bold, code blocks, inline code, line breaks, lists
function renderMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/```([\s\S]*?)```/g, (m, code) => `<pre><code>${code.trim()}</code></pre>`);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/^- (.+)$/gm, "• $1");
  html = html.replace(/\n/g, "<br>");
  return html;
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => { el.style.opacity = "0"; }, 4000);
  });
});
