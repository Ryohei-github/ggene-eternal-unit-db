import { readFileSync } from 'fs';
import { join } from 'path';

// Simple in-memory rate limiter
const rateLimit = new Map();
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX = 30; // max requests per window per IP

function checkRateLimit(ip) {
  const now = Date.now();
  const record = rateLimit.get(ip);
  if (!record || now - record.windowStart > RATE_LIMIT_WINDOW) {
    rateLimit.set(ip, { windowStart: now, count: 1 });
    return true;
  }
  record.count++;
  if (record.count > RATE_LIMIT_MAX) return false;
  return true;
}

// Allowed origins
const ALLOWED_ORIGINS = [
  'https://gget-db.com',
  'https://www.gget-db.com',
];

function isAllowedOrigin(req) {
  const origin = req.headers['origin'] || '';
  const referer = req.headers['referer'] || '';

  // Allow if origin or referer matches
  if (ALLOWED_ORIGINS.some(o => origin.startsWith(o) || referer.startsWith(o))) return true;

  // Allow server-side rendering (no origin/referer = direct page load)
  // But block if it looks like a scraper (has origin but wrong one)
  if (!origin && !referer) {
    // Check for common bot user agents
    const ua = (req.headers['user-agent'] || '').toLowerCase();
    const botPatterns = ['bot', 'crawl', 'spider', 'scrape', 'curl', 'wget', 'python', 'httpclient', 'axios', 'node-fetch', 'go-http'];
    if (botPatterns.some(p => ua.includes(p))) return false;
    return true; // Allow browser direct access for initial page load
  }

  return false;
}

export default function handler(req, res) {
  // Only allow GET
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Rate limit check
  const ip = req.headers['x-forwarded-for'] || req.headers['x-real-ip'] || 'unknown';
  if (!checkRateLimit(ip)) {
    return res.status(429).json({ error: 'Too many requests. Please try again later.' });
  }

  // Origin/Referer check
  if (!isAllowedOrigin(req)) {
    return res.status(403).json({ error: 'Access denied' });
  }

  // Determine which data file to serve
  const { type } = req.query;
  const allowedTypes = {
    'units': 'units.json',
    'supporters': 'supporters.json',
    'translations': 'translations_en.json',
    'translations_en': 'translations_en.json',
    'translations_zh_tw': 'translations_zh-tw.json',
    'characters': 'characters.json',
  };

  const filename = allowedTypes[type];
  if (!filename) {
    return res.status(400).json({ error: 'Invalid type parameter' });
  }

  try {
    const filePath = join(process.cwd(), 'public', filename);
    const data = readFileSync(filePath, 'utf8');

    // Set security headers
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Cache-Control', 'public, s-maxage=300, stale-while-revalidate=600');
    res.setHeader('Content-Type', 'application/json');

    // Set CORS only for allowed origins
    const origin = req.headers['origin'] || '';
    if (ALLOWED_ORIGINS.some(o => origin.startsWith(o))) {
      res.setHeader('Access-Control-Allow-Origin', origin);
    }

    return res.status(200).send(data);
  } catch (err) {
    return res.status(500).json({ error: 'Internal server error' });
  }
}
