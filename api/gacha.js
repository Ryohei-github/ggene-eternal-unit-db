import { createClient } from '@supabase/supabase-js';

// Simple in-memory rate limiter
const rateLimit = new Map();
const RATE_LIMIT_WINDOW = 60 * 1000;
const RATE_LIMIT_MAX = 30;

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

const ALLOWED_ORIGINS = [
  'https://gget-db.com',
  'https://www.gget-db.com',
];

function isAllowedOrigin(req) {
  const origin = req.headers['origin'] || '';
  const referer = req.headers['referer'] || '';
  if (ALLOWED_ORIGINS.some(o => origin.startsWith(o) || referer.startsWith(o))) return true;
  if (!origin && !referer) {
    const ua = (req.headers['user-agent'] || '').toLowerCase();
    const botPatterns = ['bot', 'crawl', 'spider', 'scrape', 'curl', 'wget', 'python', 'httpclient', 'axios', 'node-fetch', 'go-http'];
    if (botPatterns.some(p => ua.includes(p))) return false;
    return true;
  }
  return false;
}

// Supabase anon key is intentionally public (designed for client-side use with RLS)
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://juzzgoplgmfbwsyexupg.supabase.co';
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1enpnb3BsZ21mYndzeWV4dXBnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzMTY5NDcsImV4cCI6MjA5MDg5Mjk0N30.rmPVxrLNek8WUMYtSkLbZymCkxAlndVxLwZ1b8_Uo3Q';

function getSupabase() {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) return null;
  return createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
}

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const ip = req.headers['x-forwarded-for'] || req.headers['x-real-ip'] || 'unknown';
  if (!checkRateLimit(ip)) {
    return res.status(429).json({ error: 'Too many requests. Please try again later.' });
  }

  if (!isAllowedOrigin(req)) {
    return res.status(403).json({ error: 'Access denied' });
  }

  const supabase = getSupabase();
  if (!supabase) {
    return res.status(503).json({ error: 'Database not configured' });
  }

  // Security headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=120');
  res.setHeader('Content-Type', 'application/json');

  const origin = req.headers['origin'] || '';
  if (ALLOWED_ORIGINS.some(o => origin.startsWith(o))) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }

  const { action, gacha_id } = req.query;

  try {
    switch (action) {
      // GET /api/gacha?action=list — active gacha list
      case 'list': {
        const { data, error } = await supabase
          .from('gachas')
          .select('*')
          .eq('is_active', true)
          .order('start_date', { ascending: false });
        if (error) throw error;
        return res.status(200).json(data);
      }

      // GET /api/gacha?action=all — all gachas (including inactive)
      case 'all': {
        const { data, error } = await supabase
          .from('gachas')
          .select('*')
          .order('start_date', { ascending: false });
        if (error) throw error;
        return res.status(200).json(data);
      }

      // GET /api/gacha?action=detail&gacha_id=1 — gacha detail with units
      case 'detail': {
        if (!gacha_id) {
          return res.status(400).json({ error: 'gacha_id is required' });
        }
        const gachaId = parseInt(gacha_id, 10);
        if (isNaN(gachaId)) {
          return res.status(400).json({ error: 'Invalid gacha_id' });
        }

        // Fetch gacha info
        const { data: gacha, error: gachaErr } = await supabase
          .from('gachas')
          .select('*')
          .eq('id', gachaId)
          .single();
        if (gachaErr) throw gachaErr;
        if (!gacha) {
          return res.status(404).json({ error: 'Gacha not found' });
        }

        // Fetch gacha units with unit details
        const { data: gachaUnits, error: guErr } = await supabase
          .from('gacha_units')
          .select('is_pickup, unit_id, units(unit_id, name, image, rarity, type, obtain, series, tags, combat_power)')
          .eq('gacha_id', gachaId);
        if (guErr) throw guErr;

        return res.status(200).json({
          ...gacha,
          units: (gachaUnits || []).map(gu => ({
            ...gu.units,
            is_pickup: gu.is_pickup,
          })),
        });
      }

      // GET /api/gacha?action=reroll — reroll tier list
      case 'reroll': {
        const { data, error } = await supabase
          .from('reroll_tiers')
          .select('*, units(unit_id, name, image, rarity, type, series, tags)')
          .order('tier', { ascending: true });
        if (error) throw error;
        return res.status(200).json(data);
      }

      default:
        return res.status(400).json({ error: 'Invalid action. Use: list, all, detail, reroll' });
    }
  } catch (err) {
    console.error('Gacha API error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
