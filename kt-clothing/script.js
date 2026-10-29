const toggle = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('open', open);
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
  const brief = `KT CLOTHING — DESIGN BRIEF\n\nName: ${name}\nInterest: ${form.get('interest')}\n\n${message}\n`;
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
