import { convertProducts, convertClients, downloadBlob, type ConvertClientsOptions } from "../api/client";
import type { LogEntry } from "../types";

interface Props {
  templateName: string;
  productsFile: File | null;
  clientsFile: File | null;
  suppliersFile: File | null;
  fixes: ConvertClientsOptions;
  logs: LogEntry[];
  converting: boolean;
  progress: number;
  onLog: (text: string, type: LogEntry["type"]) => void;
  onConvertingChange: (v: boolean) => void;
  onProgressChange: (v: number) => void;
  onBack: () => void;
}

export default function StepGenerate({
  templateName,
  productsFile,
  clientsFile,
  suppliersFile,
  fixes,
  logs,
  converting,
  progress,
  onLog,
  onConvertingChange,
  onProgressChange,
  onBack,
}: Props) {
  const handleConvertProducts = async () => {
    if (!productsFile) return;
    onConvertingChange(true);
    onProgressChange(10);
    try {
      onLog("Iniciando conversão de produtos...", "info");
      const blob = await convertProducts(productsFile, templateName, "MERCADORIAS_SGACLOUD.xlsx");
      downloadBlob(blob, `MERCADORIAS_SGACLOUD.xlsx`);
      onLog("Produtos convertidos com sucesso!", "success");
      onProgressChange(50);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro desconhecido";
      onLog(`Erro produtos: ${msg}`, "error");
    } finally {
      onConvertingChange(false);
    }
  };

  const handleConvertClients = async () => {
    if (!clientsFile) return;
    onConvertingChange(true);
    onProgressChange(60);
    try {
      onLog("Iniciando conversão de clientes...", "info");
      if (fixes.defaultCep) onLog(`CEP padrão: ${fixes.defaultCep}`, "info");
      if (fixes.defaultCity) onLog(`Cidade padrão: ${fixes.defaultCity}`, "info");
      if (fixes.defaultState) onLog(`UF padrão: ${fixes.defaultState}`, "info");
      if (fixes.excludeMissingCity) onLog("Excluindo registros sem cidade/estado", "info");
      const blob = await convertClients(
        clientsFile,
        suppliersFile,
        "TEMPLATE CLIENTES.xlsx",
        "CLIENTE_FORNECEDOR_SGACLOUD.xlsx",
        fixes
      );
      downloadBlob(blob, `CLIENTE_FORNECEDOR_SGACLOUD.xlsx`);
      onLog("Clientes/Fornecedores convertidos com sucesso!", "success");
      onProgressChange(100);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro desconhecido";
      onLog(`Erro clientes: ${msg}`, "error");
    } finally {
      onConvertingChange(false);
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: 18, marginBottom: 16 }}>Gerar Arquivos</h2>

      <div className="card">
        <button
          className="btn btn-primary"
          disabled={converting || !productsFile}
          onClick={handleConvertProducts}
          style={{ marginRight: 8 }}
        >
          Converter Produtos
        </button>
        <button
          className="btn btn-primary"
          disabled={converting || !clientsFile}
          onClick={handleConvertClients}
        >
          Converter Clientes/Fornecedores
        </button>
      </div>

      {converting && (
        <div className="card">
          <div
            style={{
              height: 8,
              background: "var(--bg-border)",
              borderRadius: 4,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${progress}%`,
                height: "100%",
                background: "var(--accent)",
                transition: "width 0.3s ease",
              }}
            />
          </div>
          <p className="text-muted mt-1" style={{ fontSize: 12 }}>
            {progress}%
          </p>
        </div>
      )}

      <div
        className="card"
        style={{
          maxHeight: 160,
          overflowY: "auto",
          fontFamily: "monospace",
          fontSize: 12,
        }}
      >
        {logs.length === 0 ? (
          <p className="text-muted">Nenhum log disponível</p>
        ) : (
          logs.map((log, i) => (
            <p
              key={i}
              style={{
                color:
                  log.type === "error"
                    ? "var(--error)"
                    : log.type === "success"
                    ? "var(--success)"
                    : "var(--text-secondary)",
                margin: "2px 0",
              }}
            >
              {log.text}
            </p>
          ))
        )}
      </div>

      <button className="btn btn-ghost mt-2" onClick={onBack}>
        Voltar
      </button>
    </div>
  );
}
