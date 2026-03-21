import { readFileSync } from 'fs';
import { join } from 'path';

let _unitsCache = null;

export function getAllUnits() {
  if (_unitsCache) return _unitsCache;
  const filePath = join(process.cwd(), 'public', 'units.json');
  const raw = JSON.parse(readFileSync(filePath, 'utf8'));
  // Filter: only units (not characters)
  _unitsCache = raw.filter(u => {
    const tags = u.tags || [];
    if (tags.includes('キャラ')) return false;
    const s = u.normal?.stats;
    return s && (s.hp > 0 || s.attack > 0 || s.defense > 0 || s.en > 0);
  });
  return _unitsCache;
}

export function getUnitById(id) {
  const units = getAllUnits();
  return units.find(u => String(u.id) === String(id)) || null;
}
