(() => {
  document.querySelectorAll('[data-current-year]').forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });

  const CLARITY_PROJECT_ID = 'y8j5n0zmsd';

  if (!window.clarity) {
    window.clarity = function () {
      (window.clarity.q = window.clarity.q || []).push(arguments);
    };

    const clarityScript = document.createElement('script');
    clarityScript.async = true;
    clarityScript.src = `https://www.clarity.ms/tag/${CLARITY_PROJECT_ID}`;
    clarityScript.dataset.clarityProject = CLARITY_PROJECT_ID;
    document.head.appendChild(clarityScript);
  }

  const copyButtons = document.querySelectorAll('[data-copy-target]');

  const writeText = async (text, source) => {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }

    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(source);
    selection.removeAllRanges();
    selection.addRange(range);
    const copied = document.execCommand('copy');
    selection.removeAllRanges();
    if (!copied) throw new Error('Copy command was unavailable.');
  };

  copyButtons.forEach((copyButton) => {
    const status = document.getElementById(copyButton.getAttribute('aria-describedby') || '');
    const originalLabel = copyButton.textContent;

    copyButton.addEventListener('click', async () => {
      const source = document.getElementById(copyButton.dataset.copyTarget);
      if (!source) return;

      try {
        await writeText(source.innerText.replace(/\s+/g, ' ').trim(), source);
        copyButton.textContent = 'Copied';
        if (status) status.textContent = 'Citation copied to clipboard.';
      } catch (error) {
        copyButton.textContent = 'Select citation';
        if (status) status.textContent = 'Copy was unavailable. Select the citation text manually.';
      }

      window.setTimeout(() => {
        copyButton.textContent = originalLabel;
        if (status) status.textContent = '';
      }, 2400);
    });
  });

  document.querySelectorAll('[data-analytics-role="support_click"]').forEach((supportLink) => {
    supportLink.addEventListener('click', () => {
      const material = supportLink.dataset.analyticsMaterial || 'The Norynthe Papers';

      if (typeof window.gtag === 'function') {
        window.gtag('event', 'support_click', {
          event_category: 'Papers',
          link_text: supportLink.textContent.trim(),
          material,
          destination: supportLink.href,
          outbound: true
        });
      }

      if (typeof window.clarity === 'function') {
        window.clarity('event', 'support_click');
      }

      const pulse = window.NorynthePulse = window.NorynthePulse || { queue: [] };
      const payload = { material, requestType: material, sourceArea: 'Papers support' };
      if (pulse.ready && typeof pulse.track === 'function') {
        pulse.track('support_click', payload);
      } else {
        pulse.queue = Array.isArray(pulse.queue) ? pulse.queue : [];
        pulse.queue.push({ eventType: 'support_click', payload });
      }
    });
  });

  const donateContainers = Array.from(document.querySelectorAll('.paypal-donate-button'));

  const recordSupportEvent = (eventName, material) => {
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, {
        event_category: 'Papers',
        material,
        payment_provider: 'PayPal'
      });
    }

    if (typeof window.clarity === 'function') {
      window.clarity('event', eventName);
    }

    const pulsePayload = {
      material,
      requestType: material,
      sourceArea: 'Papers support'
    };
    const pulse = window.NorynthePulse = window.NorynthePulse || { queue: [] };
    if (pulse.ready && typeof pulse.track === 'function') {
      pulse.track(eventName, pulsePayload);
    } else if (eventName === 'support_click') {
      pulse.queue = Array.isArray(pulse.queue) ? pulse.queue : [];
      pulse.queue.push({ eventType: eventName, payload: pulsePayload });
    }
  };

  const renderDonateButtons = () => {
    if (!window.PayPal || !window.PayPal.Donation) return;

    donateContainers.forEach((container, index) => {
      const material = container.dataset.analyticsMaterial || 'The Norynthe Papers';
      const fallbackMarkup = container.innerHTML;
      const renderTarget = `paypal-donate-button-${index + 1}`;

      container.id = renderTarget;
      container.innerHTML = '';

      try {
        window.PayPal.Donation.Button({
          env: 'production',
          hosted_button_id: 'BYKMYWUY634N8',
          image: {
            src: '/assets/norynthe-support-button.png?v=20260902c',
            title: 'Support independent research through PayPal',
            alt: 'Support independent research. The Norynthe Papers.'
          },
          onComplete: () => {
            const status = container.parentElement.querySelector('.support-status');
            if (status) status.innerHTML = '<strong>Thank you for supporting independent research.</strong><br>You can continue reading the Papers here.';
            recordSupportEvent('support_complete', material);
          }
        }).render(`#${renderTarget}`);

        container.addEventListener('click', () => recordSupportEvent('support_click', material), { once: true });
      } catch (error) {
        container.innerHTML = fallbackMarkup;
      }
    });
  };

  if (donateContainers.length) {
    const donateScript = document.createElement('script');
    donateScript.src = 'https://www.paypalobjects.com/donate/sdk/donate-sdk.js';
    donateScript.charset = 'UTF-8';
    donateScript.onload = renderDonateButtons;
    document.head.appendChild(donateScript);
  }
})();
