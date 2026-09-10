/* ============================================
   Piste AI EVANGELISTS - Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // --- Header scroll effect ---
  const header = document.querySelector('.header');
  window.addEventListener('scroll', () => {
    if (!header) return;
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

  if (hamburger && mobileNav && mobileOverlay) {
    const setMenu = (open) => {
      mobileNav.classList.toggle('open', open);
      mobileOverlay.classList.toggle('open', open);
      hamburger.setAttribute('aria-expanded', String(open));
      hamburger.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    };
    hamburger.addEventListener('click', () => setMenu(!mobileNav.classList.contains('open')));
    mobileOverlay.addEventListener('click', () => setMenu(false));
    mobileNav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && mobileNav.classList.contains('open')) {
        setMenu(false);
        hamburger.focus();
      }
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
      const href = anchor.getAttribute('href');
      if (href === '#') { window.scrollTo({ top: 0, behavior: 'smooth' }); return; }
      const target = document.getElementById(decodeURIComponent(href.slice(1)));
      if (target) {
        const headerHeight = header?.offsetHeight || 0;
        const targetPos = target.getBoundingClientRect().top + window.scrollY - headerHeight;
        window.scrollTo({ top: targetPos, behavior: 'smooth' });
      }
    });
  });

  // Make the existing news disclosure available to keyboard users too.
  document.querySelectorAll('.news-item[onclick]').forEach((item, index) => {
    const detail = item.querySelector('.news-detail');
    if (!detail) return;
    detail.id = detail.id || `news-detail-${index}`;
    item.setAttribute('role', 'button');
    item.setAttribute('tabindex', '0');
    item.setAttribute('aria-controls', detail.id);
    item.setAttribute('aria-expanded', String(detail.classList.contains('open')));
    item.addEventListener('click', () => item.setAttribute('aria-expanded', String(detail.classList.contains('open'))));
    item.addEventListener('keydown', event => {
      if (event.target === item && (event.key === 'Enter' || event.key === ' ')) {
        event.preventDefault(); item.click();
      }
    });
  });

  // --- Contact form ---
  const CONTACT_URL = '/api/contact';
  const form = document.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      if (btn.disabled || !form.reportValidity()) return;
      btn.textContent = '送信中...';
      btn.disabled = true;

      const data = {
        name: form.querySelector('[name="name"]').value,
        company: form.querySelector('[name="company"]').value,
        email: form.querySelector('[name="email"]').value,
        category: form.querySelector('[name="category"]').value,
        message: form.querySelector('[name="message"]').value,
        website: form.querySelector('[name="website"]')?.value || ''
      };

      try {
        const response = await fetch(CONTACT_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!response.ok || (await response.json()).status !== 'ok') throw new Error('Submission not confirmed');
        window.pisteTrack?.('generate_lead', { method: 'contact_form' });
        alert('お問い合わせを受け付けました。担当者より順次ご連絡します。');
        form.reset();
      } catch (err) {
        alert('送信完了を確認できませんでした。重複送信を避けるため、時間をおいて受信メールをご確認いただくか、LINEからお問い合わせください。');
      } finally {
        btn.textContent = '送信する';
        btn.disabled = false;
      }
    });
  }

});
