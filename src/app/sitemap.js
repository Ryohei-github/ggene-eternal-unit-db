import { getAllUnits } from '@/lib/units';

export default function sitemap() {
  const units = getAllUnits();
  const baseUrl = 'https://gget-db.com';

  const unitPages = units.map((unit) => ({
    url: `${baseUrl}/units/${unit.id}`,
    lastModified: new Date(),
    changeFrequency: 'weekly',
    priority: 0.7,
  }));

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    ...unitPages,
  ];
}
