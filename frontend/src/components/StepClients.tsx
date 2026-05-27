import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface Props {
  clientsFile: File | null;
  suppliersFile: File | null;
  onClientsSelect: (file: File) => void;
  onSuppliersSelect: (file: File) => void;
  onBack: () => void;
  onSkip: () => void;
  onNext: () => void;
}

function DropBox({
  label,
  file,
  onDrop,
}: {
  label: string;
  file: File | null;
  onDrop: (f: File) => void;
}) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: useCallback((accepted: File[]) => {
      if (accepted.length > 0) onDrop(accepted[0]);
    }, [onDrop]),
    accept: { "application/vnd.ms-excel": [".xls"] },
    maxFiles: 1,
  });

  return (
    <div className="card">
      <p className="text-muted mb-1">{label}</p>
      <div
        {...getRootProps()}
        style={{
          border: `2px dashed ${isDragActive ? "var(--accent)" : "var(--bg-border)"}`,
          borderRadius: 8,
          padding: 16,
          textAlign: "center",
          cursor: "pointer",
        }}
      >
        <input {...getInputProps()} />
        {file ? (
          <p className="text-success">{file.name}</p>
        ) : isDragActive ? (
          <p className="text-muted">Solte aqui...</p>
        ) : (
          <p className="text-muted">Arraste ou clique</p>
        )}
      </div>
    </div>
  );
}

export default function StepClients({
  clientsFile,
  suppliersFile,
  onClientsSelect,
  onSuppliersSelect,
  onBack,
  onSkip,
  onNext,
}: Props) {
  return (
    <div>
      <h2 style={{ fontSize: 18, marginBottom: 16 }}>Clientes e Fornecedores</h2>
      <p className="text-muted" style={{ marginBottom: 12, fontSize: 13 }}>
        Opcional. Se não houver planilhas de clientes/fornecedores, clique em "Pular".
      </p>
      <DropBox label="CLIENTES.XLS (obrigatório se for converter)" file={clientsFile} onDrop={onClientsSelect} />
      <DropBox label="FORNECEDORES.XLS (opcional)" file={suppliersFile} onDrop={onSuppliersSelect} />
      <div className="flex gap-1 mt-2">
        <button className="btn btn-ghost" onClick={onBack}>Voltar</button>
        <button className="btn btn-ghost" onClick={onSkip}>Pular</button>
        <button className="btn btn-primary" disabled={!clientsFile} onClick={onNext}>Avançar</button>
      </div>
    </div>
  );
}
