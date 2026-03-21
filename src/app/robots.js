export default function robots() {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/unit-images/'],
      },
    ],
    sitemap: 'https://gget-db.com/sitemap.xml',
  };
}
