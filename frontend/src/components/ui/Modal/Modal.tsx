import { useId, type PropsWithChildren } from 'react';
import './Modal.css';

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
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby={titleId}>
      <div className={`modal__panel modal__panel--${size}`}>
        <div className="modal__header">
          <div>
            {kicker ? <span className="section-kicker">{kicker}</span> : null}
            <h3 id={titleId}>{title}</h3>
          </div>
          <button type="button" onClick={onClose}>
            Cerrar
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
