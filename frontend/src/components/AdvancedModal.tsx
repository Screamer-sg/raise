import { Dialog, Transition } from '@headlessui/react';
import { Fragment, useEffect, useState } from 'react';
import { PortAdvanced } from '../types/config';

interface AdvancedModalProps {
  open: boolean;
  portName: string;
  initial: PortAdvanced;
  onClose: () => void;
  onSave: (settings: PortAdvanced) => void;
}

export function AdvancedModal({ open, portName, initial, onClose, onSave }: AdvancedModalProps) {
  const [state, setState] = useState<PortAdvanced>(initial);

  useEffect(() => {
    setState(initial);
  }, [initial, open]);

  const apply = () => {
    onSave(state);
    onClose();
  };

  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-slate-900 p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-slate-100">
                  Advanced settings for {portName}
                </Dialog.Title>
                <div className="mt-4 space-y-3">
                  <input
                    type="text"
                    placeholder="Description"
                    value={state.description ?? ''}
                    onChange={(event) => setState((prev) => ({ ...prev, description: event.target.value || undefined }))}
                    className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <input
                      type="text"
                      placeholder="Speed"
                      value={state.speed ?? ''}
                      onChange={(event) => setState((prev) => ({ ...prev, speed: event.target.value || undefined }))}
                      className="rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
                    />
                    <input
                      type="text"
                      placeholder="Duplex"
                      value={state.duplex ?? ''}
                      onChange={(event) => setState((prev) => ({ ...prev, duplex: event.target.value || undefined }))}
                      className="rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
                    />
                  </div>
                  <input
                    type="text"
                    placeholder="Storm control"
                    value={state.storm_control ?? ''}
                    onChange={(event) => setState((prev) => ({ ...prev, storm_control: event.target.value || undefined }))}
                    className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
                  />
                  <textarea
                    placeholder="Comment"
                    value={state.comment ?? ''}
                    onChange={(event) => setState((prev) => ({ ...prev, comment: event.target.value || undefined }))}
                    className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-orange-500 focus:outline-none"
                    rows={3}
                  />
                </div>

                <div className="mt-6 flex justify-end gap-3">
                  <button
                    type="button"
                    className="rounded-md border border-transparent bg-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-600"
                    onClick={onClose}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="rounded-md border border-transparent bg-orange-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-orange-400"
                    onClick={apply}
                  >
                    Save changes
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
