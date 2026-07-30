(() => {
  const copyButtons = document.querySelectorAll('[data-copy-target]');
  if (!copyButtons.length) return;

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
})();
