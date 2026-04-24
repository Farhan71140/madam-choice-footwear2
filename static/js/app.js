// ============================================================
// MADAM CHOICE FOOTWEAR — app.js
// ============================================================

// ─────────────────────────────────────────
// 🛒 CART FUNCTIONS
// ─────────────────────────────────────────

function addToCart(name, price) {
  let cart = JSON.parse(localStorage.getItem('cart') || '[]');
  const existing = cart.find(i => i.name === name);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ name, price: parseFloat(price), quantity: 1 });
  }
  localStorage.setItem('cart', JSON.stringify(cart));
  showToast(`✅ "${name}" added to cart!`);
  updateCartBadge();
}

function getCartCount() {
  const cart = JSON.parse(localStorage.getItem('cart') || '[]');
  return cart.reduce((sum, i) => sum + i.quantity, 0);
}

function updateCartBadge() {
  const badge = document.getElementById('cartBadge');
  if (!badge) return;
  const count = getCartCount();
  badge.innerText = count;
  badge.style.display = count > 0 ? 'inline-block' : 'none';
}

// ─────────────────────────────────────────
// 💳 PAYMENT
// ─────────────────────────────────────────

function startPayment() {
  const cart = JSON.parse(localStorage.getItem('cart') || '[]');
  if (cart.length === 0) {
    showToast('Your cart is empty! Add items first.', 'error');
    return;
  }
  window.location.href = '/pay';
}

// ─────────────────────────────────────────
// 🍞 TOAST NOTIFICATION
// ─────────────────────────────────────────

function showToast(message, type = 'success') {
  const existing = document.getElementById('globalToast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'globalToast';
  toast.innerText = message;

  Object.assign(toast.style, {
    position:     'fixed',
    bottom:       '28px',
    left:         '50%',
    transform:    'translateX(-50%) translateY(80px)',
    background:   type === 'error' ? '#e53935' : '#1a237e',
    color:        'white',
    padding:      '14px 28px',
    borderRadius: '50px',
    fontSize:     '0.95rem',
    fontWeight:   '600',
    zIndex:       '99999',
    boxShadow:    '0 5px 20px rgba(0,0,0,0.25)',
    transition:   'transform 0.35s ease',
    whiteSpace:   'nowrap',
  });

  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      toast.style.transform = 'translateX(-50%) translateY(0)';
    });
  });

  setTimeout(() => {
    toast.style.transform = 'translateX(-50%) translateY(80px)';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// ─────────────────────────────────────────
// 🔒 SECURITY HELPER
// ─────────────────────────────────────────

function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

// ─────────────────────────────────────────
// 🚀 INIT
// ✅ REMOVED: loadReviews() and reviewForm listener
// These are now handled directly in index.html
// to avoid double submission and double display
// ─────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  updateCartBadge();
  // ✅ NO loadReviews() here — index.html handles it
  // ✅ NO reviewForm listener here — index.html handles it
});