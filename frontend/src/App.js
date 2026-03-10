import React, { useState, useEffect } from 'react';
import { ShieldCheck, ShieldAlert, RefreshCw, Server, History } from 'lucide-react';
import './App.css';

function App() {
  const [dispositivos, setDispositivos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [abaAtiva, setAbaAtiva] = useState('monitor');
  const [historico, setHistorico] = useState([]);

  const fetchDispositivos = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/dispositivos');
      const data = await response.json();
      setDispositivos(Array.isArray(data) ? data : []);
    } catch (error) { console.error(error); }
  };

  const fetchHistorico = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/historico');
      const data = await response.json();
      setHistorico(Array.isArray(data) ? data : []);
    } catch (error) { console.error(error); }
  };

  const atualizarTudo = async () => {
    setLoading(true);
    await Promise.all([fetchDispositivos(), fetchHistorico()]);
    setLoading(false);
  };

  useEffect(() => {
    atualizarTudo();
    const intervalo = setInterval(atualizarTudo, 60000);
    return () => clearInterval(intervalo);
  }, []);

  const cadastrarConhecido = async (mac) => {
    const nome = prompt("Nome do dispositivo:");
    if (!nome) return;
    await fetch('http://127.0.0.1:8000/api/cadastrar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mac: mac.toLowerCase(), nome, tipo: 'Conhecido' })
    });
    atualizarTudo();
  };

  return (
    <div className="container-fluid bg-light min-vh-100 p-4">
      <header className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
        <h1 className="h3 fw-bold text-dark mb-0">Network Sentinel <small className="text-muted h6">v1.2</small></h1>
        <button className="btn btn-primary d-flex align-items-center gap-2" onClick={atualizarTudo} disabled={loading}>
          <RefreshCw size={18} className={loading ? 'spin' : ''} /> {loading ? "Escaneando..." : "Atualizar Rede"}
        </button>
      </header>

      <div className="row g-3 mb-4">
        <div className="col-md-4"><div className="card p-3 shadow-sm text-center"><h6>Online</h6><h3>{dispositivos.length}</h3></div></div>
        <div className="col-md-4"><div className="card p-3 shadow-sm text-center text-success"><h6>Conhecidos</h6><h3>{dispositivos.filter(d => d.status === 'Conhecido').length}</h3></div></div>
        <div className="col-md-4"><div className="card p-3 shadow-sm text-center text-danger"><h6>Intrusos</h6><h3>{dispositivos.filter(d => d.status === 'INTRUSO').length}</h3></div></div>
      </div>

      <div className="nav nav-pills mb-3">
        <button className={`nav-link ${abaAtiva === 'monitor' ? 'active' : ''}`} onClick={() => setAbaAtiva('monitor')}>Monitor</button>
        <button className={`nav-link ${abaAtiva === 'historico' ? 'active' : ''}`} onClick={() => setAbaAtiva('historico')}>Histórico</button>
      </div>

      <div className="card shadow-sm">
        <table className="table mb-0 align-middle">
          <thead className="table-light">
            <tr>
              {abaAtiva === 'monitor' ? (
                <><th>Status</th><th>IP</th><th>MAC</th><th>Fabricante</th><th className="text-end">Ações</th></>
              ) : (
                <><th>Visto em</th><th>IP</th><th>MAC</th><th>Fabricante</th></>
              )}
            </tr>
          </thead>
          <tbody>
            {abaAtiva === 'monitor' ? dispositivos.map((d, i) => (
              <tr key={i} className={d.status === 'INTRUSO' ? 'table-danger-light' : ''}>
                <td><span className={`badge ${d.status === 'INTRUSO' ? 'bg-danger' : 'bg-success'}`}>{d.status}</span></td>
                <td>{d.ip}</td><td><code>{d.mac}</code></td><td>{d.fabricante || d.nome_personalizado}</td>
                <td className="text-end">{d.status === 'INTRUSO' && <button className="btn btn-sm btn-outline-primary" onClick={() => cadastrarConhecido(d.mac)}>Confiar</button>}</td>
              </tr>
            )) : historico.map((h, i) => (
              <tr key={i}><td>{h.data}</td><td>{h.ip}</td><td><code>{h.mac}</code></td><td>{h.fabricante}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default App;