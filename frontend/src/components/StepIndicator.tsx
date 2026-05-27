interface Props {
  currentStep: number;
  totalSteps: number;
  labels: string[];
}

export default function StepIndicator({ currentStep, totalSteps, labels }: Props) {
  return (
    <div className="flex items-center justify-between" style={{ marginBottom: 24 }}>
      {Array.from({ length: totalSteps }, (_, i) => (
        <div key={i} className="flex items-center" style={{ flex: 1 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 700,
              fontSize: 14,
              background:
                i < currentStep ? "var(--success)" :
                i === currentStep ? "var(--accent)" :
                "var(--bg-border)",
              color: "#fff",
            }}
          >
            {i < currentStep ? "✓" : i + 1}
          </div>
          <span
            style={{
              marginLeft: 8,
              fontSize: 13,
              color: i === currentStep ? "var(--text-primary)" : "var(--text-muted)",
            }}
          >
            {labels[i]}
          </span>
          {i < totalSteps - 1 && (
            <div
              style={{
                flex: 1,
                height: 2,
                margin: "0 12px",
                background: i < currentStep ? "var(--success)" : "var(--bg-border)",
              }}
            />
          )}
        </div>
      ))}
    </div>
  );
}
