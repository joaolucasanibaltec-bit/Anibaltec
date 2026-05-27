import { useState, useEffect } from "react";
import { fetchTemplates, type Template } from "../api/client";

interface Props {
  templateName: string;
  onTemplateChange: (name: string) => void;
  onNext: () => void;
}

export default function StepConfig({ templateName, onTemplateChange, onNext }: Props) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTemplates()
      .then(setTemplates)
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h2 style={{ fontSize: 18, marginBottom: 16 }}>Configuração</h2>
      <div className="card">
        <label className="text-muted" style={{ display: "block", marginBottom: 6, fontSize: 13 }}>
          Template de destino
        </label>
        {loading ? (
          <p className="text-muted">Carregando templates...</p>
        ) : (
          <select
            value={templateName}
            onChange={(e) => onTemplateChange(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid var(--bg-border)",
              background: "var(--bg-primary)",
              color: "var(--text-primary)",
              fontSize: 14,
            }}
          >
            {templates.map((t) => (
              <option key={t.name} value={t.name}>
                {t.name} ({(t.size / 1024).toFixed(0)} KB)
              </option>
            ))}
          </select>
        )}
      </div>
      <button className="btn btn-primary" onClick={onNext} style={{ marginTop: 16 }}>
        Avançar
      </button>
    </div>
  );
}
