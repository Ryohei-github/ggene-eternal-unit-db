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
          // 忍者AdMaxのスクリプトはiframe方式で後から注入するためスキップ
          if (s.src && s.src.includes('adm.shinobi.jp')) {
            s.remove();
            return;
          }
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
        // 忍者AdMax: document.write()を使うためiframeで注入
        const adSlots = [
          { id: 'adSlotTop', src: 'https://adm.shinobi.jp/s/f969299a5a7ac2147238c6e4c8abd0da', w: '320', h: '50' },
          { id: 'adSlotBottom', src: 'https://adm.shinobi.jp/s/6b37984cfa9c490a4d625b9fcbbf94f4', w: '320', h: '50' },
        ];
        function injectAds() {
          adSlots.forEach(ad => {
            const el = container.querySelector('#' + ad.id);
            if (!el || el.dataset.adLoaded) return;
            el.dataset.adLoaded = '1';
            const iframe = document.createElement('iframe');
            iframe.style.cssText = 'border:none;overflow:hidden;display:block;margin:0 auto;';
            iframe.width = ad.w;
            iframe.height = ad.h;
            iframe.scrolling = 'no';
            el.appendChild(iframe);
            // document.write()で直接書き込み：同一オリジン＋パース時にdocument.write()が実行される
            const doc = iframe.contentDocument;
            doc.open();
            doc.write('<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="margin:0;padding:0;overflow:hidden"><script src="' + ad.src + '"><\/script></body></html>');
            doc.close();
          });
        }
        injectAds();
        setTimeout(injectAds, 500);

      } catch (err) {
        console.error('Failed to load SPA:', err);
      }
    }

    loadSPA();
  }, []);

  return <div ref={containerRef} id="spa-root" />;
}
