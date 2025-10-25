import { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { CheckIcon, ChevronUpDownIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { PortConfig, PortMode } from '../types/config';

const modes: { value: PortMode; label: string; color: string }[] = [
  { value: 'access', label: 'Access', color: 'bg-emerald-500' },
  { value: 'trunk', label: 'Trunk', color: 'bg-sky-500' },
  { value: 'qinq', label: 'QinQ', color: 'bg-purple-500' },
  { value: 'disabled', label: 'Disabled', color: 'bg-slate-500' },
];

interface PortRowProps {
  port: PortConfig;
  index: number;
  onChange: (index: number, patch: Partial<PortConfig>) => void;
  onAdvanced: (index: number) => void;
}

export function PortRow({ port, index, onChange, onAdvanced }: PortRowProps) {
  return (
    <div className="grid grid-cols-12 gap-3 items-center bg-slate-800/50 rounded-lg p-3">
      <span className="col-span-2 font-mono text-sm">{port.name}</span>
      <div className="col-span-2">
        <Listbox
          value={port.mode}
          onChange={(value: PortMode) => onChange(index, { mode: value })}
        >
          <div className="relative">
            <Listbox.Button className="relative w-full cursor-pointer rounded-md bg-slate-900 py-2 pl-3 pr-10 text-left text-sm shadow focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-500">
              <span className="flex items-center gap-2">
                <span className={clsx('h-2 w-2 rounded-full', modes.find((m) => m.value === port.mode)?.color)} />
                {modes.find((m) => m.value === port.mode)?.label ?? 'Select'}
              </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon className="h-4 w-4 text-slate-400" aria-hidden="true" />
            </span>
            </Listbox.Button>
            <Transition
              as={Fragment}
              leave="transition ease-in duration-100"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <Listbox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-slate-900 py-1 text-sm shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                {modes.map((mode) => (
                <Listbox.Option
                  key={mode.value}
                  className={({ active }) =>
                    clsx('relative cursor-pointer select-none py-2 pl-10 pr-4', {
                      'bg-slate-700 text-white': active,
                      'text-slate-100': !active,
                    })
                  }
                  value={mode.value}
                >
                  {({ selected }) => (
                    <>
                      <span className={clsx('absolute left-2 top-3 h-2 w-2 rounded-full', mode.color)} />
                      <span className={clsx('block truncate', { 'font-medium': selected, 'font-normal': !selected })}>
                        {mode.label}
                      </span>
                      {selected ? (
                        <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-emerald-400">
                          <CheckIcon className="h-4 w-4" aria-hidden="true" />
                        </span>
                      ) : null}
                    </>
                  )}
                </Listbox.Option>
              ))}
              </Listbox.Options>
            </Transition>
          </div>
        </Listbox>
      </div>

      <div className="col-span-4 flex gap-2">
        {port.mode === 'access' && (
          <input
            type="number"
            value={port.access_vlan ?? ''}
            onChange={(event) => {
              const value = event.target.value;
              onChange(index, { access_vlan: value ? Number(value) : undefined });
            }}
            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
            placeholder="VLAN ID"
          />
        )}
        {port.mode === 'trunk' && (
          <input
            type="text"
            value={port.trunk_vlans ?? ''}
            onChange={(event) => onChange(index, { trunk_vlans: event.target.value || undefined })}
            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
            placeholder="e.g. 10,20,100-120"
          />
        )}
        {port.mode === 'qinq' && (
          <>
            <input
              type="number"
              value={port.qinq_outer ?? ''}
              onChange={(event) => {
                const value = event.target.value;
                onChange(index, { qinq_outer: value ? Number(value) : undefined });
              }}
              className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
              placeholder="Outer VLAN"
            />
            <input
              type="number"
              value={port.qinq_inner ?? ''}
              onChange={(event) => {
                const value = event.target.value;
                onChange(index, { qinq_inner: value ? Number(value) : undefined });
              }}
              className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
              placeholder="Inner VLAN"
            />
          </>
        )}
      </div>

      <button
        type="button"
        onClick={() => onAdvanced(index)}
        className="col-span-2 inline-flex items-center justify-center gap-2 rounded-md border border-slate-600 bg-slate-900 px-3 py-2 text-sm text-slate-200 hover:border-orange-500 hover:text-orange-400"
      >
        <AdjustmentsHorizontalIcon className="h-4 w-4" />
        Advanced
      </button>
    </div>
  );
}
