import { useState } from "react";
import StepIndicator from "./components/StepIndicator";
import StepProducts from "./components/StepProducts";
import StepClients from "./components/StepClients";
import StepValidate from "./components/StepValidate";
import StepGenerate from "./components/StepGenerate";
import type { LogEntry } from "./types";
import type { ConvertClientsOptions } from "./api/client";

const LABELS = ["Mercadorias", "Clientes", "Validação", "Gerar"];

export default function App() {
  const [step, setStep] = useState(0);
  const [productsFile, setProductsFile] = useState<File | null>(null);
  const [clientsFile, setClientsFile] = useState<File | null>(null);
  const [suppliersFile, setSuppliersFile] = useState<File | null>(null);
  const [fixes, setFixes] = useState<ConvertClientsOptions>({});
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [converting, setConverting] = useState(false);
  const [progress, setProgress] = useState(0);

  const addLog = (text: string, type: LogEntry["type"]) => {
    setLogs((prev) => [...prev, { text, type }]);
  };

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <StepProducts
            file={productsFile}
            onFileSelect={setProductsFile}
            onBack={() => {}}
            onSkip={() => setStep(1)}
            onNext={() => setStep(1)}
          />
        );
      case 1:
        return (
          <StepClients
            clientsFile={clientsFile}
            suppliersFile={suppliersFile}
            onClientsSelect={setClientsFile}
            onSuppliersSelect={setSuppliersFile}
            onBack={() => setStep(0)}
            onSkip={() => setStep(3)}
            onNext={() => setStep(2)}
          />
        );
      case 2:
        return clientsFile ? (
          <StepValidate
            clientsFile={clientsFile}
            suppliersFile={suppliersFile}
            onFixesChange={setFixes}
            onBack={() => setStep(1)}
            onNext={() => setStep(3)}
          />
        ) : null;
      case 3:
        return (
          <StepGenerate
            templateName="TEMPLATE MERCADORIAS.xlsx"
            productsFile={productsFile}
            clientsFile={clientsFile}
            suppliersFile={suppliersFile}
            fixes={fixes}
            logs={logs}
            converting={converting}
            progress={progress}
            onLog={addLog}
            onConvertingChange={setConverting}
            onProgressChange={setProgress}
            onBack={() => clientsFile ? setStep(2) : setStep(1)}
          />
        );
    }
  };

  const current = step === 2 && !clientsFile ? 3 : step;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg-primary)",
        color: "var(--text-primary)",
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      <div
        style={{
          background: "var(--bg-surface)",
          padding: "16px 24px",
          borderBottom: "1px solid var(--bg-border)",
        }}
      >
        <h1 style={{ fontSize: 22, margin: 0 }}>ANIBALTEC</h1>
        <p style={{ fontSize: 11, color: "var(--accent)", margin: "2px 0 0 0" }}>
          Conversor ACSN → SGAcloud
        </p>
      </div>

      <div style={{ maxWidth: 720, margin: "24px auto", padding: "0 16px" }}>
        <StepIndicator currentStep={current} totalSteps={LABELS.length} labels={LABELS} />
        {renderStep()}
      </div>
    </div>
  );
}
