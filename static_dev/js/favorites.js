/* static/js/favorites.js */
(function () {
  const LS_KEY = 'sf_favorites_v1';

  // ---------- ХРАНИЛИЩЕ ----------
  function loadFavs() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      console.warn('Favorites parse error', e);
      return [];
    }
  }
  function saveFavs(list) {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(list));
    } catch (e) {
      console.warn('Favorites save error', e);
    }
  }
  function getIndex(list, id) {
    return list.findIndex(x => String(x.id) === String(id));
  }
  function isFav(id) {
    return getIndex(loadFavs(), id) !== -1;
  }
  function addFav(item) {
    const list = loadFavs();
    if (getIndex(list, item.id) === -1) {
      list.push(item);
      saveFavs(list);
      dispatch();
    }
  }
  function removeFav(id) {
    const list = loadFavs();
    const idx = getIndex(list, id);
    if (idx !== -1) {
      list.splice(idx, 1);
      saveFavs(list);
      dispatch();
    }
  }
  function toggleFav(item) {
    if (isFav(item.id)) removeFav(item.id);
    else addFav(item);
  }

  // ---------- СОБЫТИЯ / СТЕЙТ ----------
  const EVENT = 'sf:favs-changed';
  function dispatch() {
    document.dispatchEvent(new CustomEvent(EVENT, { detail: loadFavs() }));
  }

  // ---------- UI СВЯЗКИ ----------
  function updateHeaderCount() {
  const n = loadFavs().length;
  document.querySelectorAll('[data-fav-count]').forEach(el => {
    el.textContent = n > 0 ? String(n) : '';
  });
}

  function markButtons() {
    document.querySelectorAll('[data-fav-btn]').forEach(btn => {
      const id = btn.getAttribute('data-product-id');
      btn.classList.toggle('is-active', isFav(id));
      const labelAdd = btn.getAttribute('data-label-add') || 'В избранное';
      const labelRemove = btn.getAttribute('data-label-remove') || 'В избранном';
      const icon = btn.querySelector('[data-fav-icon]');
      const text = btn.querySelector('[data-fav-text]');
      if (text) text.textContent = isFav(id) ? labelRemove : labelAdd;
      if (icon) icon.classList.toggle('is-active', isFav(id));
      btn.setAttribute('aria-pressed', isFav(id) ? 'true' : 'false');
    });
  }

  function buildDrawerList() {
    const wrap = document.querySelector('#favorites-list');
    if (!wrap) return;
    const list = loadFavs();
    if (!list.length) {
      wrap.innerHTML = `<div class="fav-empty">В избранном пока пусто.</div>`;
      return;
    }
    wrap.innerHTML = list.map(item => `
      <div class="fav-item" data-fav-item="${item.id}">
        <a class="fav-thumb" href="${item.url}" aria-label="${item.name}">
          ${item.image ? `<img src="${item.image}" alt="${item.name}">` : ''}
        </a>
        <div class="fav-info">
          <a class="fav-title" href="${item.url}">${item.name}</a>
          ${item.price ? `<div class="fav-price">${item.price}</div>` : ''}
        </div>
        <button class="fav-remove" data-remove-fav="${item.id}" aria-label="Убрать из избранного">×</button>
      </div>
    `).join('');
  }

  function openDrawer() {
    const drawer = document.querySelector('#favorites-drawer');
    if (!drawer) return;
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
    buildDrawerList();
  }
  function closeDrawer() {
    const drawer = document.querySelector('#favorites-drawer');
    if (!drawer) return;
    drawer.classList.remove('open');
    document.body.style.overflow = '';
  }

  // ---------- ДЕЛЕГИРОВАНИЕ ----------
  document.addEventListener('click', (e) => {
    // Тоггл избранного на кнопках
    const btn = e.target.closest('[data-fav-btn]');
    if (btn) {
      e.stopPropagation();
      e.preventDefault();
      const payload = {
        id: btn.getAttribute('data-product-id'),
        name: btn.getAttribute('data-product-name') || '',
        image: btn.getAttribute('data-product-image') || '',
        url: btn.getAttribute('data-product-url') || '#',
        price: btn.getAttribute('data-product-price') || ''
      };
      toggleFav(payload);
      markButtons();
      updateHeaderCount();
      return;
    }

    // Открыть/закрыть шторку
    if (e.target.closest('[data-open-favorites]')) {
      e.preventDefault();
      openDrawer();
      return;
    }
    if (e.target.closest('[data-close-favorites]') || e.target.classList.contains('drawer-overlay')) {
      e.preventDefault();
      closeDrawer();
      return;
    }

    // Удаление из списка внутри шторки
    const rm = e.target.closest('[data-remove-fav]');
    if (rm) {
      const id = rm.getAttribute('data-remove-fav');
      removeFav(id);
      buildDrawerList();
      markButtons();
      updateHeaderCount();
      return;
    }
  });

  // ---------- ИНИТ ----------
  document.addEventListener('DOMContentLoaded', () => {
    markButtons();
    updateHeaderCount();
    buildDrawerList();
  });
  document.addEventListener(EVENT, () => {
    markButtons();
    updateHeaderCount();
    buildDrawerList();
  });

  // Экспорт на всякий случай (если понадобится в другом коде)
  window.SFFavorites = { loadFavs, saveFavs, isFav, addFav, removeFav, toggleFav, openDrawer, closeDrawer };
})();
