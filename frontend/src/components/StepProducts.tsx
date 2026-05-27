import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface Props {
  file: File | null;
  onFileSelect: (file: File) => void;
  onBack: () => void;
  onSkip: () => void;
  onNext: () => void;
}

export default function StepProducts({ file, onFileSelect, onBack, onSkip, onNext }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted.length > 0) onFileSelect(accepted[0]);
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/vnd.ms-excel": [".xls"] },
    maxFiles: 1,
  });

  return (
    <div>
      <h2 style={{ fontSize: 18, marginBottom: 16 }}>Mercadorias (Produtos)</h2>
      <p className="text-muted" style={{ marginBottom: 12, fontSize: 13 }}>
        Opcional. Se não houver planilha de produtos, clique em "Pular".
      </p>
      <div className="card">
        <p className="text-muted mb-1">Selecione o arquivo PRODUTOS.XLS do ACSN</p>
        <div
          {...getRootProps()}
          style={{
            border: `2px dashed ${isDragActive ? "var(--accent)" : "var(--bg-border)"}`,
            borderRadius: 8,
            padding: 24,
            textAlign: "center",
            cursor: "pointer",
            background: isDragActive ? "var(--bg-surface)" : "transparent",
          }}
        >
          <input {...getInputProps()} />
          {file ? (
            <p className="text-success">{file.name}</p>
          ) : isDragActive ? (
            <p className="text-muted">Solte o arquivo aqui...</p>
          ) : (
            <p className="text-muted">Arraste ou clique para selecionar PRODUTOS.XLS</p>
          )}
        </div>
        {file && (
          <p className="text-muted mt-1">{(file.size / 1024).toFixed(0)} KB</p>
        )}
      </div>
      <div className="flex gap-1 mt-2">
        <button className="btn btn-ghost" onClick={onBack}>Voltar</button>
        <button className="btn btn-ghost" onClick={onSkip}>Pular</button>
        <button className="btn btn-primary" disabled={!file} onClick={onNext}>Avançar</button>
      </div>
    </div>
  );
}
