// Shared TypeScript types that mirror the backend Pydantic schemas.

export type FieldType = "string" | "integer" | "float" | "boolean" | "enum" | "date";

export interface FieldDefinition {
  name: string;
  type: FieldType;
  description: string;
  required: boolean;
  enum_options?: string[] | null;
  min_length?: number | null;
  max_length?: number | null;
  minimum?: number | null;
  maximum?: number | null;
}

export interface FewShotExample {
  input: string;
  output: Record<string, unknown>;
}

export interface TemplateResponse {
  id: number;
  name: string;
  description: string;
  extraction_mode: string;
  instruction: string;
  fields: FieldDefinition[];
  examples: FewShotExample[];
  is_builtin: boolean;
  created_at: string;
  updated_at: string;
}

export interface FileUploadResponse {
  file_id: number;
  filename: string;
  file_type: string;
  headers: string[];
  // The backend coerces every cell to string, but typing this as `unknown`
  // avoids lying if a future parser path returns numbers / booleans.
  preview_rows: Record<string, unknown>[];
  total_rows: number;
  created_at: string;
}

export interface JobResponse {
  id: number;
  file_id: number;
  template_id: number;
  input_column: string;
  max_rows: number;
  status: "pending" | "running" | "completed" | "failed";
  total_count: number;
  processed_count: number;
  success_count: number;
  failed_count: number;
  archived_count: number;
  progress_percent: number;
  created_at: string;
  updated_at: string;
}

export interface ResultResponse {
  id: number;
  job_id: number;
  source_row_index: number;
  input_text: string;
  output: Record<string, unknown>;
  raw_model_output: string;
  validation_status: string;
  // Pydantic emits {loc, msg, ...}; the enum validator emits {loc, msg};
  // tolerate any extra shape with an index signature.
  validation_errors: Array<{ loc?: (string | number)[]; msg?: string; [k: string]: unknown }>;
  retry_count: number;
  status: "success" | "failed" | "archived";
  created_at: string;
  updated_at: string;
}

export interface HealthResponse {
  status: string;
  provider: string;
  model: string;
  version: string;
}
