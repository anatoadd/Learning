// ナビゲーションのスムーズスクロール
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// ヘッダーの固定
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 100) {
        header.classList.add('fixed');
    } else {
        header.classList.remove('fixed');
    }
});

// お問い合わせフォームのバリデーション
const contactForm = document.querySelector('#contact form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.querySelector('#name').value;
        const email = document.querySelector('#email').value;
        const message = document.querySelector('#message').value;
        
        if (!name || !email || !message) {
            alert('必須項目を入力してください。');
            return;
        }
        
        if (!email.match(/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/)) {
            alert('正しいメールアドレスを入力してください。');
            return;
        }
        
        alert('お問い合わせを受け付けました。');
        this.reset();
    });
}

// レスポンシブナビゲーション
const menuButton = document.querySelector('.menu-button');
const nav = document.querySelector('nav');

if (menuButton) {
    menuButton.addEventListener('click', function() {
        nav.classList.toggle('active');
    });
}
