document.documentElement.classList.add('js');
const toggle = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('open', open);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
    toggle.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('open');
    toggle.focus();
  }
});
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  toggle.setAttribute('aria-expanded', 'false');
  navigation.classList.remove('open');
}));
document.querySelectorAll('[data-filter]').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-filter]').forEach(item => {
      item.classList.toggle('active', item === button);
      item.setAttribute('aria-pressed', String(item === button));
    });
    document.querySelectorAll('[data-category]').forEach(look => {
      look.hidden = button.dataset.filter !== 'all' && look.dataset.category !== button.dataset.filter;
    });
    const count = document.querySelectorAll('[data-category]:not([hidden])').length;
    document.querySelector('#filter-status').textContent = `Showing ${count} ${count === 1 ? 'look' : 'looks'}.`;
  });
});
document.querySelector('#brief-form').addEventListener('submit', event => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const name = String(form.get('name')).trim();
  const message = String(form.get('message')).trim();
  if (!name || !message) {
    document.querySelector('#form-status').textContent = 'Please enter your name and a short description.';
    return;
  }
  const brief = `KT CLOTHING — DESIGN BRIEF\n\nName: ${name}\nInterest: ${form.get('interest')}\nPreferred color: ${String(form.get('color') || '').trim() || 'To discuss'}\nBudget (ETB): ${form.get('budget') || 'To discuss'}\n\n${message}\n`;
  const url = URL.createObjectURL(new Blob([brief], {type: 'text/plain;charset=utf-8'}));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'kt-clothing-design-brief.txt';
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  document.querySelector('#form-status').textContent = 'Your brief is ready. Keep the downloaded file to share with your designer.';
});
document.querySelector('#year').textContent = new Date().getFullYear();

// Only confirmed business contacts are rendered. No credentials belong in this file.
const contacts = window.KT_BUSINESS || {};
const container = document.querySelector('#business-contacts');
const phone = String(contacts.phone || '').replace(/[\s()-]/g, '');
function contactLink(label, href, external = true) {
  const link = document.createElement('a');
  link.textContent = label + (external ? ' ↗' : '');
  link.href = href;
  if (external) { link.target = '_blank'; link.rel = 'noopener noreferrer'; }
  container.append(link);
}
if (/^\+[1-9]\d{7,14}$/.test(phone)) contactLink('Call ' + contacts.phone, 'tel:' + phone, false);
const hosts = {instagram: ['instagram.com', 'www.instagram.com'], tiktok: ['tiktok.com', 'www.tiktok.com'], facebook: ['facebook.com', 'www.facebook.com', 'm.facebook.com'], telegram: ['t.me', 'telegram.me']};
for (const [platform, allowed] of Object.entries(hosts)) {
  try {
    const url = new URL(contacts[platform]);
    if (url.protocol === 'https:' && !url.username && !url.password && allowed.includes(url.hostname) && url.pathname !== '/') {
      contactLink(platform[0].toUpperCase() + platform.slice(1), url.href);
    }
  } catch { /* An unconfigured or invalid profile stays hidden. */ }
}
if (container.children.length) document.querySelector('#contact-pending').hidden = true;
