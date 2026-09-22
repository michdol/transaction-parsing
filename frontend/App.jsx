import { useEffect, useState } from 'react'
import { listImports, getImport, createImport } from './api.js'

function formatAmount(minor) {
  const n = Number(minor)
  return (n / 100).toFixed(2)
}

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(new Error('Could not read the selected file.'))
    reader.readAsText(file)
  })
}

export default function App() {
  const [imports, setImports] = useState([])
  const [listStatus, setListStatus] = useState('loading') // loading | ready | error
  const [listError, setListError] = useState('')

  const [file, setFile] = useState(null)
  const [uploadStatus, setUploadStatus] = useState('idle') // idle | loading | error
  const [uploadError, setUploadError] = useState('')

  const [selectedId, setSelectedId] = useState(null)
  const [detail, setDetail] = useState(null)
  const [detailStatus, setDetailStatus] = useState('empty') // empty | loading | ready | error
  const [detailError, setDetailError] = useState('')

  async function refreshImports() {
    setListStatus('loading')
    setListError('')
    try {
      const data = await listImports()
      setImports(Array.isArray(data) ? data : [])
      setListStatus('ready')
    } catch (err) {
      setListStatus('error')
      setListError(err.message)
    }
  }

  useEffect(() => {
    refreshImports()
  }, [])

  async function openImport(id) {
    setSelectedId(id)
    setDetailStatus('loading')
    setDetailError('')
    try {
      const data = await getImport(id)
      setDetail(data)
      setDetailStatus('ready')
    } catch (err) {
      setDetail(null)
      setDetailStatus('error')
      setDetailError(err.message)
    }
  }

  function handleFileChange(e) {
    const f = e.target.files && e.target.files[0]
    setFile(f || null)
    setUploadStatus('idle')
    setUploadError('')
  }

  async function handleImport() {
    if (!file) {
      setUploadStatus('error')
      setUploadError('Choose a CSV file first.')
      return
    }
    setUploadStatus('loading')
    setUploadError('')
    try {
      const csvText = await readFileAsText(file)
      const created = await createImport(csvText)
      setUploadStatus('idle')
      setFile(null)
      // reset the file input so the same file can be reselected later
      const inputEl = document.getElementById('csv-file-input')
      if (inputEl) inputEl.value = ''
      await refreshImports()
      setSelectedId(created.id)
      setDetail(created)
      setDetailStatus('ready')
    } catch (err) {
      setUploadStatus('error')
      setUploadError(err.message)
      // deliberately do NOT touch selectedId/detail here so a failed
      // import never displays as if it succeeded
    }
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>Transaction Import</h1>

        <section className="panel">
          <h2>New import</h2>
          <input
            id="csv-file-input"
            type="file"
            accept=".csv,text/csv"
            onChange={handleFileChange}
          />
          <button onClick={handleImport} disabled={uploadStatus === 'loading'}>
            {uploadStatus === 'loading' ? 'Importing…' : 'Import CSV'}
          </button>
          {uploadStatus === 'error' && (
            <p className="error" role="alert">{uploadError}</p>
          )}
        </section>

        <section className="panel">
          <h2>Previous imports</h2>
          {listStatus === 'loading' && <p>Loading imports…</p>}
          {listStatus === 'error' && (
            <div>
              <p className="error" role="alert">{listError}</p>
              <button onClick={refreshImports}>Retry</button>
            </div>
          )}
          {listStatus === 'ready' && imports.length === 0 && (
            <p className="muted">No imports yet.</p>
          )}
          {listStatus === 'ready' && imports.length > 0 && (
            <ul className="import-list">
              {imports.map((imp) => (
                <li key={imp.id}>
                  <button
                    className={imp.id === selectedId ? 'selected' : ''}
                    onClick={() => openImport(imp.id)}
                  >
                    <span className="id">{imp.id}</span>
                    <span className="meta">
                      {imp.accepted_count} accepted / {imp.rejected_count} rejected
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </aside>

      <main className="content">
        {detailStatus === 'empty' && (
          <p className="muted">Import a CSV or select a previous import to see results.</p>
        )}

        {detailStatus === 'loading' && <p>Loading import…</p>}

        {detailStatus === 'error' && (
          <p className="error" role="alert">{detailError}</p>
        )}

        {detailStatus === 'ready' && detail && (
          <div>
            <h2>Import {detail.id}</h2>
            <div className="summary">
              <div><span className="label">Accepted</span><span>{detail.accepted_count}</span></div>
              <div><span className="label">Rejected</span><span>{detail.rejected_count}</span></div>
              <div><span className="label">Total</span><span>{formatAmount(detail.total_minor)} {detail.currency}</span></div>
            </div>

            <h3>Accepted ({detail.accepted?.length ?? 0})</h3>
            {(!detail.accepted || detail.accepted.length === 0) ? (
              <p className="muted">No accepted rows.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Transaction ID</th>
                    <th>Date</th>
                    <th>Customer</th>
                    <th>Amount</th>
                    <th>Currency</th>
                  </tr>
                </thead>
                <tbody>
                  {detail.accepted.map((row, i) => (
                    <tr key={row.transaction_id ?? i}>
                      <td>{row.transaction_id}</td>
                      <td>{row.date}</td>
                      <td>{row.customer}</td>
                      <td>{formatAmount(row.amount_minor)}</td>
                      <td>{row.currency}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            <h3>Rejected ({detail.rejected?.length ?? 0})</h3>
            {(!detail.rejected || detail.rejected.length === 0) ? (
              <p className="muted">No rejected rows.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {detail.rejected.map((row, i) => (
                    <tr key={i}>
                      <td>{row.row}</td>
                      <td>{row.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
