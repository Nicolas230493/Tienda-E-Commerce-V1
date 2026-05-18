// Helper para obtener el CSRF Token de Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ═══════════════════════════════════════════
// SIDE CART (LÓGICA PREMIUM)
// ═══════════════════════════════════════════

function toggleSideCart(open) {
    const cart = document.getElementById('sideCart');
    const overlay = document.getElementById('sideCartOverlay');
    if (open) {
        fetch('/carrito/obtener/')
        .then(response => response.json())
        .then(data => {
            renderSideCart(data);
            cart.classList.add('open');
            overlay.classList.add('open');
        });
    } else {
        cart.classList.remove('open');
        overlay.classList.remove('open');
    }
}

function addToCart(productId) {
    const csrftoken = getCookie('csrftoken');
    
    fetch('/carrito/agregar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'product_id': productId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartUI(data.cart_count);
            toggleSideCart(true); // Abre el carrito lateral automáticamente
            showToast(`✨ ${data.product_name} añadido`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('❌ Error al agregar');
    });
}

function renderSideCart(data) {
    const body = document.getElementById('sideCartBody');
    const footer = document.getElementById('sideCartFooter');

    if (data.items.length === 0) {
        body.innerHTML = `
            <div style="text-align:center; padding-top:50px; color:var(--muted);">
                <div style="font-size:60px; margin-bottom:20px;">🛒</div>
                <p>Tu carrito está vacío</p>
                <button class="btn-outline" style="margin-top:20px;" onclick="toggleSideCart(false)">Empezar a comprar</button>
            </div>`;
        footer.innerHTML = '';
        return;
    }

    let itemsHtml = data.items.map(item => `
        <div class="cart-item" style="padding:15px 0; border-bottom:var(--border); display:flex; gap:15px;">
            <div style="width:70px; height:70px; background:var(--light); border-radius:4px; display:flex; align-items:center; justify-content:center;">
                ${item.imagen ? `<img src="${item.imagen}" style="max-width:90%; max-height:90%; object-fit:contain;">` : `<span style="font-size:30px;">${item.emoji}</span>`}
            </div>
            <div style="flex:1;">
                <div style="font-size:10px; text-transform:uppercase; color:var(--accent); letter-spacing:1px;">${item.marca}</div>
                <div style="font-family:'Cormorant Garamond',serif; font-size:16px; font-weight:600; margin:2px 0;">${item.nombre}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span style="font-size:13px; color:var(--muted);">${item.cantidad} x $${item.precio}</span>
                    <span style="font-weight:600;">$${item.total}</span>
                </div>
            </div>
        </div>
    `).join('');

    body.innerHTML = itemsHtml;

    footer.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:14px;">
            <span>Subtotal</span><span>$${data.subtotal}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:20px; font-size:18px; font-weight:600;">
            <span>Total</span><span>$${data.total}</span>
        </div>
        <button class="btn-primary" style="width:100%; padding:18px;" onclick="openCheckout()">Finalizar Compra</button>
    `;
}

function updateCartUI(count) {
    const badge = document.getElementById('cartCount');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// ═══════════════════════════════════════════
// CHECKOUT
// ═══════════════════════════════════════════

function openCheckout() {
    toggleSideCart(false);
    document.getElementById('checkoutModal').classList.add('open');
}

function closeCheckout() {
    document.getElementById('checkoutModal').classList.remove('open');
}

function procesarPago() {
    const csrftoken = getCookie('csrftoken');
    const data = {
        nombre_completo: document.getElementById('checkoutNombre').value,
        email: document.getElementById('checkoutEmail').value,
        direccion: document.getElementById('checkoutDireccion').value,
        ciudad: document.getElementById('checkoutCiudad').value,
        zip_code: document.getElementById('checkoutZip').value,
    };

    if (!data.nombre_completo || !data.email || !data.direccion) {
        showToast('❌ Por favor completa los campos obligatorios');
        return;
    }

    fetch('/carrito/procesar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeCheckout();
            updateCartUI(0);
            showToast('✅ Pedido registrado. Redirigiendo a pago...');
            setTimeout(() => {
                window.location.href = data.payment_url;
            }, 1500);
        } else {
            showToast('❌ ' + (data.message || 'Error al procesar el pedido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('❌ Error de conexión');
    });
}

// ═══════════════════════════════════════════
// NEWSLETTER
// ═══════════════════════════════════════════

function subscribeEmail() {
    const name = document.getElementById('nlName').value.trim();
    const email = document.getElementById('nlEmail').value.trim();
    const csrftoken = getCookie('csrftoken');

    if (!email || !email.includes('@')) {
        showToast('Por favor ingresá un email válido');
        return;
    }

    fetch('/newsletter/suscribir/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'nombre': name, 'email': email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('nlName').value = '';
            document.getElementById('nlEmail').value = '';
            showToast(`🎉 ¡Gracias ${name || ''}! Revisa tu email`);
        } else {
            showToast('❌ ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('❌ Error en la suscripción');
    });
}

// ═══════════════════════════════════════════
// UI & GENERAL
// ═══════════════════════════════════════════

let toastTimer;
function showToast(msg) {
    const t = document.getElementById('toast');
    if (!t) return;
    clearTimeout(toastTimer);
    t.textContent = msg;
    t.classList.add('show');
    toastTimer = setTimeout(() => t.classList.remove('show'), 3200);
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('open');
    }
}

window.addEventListener('scroll', () => {
    const btn = document.getElementById('scrollTopBtn');
    if (btn) {
        btn.classList.toggle('visible', window.scrollY > 400);
    }
});
