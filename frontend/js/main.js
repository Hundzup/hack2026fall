async function loadItems() {
  const ul = document.getElementById('items');
  if (!ul) return;
  try {
    const res = await fetch('/api/items');
    const items = await res.json();
    ul.innerHTML = '';
    items.forEach(it => {
      const li = document.createElement('li');
      li.textContent = `#${it.id} ${it.name} = ${it.value}`;
      ul.appendChild(li);
    });
  } catch (e) {
    ul.innerHTML = `<li>Ошибка загрузки: ${e.message}</li>`;
  }
}
loadItems();