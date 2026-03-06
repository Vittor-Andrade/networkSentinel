import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [dispositivos, setDispositivos] = useState([]);
  const [loading, setLoading] = useState(false);

  // 1. Defina a função que busca os dados
  const fetchDispositivos = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/dispositivos');
      const data = await response.json();
      setDispositivos(data);
    } catch (error) {
      console.error("Erro ao buscar dispositivos:", error);
      alert("Certifique-se que o backend Python está rodando!");
    } finally {
      setLoading(false);
    }
  };

  // 2. Chame ela quando a página carregar
  useEffect(() => {
    fetchDispositivos();
  }, []);

  // 3. A sua função de cadastrar deve chamar a fetchDispositivos no final
  const cadastrarConhecido = async (mac) => {
    const nome = prompt("Qual o nome deste dispositivo?");
    if (!nome) return;

    try {
      await fetch('http://127.0.0.1:8000/api/cadastrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mac, nome, tipo: 'Conhecido' })
      });

      // AQUI estava o erro: agora a função existe e pode ser chamada!
      fetchDispositivos();
    } catch (error) {
      alert("Erro ao salvar.");
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Network Sentinel</h1>
        <button className="btn-update" onClick={fetchDispositivos}>
          {loading ? "Escaneando..." : "Atualizar Rede"}
        </button>
      </header>

      <main>
        <table>
          <thead>
            <tr>
              <th>Status</th>
              <th>IP</th>
              <th>MAC</th>
              <th>Identificação</th>
            </tr>
          </thead>
          <tbody>
            {Array.isArray(dispositivos) && dispositivos.length > 0 ? (
              dispositivos.map((d, index) => (
                <tr key={index} className={d.status === 'INTRUSO' ? 'row-intruso' : 'row-conhecido'}>
                  <td>
                    <span className={`badge ${d.status ? d.status.toLowerCase() : ''}`}>
                      {d.status}
                    </span>
                  </td>
                  <td>{d.ip}</td>
                  <td><code>{d.mac}</code></td>
                  <td>{d.nome_personalizado}</td>
                  <td>
                    {d.status === 'INTRUSO' && (
                      <button className="btn-save" onClick={() => cadastrarConhecido(d.mac)}>
                        Confiar
                      </button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>
                  {loading ? "Buscando dispositivos..." : "Nenhum dado disponível ou erro no servidor."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </main>
    </div>
  );
}

export default App;