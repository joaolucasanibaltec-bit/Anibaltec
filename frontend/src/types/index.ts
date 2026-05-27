export interface Template {
  name: string;
  size: number;
}

export interface UploadResult {
  filename: string;
  original_name: string;
  size: number;
}

export interface LogEntry {
  text: string;
  type: "info" | "success" | "error";
}

export type StepId = "config" | "products" | "clients" | "validate" | "generate";

export interface AppState {
  currentStep: number;
  templateName: string;
  productsFile: File | null;
  clientsFile: File | null;
  suppliersFile: File | null;
  productOutput: string;
  clientOutput: string;
  logs: LogEntry[];
  converting: boolean;
  progress: number;
}

export interface ValidationIssue {
  codigo: string;
  nome: string;
  tipo: string;
}

export interface ValidationIssues {
  count: number;
  amostras: ValidationIssue[];
}

export interface ValidationResult {
  total: number;
  sem_cep: ValidationIssues;
  sem_cidade: ValidationIssues;
  sem_estado: ValidationIssues;
}
