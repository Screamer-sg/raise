export type PortMode = 'access' | 'trunk' | 'qinq' | 'disabled';

export interface PortAdvanced {
  description?: string;
  speed?: string;
  duplex?: string;
  storm_control?: string;
  comment?: string;
}

export interface PortConfig {
  name: string;
  mode: PortMode;
  access_vlan?: number;
  trunk_vlans?: string;
  qinq_outer?: number;
  qinq_inner?: number;
  advanced?: PortAdvanced;
}

export interface ConfigMetadata {
  model_id: string;
  model_name: string;
  firmware?: string;
  author?: string;
}

export interface ConfigRequest {
  metadata: ConfigMetadata;
  ports: PortConfig[];
  profiles?: string[];
}

export interface ValidationMessage {
  level: 'info' | 'warning' | 'error';
  code: string;
  message: string;
  port?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  messages: ValidationMessage[];
}

export interface ConfigPreviewResponse {
  cli: string;
  config_json: Record<string, unknown>;
  config_cfg: string;
  validation: ValidationResult;
}

export interface ModelDefinition {
  id: string;
  name: string;
  description: string;
  ports: { name: string; type: string }[];
}
