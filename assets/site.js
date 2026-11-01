// Language is encoded in static URLs; no cookies, storage, or network requests.
// Preserve the section when switching between translated versions of a page.
function syncLanguageAnchors() {
  document.querySelectorAll('.language-options a').forEach(link => {
    const target = new URL(link.href);
    target.hash = window.location.hash;
    link.href = target.href;
  });
}
syncLanguageAnchors();
window.addEventListener('hashchange', syncLanguageAnchors);
const languageMenu = document.querySelector('.language-switch');
if (languageMenu) {
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && languageMenu.open) {
      languageMenu.open = false;
      languageMenu.querySelector('summary').focus();
    }
  });
  document.addEventListener('click', event => {
    if (languageMenu.open && !languageMenu.contains(event.target)) languageMenu.open = false;
  });
}
