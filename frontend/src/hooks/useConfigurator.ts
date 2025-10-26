import { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import {
  ConfigMetadata,
  ConfigPreviewResponse,
  ConfigRequest,
  ModelDefinition,
  PortConfig,
  PortMode,
  ValidationMessage,
} from '../types/config';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
});

export function useConfigurator() {
  const [models, setModels] = useState<ModelDefinition[]>([]);
  const [selectedModel, setSelectedModel] = useState<ModelDefinition | null>(null);
  const [ports, setPorts] = useState<PortConfig[]>([]);
  const [preview, setPreview] = useState<ConfigPreviewResponse | null>(null);
  const [validationMessages, setValidationMessages] = useState<ValidationMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectModel = useCallback((model: ModelDefinition) => {
    setSelectedModel(model);
    setPorts(
      model.ports.map((port) => ({
        name: port.name,
        mode: 'disabled' satisfies PortMode,
        advanced: {},
      })),
    );
  }, []);

  useEffect(() => {
    api.get<ModelDefinition[]>('/models').then((response) => {
      setModels(response.data);
      if (response.data.length) {
        selectModel(response.data[0]);
      }
    });
  }, [selectModel]);

  const metadata: ConfigMetadata | null = useMemo(() => {
    if (!selectedModel) return null;
    return {
      model_id: selectedModel.id,
      model_name: selectedModel.name,
    };
  }, [selectedModel]);

  const updatePort = (index: number, patch: Partial<PortConfig>) => {
    setPorts((prev) => prev.map((port, idx) => (idx === index ? { ...port, ...patch } : port)));
  };

  const generatePreview = async () => {
    if (!metadata) return;
    setLoading(true);
    setError(null);
    try {
      const request: ConfigRequest = { metadata, ports };
      const response = await api.post<ConfigPreviewResponse>('/config/preview', request);
      setPreview(response.data);
      setValidationMessages(response.data.validation.messages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const exportConfig = () => {
    if (!preview) return;
    const blob = new Blob([preview.cli], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${metadata?.model_id ?? 'config'}.txt`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return {
    models,
    selectedModel,
    ports,
    preview,
    metadata,
    validationMessages,
    loading,
    error,
    selectModel,
    updatePort,
    generatePreview,
    exportConfig,
  };
}
