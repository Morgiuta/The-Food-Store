import { useId, type PropsWithChildren } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  title: string;
  kicker?: string;
  onClose: () => void;
  size?: 'md' | 'lg';
}

export function Modal({
  children,
  kicker,
  onClose,
  size = 'md',
  title,
}: PropsWithChildren<ModalProps>) {
  const titleId = useId();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal/50 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby={titleId}>
      <div 
        className={`bg-white rounded-xl shadow-2xl overflow-hidden w-full max-h-[90vh] flex flex-col ${
          size === 'lg' ? 'max-w-4xl' : 'max-w-2xl'
        }`}
      >
        <div className="flex items-start justify-between p-6 border-b border-gray-100">
          <div>
            {kicker ? <span className="section-kicker">{kicker}</span> : null}
            <h3 id={titleId} className="text-xl font-bold mt-1">{title}</h3>
          </div>
          <button 
            type="button" 
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-charcoal hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={24} />
          </button>
        </div>
        <div className="p-6 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
