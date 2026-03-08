import React, { useState, useEffect } from 'react';
import { ShieldCheck, ShieldAlert, RefreshCw, Server, History } from 'lucide-react';
import './App.css';

function App() {
  const [dispositivos, setDispositivos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [abaAtiva, setAbaAtiva] = useState('monitor');
  const [historico, setHistorico] = useState([]);

  const fetchDispositivos = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/dispositivos');
      const data = await response.json();
      setDispositivos(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Erro:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistorico = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/historico');
      const data = await response.json();
      setHistorico(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Erro ao buscar histórico: ", error);
    }
  };

  useEffect(() => {
    //Faz a primeira busca ao carregar a página
    fetchDispositivos();

    // Configurando o intervalo de atualização automática (60 segundos)
    const intervalo = setInterval(() => {
      console.log("Auto-scan: Atualizando lista de dispositivos...");
      fetchDispositivos();
    }, 60000); 

    //Limpando o intervalo se o usuário fechar a página
    return() => clearInterval(intervalo);
  }, []);

  const cadastrarConhecido = async (mac) => {
    const nome = prompt("Qual o nome deste dispositivo?");
    if (!nome) return;

    try {
      const response = await fetch('http://127.0.0.1:8000/api/cadastrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mac: mac.toLowerCase(), nome: nome, tipo: 'Conhecido' })
      });

      const result = await response.json()
      
      if (result.status === "sucesso") {
        alert("Dispositivo confiado!");
        fetchDispositivos();
      } else {
        alert("Erro do servidor: " + result.mensagem);
      }
    } catch (error) {
      alert("Erro na conexão com o servidor.")
    }
  };

  const total = dispositivos.length;
  const conhecidos = dispositivos.filter(d => d.status === 'Conhecido').length;
  const intrusos = dispositivos.filter(d => d.status === 'INTRUSO').length;

  return (
    <div className="container-fluid bg-light min-vh-100 p-4">
      <header className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
        <div>
          <h1 className="h3 fw-bold text-dark mb-0">Network Sentinel <small className="text-muted h6">v1.2</small></h1>
          <p className="text-muted mb-0">Monitoramento de Segurança de Rede</p>
        </div>
        <button 
          className={`btn ${loading ? 'btn-secondary' : 'btn-primary'} d-flex align-items-center gap-2 shadow-sm`} 
          onClick={fetchDispositivos} 
          disabled={loading}
        >
          <RefreshCw size={18} className={loading ? 'spin' : ''} />
          {loading ? "Escaneando..." : "Atualizar Rede"}
        </button>
      </header>

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="card border-0 shadow-sm p-3">
            <div className="d-flex align-items-center">
              <div className="bg-primary bg-opacity-10 p-3 rounded-3 text-primary me-3"><Server size={24} /></div>
              <div><h6 className="text-muted mb-0 small">Dispositivos Online</h6><h3 className="fw-bold mb-0">{total}</h3></div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card border-0 shadow-sm p-3 text-success">
            <div className="d-flex align-items-center">
              <div className="bg-success bg-opacity-10 p-3 rounded-3 me-3"><ShieldCheck size={24} /></div>
              <div><h6 className="text-muted mb-0 small">Conhecidos</h6><h3 className="fw-bold mb-0">{conhecidos}</h3></div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card border-0 shadow-sm p-3 text-danger">
            <div className="d-flex align-items-center">
              <div className="bg-danger bg-opacity-10 p-3 rounded-3 me-3"><ShieldAlert size={24} /></div>
              <div><h6 className="text-muted mb-0 small">Intrusos Detectados</h6><h3 className="fw-bold mb-0">{intrusos}</h3></div>
            </div>
          </div>
        </div>
      </div>

      <ul className="nav nav-pills mb-3 bg-white p-2 rounded shadow-sm d-inline-flex">
        <li className="nav-item">
          <button className={`nav-link ${abaAtiva === 'monitor' ? 'active' : ''}`} onClick={() => setAbaAtiva('monitor')}>
            <Server size={16} className="me-2" /> Monitor em Tempo Real
          </button>
        </li>
        <li className="nav-item">
          <button className={`nav-link ${abaAtiva === 'historico' ? 'active' : ''}`} onClick={() => setAbaAtiva('historico')}>
            <History size={16} className="me-2" /> Histórico de Acessos
          </button>
        </li>
      </ul>

      <div className="card border-0 shadow-sm">
        <div className="card-body p-0">
          {abaAtiva === 'monitor' ? (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="bg-light text-muted small text-uppercase">
                  <tr>
                    <th className="px-4 py-3">Status</th>
                    <th>IP</th>
                    <th>MAC</th>
                    <th>Identificação</th>
                    <th className="text-end px-4">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {dispositivos.map((d, index) => (
                    <tr key={index}>
                      <td className="px-4">
                        <span className={`badge d-inline-flex align-items-center gap-1 rounded-pill px-3 py-2 ${
                          d.status === 'INTRUSO' ? 'bg-danger-subtle text-danger border border-danger-subtle' : 'bg-success-subtle text-success border border-success-subtle'
                        }`}>
                          {d.status === 'INTRUSO' ? <ShieldAlert size={14} /> : <ShieldCheck size={14} />}
                          {d.status}
                        </span>
                      </td>
                      <td className="fw-bold text-dark">{d.ip}</td>
                      <td><code className="text-muted small">{d.mac}</code></td>
                      <td className="text-muted">{d.nome_personalizado}</td>
                      <td className="text-end px-4">
                        {d.status === 'INTRUSO' && (
                          <button className="btn btn-sm btn-primary shadow-sm" onClick={() => cadastrarConhecido(d.mac)}>
                            Confiar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="bg-light text-muted small text-uppercase">
                  <tr>
                    <th className="px-4 py-3">Última Vez Visto</th>
                    <th>Endereço IP</th>
                    <th>Endereço MAC</th>
                  </tr>
                </thead>
                <tbody>
                  {historico.length > 0 ? (
                    historico.map((h, index) => (
                      <tr key={index}>
                        <td className="px-4 text-muted small">{h.data}</td>
                        <td className="fw-medium">{h.ip}</td>
                        <td><code className="text-muted small">{h.mac}</code></td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="3" className="text-center py-5 text-muted">Nenhum dado de histórico encontrado.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;