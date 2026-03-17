import { verifyToken } from './_lib/auth.js';

const REPO_OWNER = 'Ryohei-github';
const REPO_NAME = 'ggene-eternal-unit-db';
const BRANCH = 'main';

const ALLOWED_FILES = {
  units: 'public/units.json',
  characters: 'public/characters.json',
  supporters: 'public/supporters.json',
};

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();

  // Auth check
  if (!verifyToken(req)) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  if (!GITHUB_TOKEN) {
    return res.status(500).json({ error: 'GITHUB_TOKEN not configured' });
  }

  try {
    const { section, data } = req.body;

    if (!section || !ALLOWED_FILES[section]) {
      return res.status(400).json({ error: 'Invalid section. Use: units, characters, supporters' });
    }
    if (!Array.isArray(data)) {
      return res.status(400).json({ error: 'data must be an array' });
    }

    const filePath = ALLOWED_FILES[section];
    const apiBase = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`;
    const headers = {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: 'application/vnd.github.v3+json',
      'User-Agent': 'GGeneDB-CMS',
    };

    // Step 1: Get current file SHA (required for update)
    const getRes = await fetch(`${apiBase}?ref=${BRANCH}`, { headers });
    if (!getRes.ok) {
      const err = await getRes.text();
      return res.status(500).json({ error: `Failed to get file info: ${getRes.status} ${err}` });
    }
    const fileInfo = await getRes.json();
    const currentSha = fileInfo.sha;

    // Step 2: Encode new content as base64
    const jsonStr = JSON.stringify(data, null, 1);
    const content = Buffer.from(jsonStr, 'utf8').toString('base64');

    // Step 3: Commit via GitHub Contents API
    const now = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });
    const putRes = await fetch(apiBase, {
      method: 'PUT',
      headers,
      body: JSON.stringify({
        message: `update ${section}.json via CMS (${now})`,
        content,
        sha: currentSha,
        branch: BRANCH,
      }),
    });

    if (!putRes.ok) {
      const err = await putRes.text();
      return res.status(500).json({ error: `GitHub commit failed: ${putRes.status} ${err}` });
    }

    const result = await putRes.json();
    return res.status(200).json({
      success: true,
      section,
      commit: result.commit?.sha?.substring(0, 7) || 'unknown',
      message: `${section}.json を更新しました。Vercelが自動デプロイします。`,
    });

  } catch (e) {
    console.error('Save error:', e);
    return res.status(500).json({ error: e.message });
  }
}
