import { useState } from 'react';
import { CloudArrowDownIcon, EyeIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { PortConfig, PortAdvanced } from './types/config';
import { useConfigurator } from './hooks/useConfigurator';
import { PortRow } from './components/PortRow';
import { AdvancedModal } from './components/AdvancedModal';

function ValidationBanner({ messages }: { messages: ReturnType<typeof useConfigurator>['validationMessages'] }) {
  if (!messages.length) {
    return (
      <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
        ✅ All checks passed. Configuration is ready.
      </div>
    );
  }
  return (
    <div className="space-y-2">
      {messages.map((message, index) => (
        <div
          key={`${message.code}-${index}`}
          className={`rounded-lg border px-4 py-3 text-sm ${
            message.level === 'error'
              ? 'border-rose-500/40 bg-rose-500/10 text-rose-200'
              : 'border-amber-500/40 bg-amber-500/10 text-amber-200'
          }`}
        >
          <strong className="uppercase">{message.level}</strong> — {message.message}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const configurator = useConfigurator();
  const [activeAdvancedIndex, setActiveAdvancedIndex] = useState<number | null>(null);

  const openAdvanced = (index: number) => setActiveAdvancedIndex(index);
  const closeAdvanced = () => setActiveAdvancedIndex(null);
  const saveAdvanced = (settings: PortAdvanced) => {
    if (activeAdvancedIndex === null) return;
    configurator.updatePort(activeAdvancedIndex, { advanced: settings });
  };

  const activePort: PortConfig | undefined =
    activeAdvancedIndex !== null ? configurator.ports[activeAdvancedIndex] : undefined;

  return (
    <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-6 py-10">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Raisecom Configurator v6.2</h1>
          <p className="text-sm text-slate-400">
            Design, validate and export Raisecom switch configurations entirely offline.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-orange-500 focus:outline-none"
            value={configurator.selectedModel?.id ?? ''}
            onChange={(event) => {
              const model = configurator.models.find((item) => item.id === event.target.value);
              if (model) configurator.selectModel(model);
            }}
          >
            {configurator.models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
        </div>
      </header>

      <main className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">Port matrix</h2>
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 hover:border-orange-500 hover:text-orange-300"
              onClick={configurator.generatePreview}
            >
              <ArrowPathIcon className={configurator.loading ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} />
              {configurator.loading ? 'Generating…' : 'Apply changes'}
            </button>
          </div>
          <div className="space-y-3">
            {configurator.error && (
              <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 px-4 py-2 text-sm text-rose-200">
                {configurator.error}
              </div>
            )}
            {configurator.ports.map((port, index) => (
              <PortRow
                key={port.name}
                port={port}
                index={index}
                onChange={configurator.updatePort}
                onAdvanced={openAdvanced}
              />
            ))}
          </div>
        </section>

        <aside className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-lg font-semibold text-slate-100">Validation</h2>
          <ValidationBanner messages={configurator.validationMessages} />

          <div className="space-y-3">
            <button
              type="button"
              onClick={configurator.exportConfig}
              disabled={!configurator.preview}
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm font-medium text-slate-100 transition hover:border-orange-500 hover:text-orange-300 disabled:cursor-not-allowed disabled:border-slate-800 disabled:text-slate-500"
            >
              <CloudArrowDownIcon className="h-4 w-4" />
              Export CLI script
            </button>
            <button
              type="button"
              onClick={configurator.generatePreview}
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm font-medium text-slate-100 transition hover:border-orange-500 hover:text-orange-300"
            >
              <EyeIcon className="h-4 w-4" />
              Preview commands
            </button>
          </div>

          {configurator.preview && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Real-time preview</h3>
              <pre className="max-h-64 overflow-auto rounded-lg bg-slate-950/80 p-4 text-xs text-slate-200">
                {configurator.preview.cli}
              </pre>
            </div>
          )}
        </aside>
      </main>

      <AdvancedModal
        open={activeAdvancedIndex !== null}
        portName={activePort?.name ?? ''}
        initial={activePort?.advanced ?? {}}
        onClose={closeAdvanced}
        onSave={saveAdvanced}
      />
    </div>
  );
}
