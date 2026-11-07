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

  let gateway = document.querySelector('[data-research-gateway]');
  if (!gateway && document.querySelector('[data-analytics-role="paper_download"]')) {
    gateway = document.createElement('dialog');
    gateway.className = 'research-gateway';
    gateway.dataset.researchGateway = '';
    gateway.setAttribute('aria-labelledby', 'research-gateway-title');
    gateway.innerHTML = `<form method="dialog" class="research-gateway-card" data-gateway-form><button class="research-gateway-close" value="cancel" aria-label="Close download support options">×</button><p class="section-index">Before you download</p><h2 id="research-gateway-title">Support Independent AI Research</h2><p class="research-gateway-intro">The Norynthe Papers are independently researched, developed, and published to advance transparency, accountability, and trust in artificial intelligence. Your contribution helps sustain this work, support continued research, and keep these publications accessible to the public.</p><fieldset class="research-gateway-interest"><legend>What brings you to the Papers? <span>(optional)</span></legend><label><input type="radio" name="research-interest" value="academic"> Academic research</label><label><input type="radio" name="research-interest" value="enterprise"> Enterprise or governance</label><label><input type="radio" name="research-interest" value="investment"> Investment</label><label><input type="radio" name="research-interest" value="general"> General interest</label><label class="research-gateway-email"><span>Email (optional)</span><input type="email" name="research-email" autocomplete="email" placeholder="you@example.com"></label><label class="research-gateway-consent"><input type="checkbox" name="research-consent"> I consent to sharing this interest and email with Norynthe for follow-up. No email is sent unless I choose “Share interest.”</label></fieldset><div class="research-gateway-actions"><button class="button button-primary" value="download" data-gateway-download>Continue to free download</button><a class="button button-secondary" href="https://www.paypal.com/donate/?hosted_button_id=BYKMYWUY634N8" target="_blank" rel="noopener noreferrer" data-analytics-role="gateway_donation_click">Support with a donation</a><a class="button button-secondary" href="https://tally.so/r/ZjezPA" target="_blank" rel="noopener noreferrer" data-analytics-role="gateway_inquiry_click">Discuss an enterprise evaluation</a><button class="research-gateway-share" type="button" data-gateway-share>Share interest with Norynthe</button></div><p class="research-gateway-status" data-gateway-status aria-live="polite"></p></form>`;
    document.body.appendChild(gateway);
  }
  let pendingDownload = null;

  const gatewayEvent = (eventName, params = {}) => {
    if (typeof window.gtag === 'function') window.gtag('event', eventName, { event_category: 'Papers', ...params });
    if (typeof window.clarity === 'function') window.clarity('event', eventName);
  };

  const openGateway = (link) => {
    if (!gateway || typeof gateway.showModal !== 'function') return false;
    pendingDownload = link;
    gateway.showModal();
    gatewayEvent('research_gateway_impression', { material: link.dataset.analyticsMaterial || link.textContent.trim() });
    return true;
  };

  document.querySelectorAll('[data-analytics-role="paper_download"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (link.dataset.gatewayComplete === 'true') return;
      if (openGateway(link)) event.preventDefault();
    });
  });

  if (gateway) {
    const form = gateway.querySelector('[data-gateway-form]');
    const status = gateway.querySelector('[data-gateway-status]');
    const interest = () => form.querySelector('input[name="research-interest"]:checked')?.value || 'unspecified';
    const material = () => pendingDownload?.dataset.analyticsMaterial || pendingDownload?.textContent.trim() || 'Papers download';

    gateway.querySelector('[data-gateway-download]').addEventListener('click', () => {
      gatewayEvent('research_gateway_continue_free', { material: material(), research_interest: interest() });
      if (pendingDownload) {
        pendingDownload.dataset.gatewayComplete = 'true';
        gateway.close();
        pendingDownload.click();
        pendingDownload = null;
      }
    });

    gateway.querySelector('[data-gateway-share]').addEventListener('click', () => {
      const consent = form.querySelector('input[name="research-consent"]').checked;
      const email = form.querySelector('input[name="research-email"]').value.trim();
      if (!consent) { status.textContent = 'Please check consent before sharing your interest.'; return; }
      if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { status.textContent = 'Please enter a valid email address or leave it blank.'; return; }
      gatewayEvent('research_interest_share', { material: material(), research_interest: interest(), email_provided: Boolean(email) });
      const subject = encodeURIComponent('Research interest from The Norynthe Papers');
      const body = encodeURIComponent(`Interest: ${interest()}\nEmail: ${email || '(not provided)'}\n\nI would like to discuss the research I found through The Norynthe Papers.`);
      window.location.href = `mailto:hello@norynthe.com?subject=${subject}&body=${body}`;
    });

    gateway.querySelectorAll('[data-analytics-role^="gateway_"]').forEach((link) => link.addEventListener('click', () => gatewayEvent(link.dataset.analyticsRole, { material: material() })));
  }

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
