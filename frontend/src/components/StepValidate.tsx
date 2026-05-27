import { useState, useEffect } from "react";
import { validateClients, type ConvertClientsOptions } from "../api/client";
import type { ValidationResult } from "../types";

interface Props {
  clientsFile: File;
  suppliersFile: File | null;
  onFixesChange: (fixes: ConvertClientsOptions) => void;
  onBack: () => void;
  onNext: () => void;
}

export default function StepValidate({
  clientsFile, suppliersFile,
  onFixesChange, onBack, onNext,
}: Props) {
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [validating, setValidating] = useState(true);
  const [error, setError] = useState("");
  const [defaultCep, setDefaultCep] = useState("");
  const [defaultCity, setDefaultCity] = useState("");
  const [defaultState, setDefaultState] = useState("");
  const [exclude, setExclude] = useState(false);

  useEffect(() => {
    setValidating(true);
    setError("");
    validateClients(clientsFile, suppliersFile)
      .then(setResult)
      .catch(() => setError("Erro ao validar arquivos"))
      .finally(() => setValidating(false));
  }, [clientsFile, suppliersFile]);

  const hasIssues =
    result &&
    (result.sem_cep.count > 0 || result.sem_cidade.count > 0 || result.sem_estado.count > 0);

  const handleContinue = () => {
    onFixesChange({
      defaultCep: defaultCep || undefined,
      defaultCity: defaultCity || undefined,
      defaultState: defaultState || undefined,
      excludeMissingCity: exclude,
    });
    onNext();
  };

  return (
    <div>
      <h2 style={{ fontSize: 18, marginBottom: 16 }}>Validação de Clientes e Fornecedores</h2>

      <div className="card">
        <p className="text-muted mb-1">
          Total de registros: <strong>{validating ? "..." : result?.total}</strong>
        </p>
      </div>

      {validating ? (
        <div className="card">
          <p className="text-muted">Analisando dados...</p>
        </div>
      ) : error ? (
        <div className="card">
          <p className="text-error">{error}</p>
        </div>
      ) : !hasIssues ? (
        <div className="card">
          <p className="text-success">Nenhum problema encontrado!</p>
        </div>
      ) : (
        <>
          <div className="card">
            <div className="flex justify-between items-center">
              <span>CEP vazio</span>
              <span style={{
                color: "var(--warning)",
                fontWeight: 700,
              }}>
                {result?.sem_cep.count}
              </span>
            </div>
            {result && result.sem_cep.count > 0 && (
              <>
                <input
                  type="text"
                  placeholder="CEP padrão para aplicar (vazio = manter em branco)"
                  value={defaultCep}
                  onChange={(e) => setDefaultCep(e.target.value)}
                  style={{
                    width: "100%",
                    marginTop: 8,
                    padding: "10px 12px",
                    borderRadius: 6,
                    border: "1px solid var(--bg-border)",
                    background: "var(--bg-primary)",
                    color: "var(--text-primary)",
                    fontSize: 14,
                  }}
                />
                {result.sem_cep.amostras.length > 0 && (
                  <p className="text-muted mt-1" style={{ fontSize: 12 }}>
                    Amostra: {result.sem_cep.amostras.map((a) => `${a.codigo} (${a.nome})`).join(", ")}
                  </p>
                )}
              </>
            )}
          </div>

          <div className="card">
            <div className="flex justify-between items-center">
              <span>Cidade vazia</span>
              <span style={{
                color: "var(--warning)",
                fontWeight: 700,
              }}>
                {result?.sem_cidade.count}
              </span>
            </div>
            {result && result.sem_cidade.count > 0 && (
              <>
                <input
                  type="text"
                  placeholder="Cidade padrão (ex: NATAL)"
                  value={defaultCity}
                  onChange={(e) => setDefaultCity(e.target.value)}
                  style={{
                    width: "100%",
                    marginTop: 8,
                    padding: "10px 12px",
                    borderRadius: 6,
                    border: "1px solid var(--bg-border)",
                    background: "var(--bg-primary)",
                    color: "var(--text-primary)",
                    fontSize: 14,
                  }}
                />
                {result.sem_cidade.amostras.length > 0 && (
                  <p className="text-muted mt-1" style={{ fontSize: 12 }}>
                    Amostra: {result.sem_cidade.amostras.map((a) => `${a.codigo} (${a.nome})`).join(", ")}
                  </p>
                )}
              </>
            )}
          </div>

          <div className="card">
            <div className="flex justify-between items-center">
              <span>Estado vazio</span>
              <span style={{
                color: "var(--warning)",
                fontWeight: 700,
              }}>
                {result?.sem_estado.count}
              </span>
            </div>
            {result && result.sem_estado.count > 0 && (
              <input
                type="text"
                placeholder="UF padrão (ex: RN)"
                value={defaultState}
                onChange={(e) => setDefaultState(e.target.value)}
                style={{
                  width: "100%",
                  marginTop: 8,
                  padding: "10px 12px",
                  borderRadius: 6,
                  border: "1px solid var(--bg-border)",
                  background: "var(--bg-primary)",
                  color: "var(--text-primary)",
                  fontSize: 14,
                }}
              />
            )}
          </div>

          {(result && (result.sem_cidade.count > 0 || result.sem_estado.count > 0)) && (
            <div className="card">
              <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={exclude}
                  onChange={(e) => setExclude(e.target.checked)}
                  style={{ accentColor: "var(--accent)", width: 16, height: 16 }}
                />
                <span>Excluir registros sem cidade/estado</span>
              </label>
              <p className="text-muted mt-1" style={{ fontSize: 12 }}>
                Se marcado, registros sem cidade e estado serão removidos da planilha final
              </p>
            </div>
          )}
        </>
      )}

      <div className="flex gap-1 mt-2">
        <button className="btn btn-ghost" onClick={onBack}>Voltar</button>
        <button className="btn btn-primary" disabled={validating} onClick={handleContinue}>
          Continuar
        </button>
      </div>
    </div>
  );
}
