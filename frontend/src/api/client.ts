import axios from "axios";
import type { Template, UploadResult, ValidationResult } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
});

export async function fetchTemplates(): Promise<Template[]> {
  const { data } = await api.get("/templates");
  return data.templates;
}

export async function uploadFile(file: File): Promise<UploadResult> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/upload", form);
  return data;
}

export async function convertProducts(
  file: File,
  templateName: string,
  outputName: string
): Promise<Blob> {
  const form = new FormData();
  form.append("acsn_file", file);
  form.append("template_name", templateName);
  form.append("output_name", outputName);
  const { data } = await api.post("/convert/products", form, {
    responseType: "blob",
  });
  return data;
}

export async function validateClients(
  clientFile: File,
  supplierFile: File | null
): Promise<ValidationResult> {
  const form = new FormData();
  form.append("client_file", clientFile);
  if (supplierFile) {
    form.append("supplier_file", supplierFile);
  }
  const { data } = await api.post("/validate/clients", form);
  return data;
}

export interface ConvertClientsOptions {
  defaultCep?: string;
  defaultCity?: string;
  defaultState?: string;
  excludeMissingCity?: boolean;
}

export async function convertClients(
  clientFile: File,
  supplierFile: File | null,
  templateName: string,
  outputName: string,
  options?: ConvertClientsOptions
): Promise<Blob> {
  const form = new FormData();
  form.append("client_file", clientFile);
  if (supplierFile) {
    form.append("supplier_file", supplierFile);
  }
  form.append("template_name", templateName);
  form.append("output_name", outputName);
  if (options?.defaultCep) form.append("default_cep", options.defaultCep);
  if (options?.defaultCity) form.append("default_city", options.defaultCity);
  if (options?.defaultState) form.append("default_state", options.defaultState);
  if (options?.excludeMissingCity) form.append("exclude_missing_city", "true");
  const { data } = await api.post("/convert/clients", form, {
    responseType: "blob",
  });
  return data;
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
