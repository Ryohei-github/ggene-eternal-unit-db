import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SUPABASE_URL = 'https://getqmceqsvbfghxiqhtd.supabase.co';
const ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdldHFtY2Vxc3ZiZmdoeGlxaHRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMxMzc0OTIsImV4cCI6MjA4ODcxMzQ5Mn0.MPL4a35yOuwCyonQ73Xg9pRqKrSbtXX35q-wn264j4g';
const BATCH_SIZE = 50;

async function main() {
  const unitsPath = join(__dirname, 'public', 'units.json');
  console.log(`Reading ${unitsPath}...`);
  const raw = readFileSync(unitsPath, 'utf-8');
  const units = JSON.parse(raw);
  console.log(`Loaded ${units.length} units`);

  let totalImported = 0;
  const totalBatches = Math.ceil(units.length / BATCH_SIZE);

  for (let i = 0; i < units.length; i += BATCH_SIZE) {
    const batch = units.slice(i, i + BATCH_SIZE);
    const batchNum = Math.floor(i / BATCH_SIZE) + 1;
    
    console.log(`Importing batch ${batchNum}/${totalBatches} (${batch.length} units)...`);
    
    const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/import_units_from_json`, {
      method: 'POST',
      headers: {
        'apikey': ANON_KEY,
        'Authorization': `Bearer ${ANON_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
      },
      body: JSON.stringify({ data: batch })
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error(`Batch ${batchNum} FAILED (HTTP ${res.status}): ${errText}`);
      process.exit(1);
    }

    const count = await res.json();
    totalImported += count;
    console.log(`  ✓ Batch ${batchNum} done — ${count} units imported (total: ${totalImported})`);
  }

  console.log(`\n=== Import complete: ${totalImported} units imported ===`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
