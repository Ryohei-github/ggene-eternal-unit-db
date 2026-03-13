import { withAuth, supabaseFetch } from './_lib/auth.js';

async function handler(req, res) {
  const { method } = req;
  const { id } = req.query;

  try {
    // GET - list or single
    if (method === 'GET') {
      const path = id
        ? `ggene_units?id=eq.${id}`
        : `ggene_units?order=id.asc&limit=${req.query.limit || 50}&offset=${req.query.offset || 0}`;
      const resp = await supabaseFetch(path);
      const data = await resp.json();
      return res.status(200).json(id ? data[0] || null : data);
    }

    // POST - create
    if (method === 'POST') {
      const resp = await supabaseFetch('ggene_units', {
        method: 'POST',
        body: JSON.stringify(req.body),
      });
      if (!resp.ok) {
        const err = await resp.text();
        return res.status(resp.status).json({ error: err });
      }
      const data = await resp.json();
      return res.status(201).json(data[0]);
    }

    // PUT - update
    if (method === 'PUT') {
      if (!id) return res.status(400).json({ error: 'id required' });
      const body = { ...req.body, updated_at: new Date().toISOString() };
      const resp = await supabaseFetch(`ggene_units?id=eq.${id}`, {
        method: 'PATCH',
        body: JSON.stringify(body),
      });
      if (!resp.ok) {
        const err = await resp.text();
        return res.status(resp.status).json({ error: err });
      }
      const data = await resp.json();
      return res.status(200).json(data[0]);
    }

    // DELETE
    if (method === 'DELETE') {
      if (!id) return res.status(400).json({ error: 'id required' });
      await supabaseFetch(`ggene_units?id=eq.${id}`, { method: 'DELETE' });
      return res.status(200).json({ deleted: true });
    }

    return res.status(405).json({ error: 'Method not allowed' });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}

export default withAuth(handler);
