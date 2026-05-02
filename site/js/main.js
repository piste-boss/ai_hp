/* ============================================
   Piste AI EVANGELISTS - Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // --- Header scroll effect ---
  const header = document.querySelector('.header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });

  // --- Mobile nav ---
  const hamburger = document.querySelector('.hamburger');
  const mobileNav = document.querySelector('.mobile-nav');
  const mobileOverlay = document.querySelector('.mobile-overlay');

  if (hamburger) {
    hamburger.addEventListener('click', () => {
      mobileNav.classList.toggle('open');
      mobileOverlay.classList.toggle('open');
    });

    mobileOverlay.addEventListener('click', () => {
      mobileNav.classList.remove('open');
      mobileOverlay.classList.remove('open');
    });

    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileNav.classList.remove('open');
        mobileOverlay.classList.remove('open');
      });
    });
  }

  // --- Scroll animation (Intersection Observer) ---
  const animatedElements = document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0,
    rootMargin: '0px 0px 200px 0px'
  });

  animatedElements.forEach(el => observer.observe(el));

  // Fallback: any element still hidden after load is force-shown so that
  // content (especially large news/blog cards) is never invisible.
  window.addEventListener('load', () => {
    setTimeout(() => {
      document.querySelectorAll(
        '.fade-in:not(.visible), .fade-in-left:not(.visible), .fade-in-right:not(.visible)'
      ).forEach(el => el.classList.add('visible'));
    }, 800);
  });

  // --- Smooth scroll for anchor links ---
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        const headerHeight = header.offsetHeight;
        const targetPos = target.getBoundingClientRect().top + window.scrollY - headerHeight;
        window.scrollTo({ top: targetPos, behavior: 'smooth' });
      }
    });
  });

  // --- Contact form ---
  const GAS_URL = 'https://script.google.com/macros/s/AKfycby4Tn3NHhyIVd_3gQzGT6bfF2EP9Q6bZ2IMLET5BE_ttVZCLBlC8yz5JpXOS_JAE6pi/exec';
  const form = document.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      btn.textContent = '送信中...';
      btn.disabled = true;

      const data = {
        name: form.querySelector('[name="name"]').value,
        company: form.querySelector('[name="company"]').value,
        email: form.querySelector('[name="email"]').value,
        category: form.querySelector('[name="category"]').value,
        message: form.querySelector('[name="message"]').value
      };

      try {
        await fetch(GAS_URL, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'text/plain' },
          body: JSON.stringify(data)
        });
        alert('お問い合わせありがとうございます。確認メールをお送りしましたのでご確認ください。');
        form.reset();
      } catch (err) {
        alert('送信に失敗しました。お手数ですがLINEからお問い合わせください。');
      } finally {
        btn.textContent = '送信する';
        btn.disabled = false;
      }
    });
  }

});
