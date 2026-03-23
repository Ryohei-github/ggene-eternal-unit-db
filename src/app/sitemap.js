import { getAllUnits, getAllCharas } from '@/lib/units';

export default function sitemap() {
  const units = getAllUnits();
  const charas = getAllCharas();
  const baseUrl = 'https://gget-db.com';

  const unitPages = units.map((unit) => ({
    url: `${baseUrl}/units/${unit.id}`,
    lastModified: new Date(),
    changeFrequency: 'weekly',
    priority: 0.7,
  }));

  const charaPages = charas.map((chara) => ({
    url: `${baseUrl}/charas/${chara.id}`,
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
    {
      url: `${baseUrl}/about`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    {
      url: `${baseUrl}/privacy`,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    ...unitPages,
    ...charaPages,
  ];
}
