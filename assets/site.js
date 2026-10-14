// Language is encoded in static URLs; no cookies, storage, or network requests.
// Preserve the section when switching between translated versions of a page.
function syncLanguageAnchors() {
  document.querySelectorAll('.language-switch a').forEach(link => {
    const target = new URL(link.href);
    target.hash = window.location.hash;
    link.href = target.href;
  });
}
syncLanguageAnchors();
window.addEventListener('hashchange', syncLanguageAnchors);
