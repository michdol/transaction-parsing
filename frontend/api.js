const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options) {
  let res
  try {
    res = await fetch(`${API_BASE}${path}`, options)
  } catch (err) {
    throw new Error('Could not reach the server. Is the backend running?')
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (body && body.detail) {
        detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
      }
    } catch {
      // response had no JSON body, keep default message
    }
    throw new Error(detail)
  }

  if (res.status === 204) return null
  return res.json()
}

export function getHealth() {
  return request('/api/health')
}

export function listImports() {
  return request('/api/imports')
}

export function getImport(id) {
  return request(`/api/imports/${encodeURIComponent(id)}`)
}

export function createImport(csvText) {
  return request('/api/imports', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ csv: csvText }),
  })
}
