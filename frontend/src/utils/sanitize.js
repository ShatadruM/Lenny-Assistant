import DOMPurify from 'dompurify';

/**
 * Sanitizes HTML content before passing it to the preview container.
 * Permits safe layout elements, scripts-free styling, and blocks dangerous attributes.
 */
export function sanitizeHtml(rawHtml) {
  return DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: [
      'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
      'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 
      'button', 'a', 'section', 'article', 'header', 'footer', 'main',
      'b', 'i', 'strong', 'em', 'code', 'pre', 'style'
    ],
    ALLOWED_ATTR: ['class', 'id', 'style', 'href', 'target', 'rel'],
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover']
  });
}