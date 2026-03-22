'use client';

import { useEffect, useRef } from 'react';

export default function HomePage() {
  const containerRef = useRef(null);
  const loadedRef = useRef(false);

  useEffect(() => {
    if (loadedRef.current) return;
    loadedRef.current = true;

    // Load the existing SPA by fetching index.html and injecting its body content
    async function loadSPA() {
      try {
        const res = await fetch('/spa.html');
        const html = await res.text();

        // Parse the HTML to extract body content and scripts
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Get the body content
        const container = containerRef.current;
        if (!container) return;

        // Copy body HTML (excluding scripts)
        const bodyContent = doc.body.cloneNode(true);
        const scripts = bodyContent.querySelectorAll('script');
        const scriptContents = [];
        scripts.forEach(s => {
          scriptContents.push({
            src: s.src,
            text: s.textContent,
            type: s.type,
          });
          s.remove();
        });

        // Extract and inject styles from <head>
        const headStyles = doc.querySelectorAll('head style');
        headStyles.forEach(style => {
          const newStyle = document.createElement('style');
          newStyle.textContent = style.textContent;
          document.head.appendChild(newStyle);
        });

        container.innerHTML = bodyContent.innerHTML;

        // Re-inject and execute scripts sequentially
        for (const scriptData of scriptContents) {
          await new Promise((resolve) => {
            const newScript = document.createElement('script');
            if (scriptData.type) newScript.type = scriptData.type;
            if (scriptData.src) {
              newScript.src = scriptData.src;
              newScript.onload = resolve;
              newScript.onerror = resolve;
            } else {
              newScript.textContent = scriptData.text;
            }
            container.appendChild(newScript);
            if (!scriptData.src) resolve();
          });
        }
      } catch (err) {
        console.error('Failed to load SPA:', err);
      }
    }

    loadSPA();
  }, []);

  return <div ref={containerRef} id="spa-root" />;
}
