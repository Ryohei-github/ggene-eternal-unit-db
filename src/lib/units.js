import { readFileSync } from 'fs';
import { join } from 'path';

let _unitsCache = null;
let _charasCache = null;
let _rawCache = null;

function getRawData() {
  if (_rawCache) return _rawCache;
  const filePath = join(process.cwd(), 'public', 'units.json');
  _rawCache = JSON.parse(readFileSync(filePath, 'utf8'));
  return _rawCache;
}

export function getAllUnits() {
  if (_unitsCache) return _unitsCache;
  const raw = getRawData();
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

export function getAllCharas() {
  if (_charasCache) return _charasCache;
  const raw = getRawData();
  _charasCache = raw.filter(u => {
    const tags = u.tags || [];
    return tags.includes('キャラ');
  });
  return _charasCache;
}

export function getCharaById(id) {
  const charas = getAllCharas();
  return charas.find(u => String(u.id) === String(id)) || null;
}
