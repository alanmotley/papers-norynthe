(() => {
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
    });
  });
})();
