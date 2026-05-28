import { useState } from 'react';
import type { CategoriaTree, Categoria } from '../../../../types/categoria';

interface CategoriasTreeProps {
  tree: CategoriaTree[];
  onEdit: (cat: Categoria) => void;
  onDelete: (cat: Categoria) => void;
  onRestore: (cat: Categoria) => void;
  onView: (cat: Categoria) => void;
}

/** Recolecta todos los IDs del árbol para inicializar todos expandidos */
function collectAllIds(nodes: CategoriaTree[]): Set<number> {
  const ids = new Set<number>();
  const walk = (list: CategoriaTree[]) => {
    list.forEach((n) => {
      ids.add(n.id);
      if (n.children.length > 0) walk(n.children);
    });
  };
  walk(nodes);
  return ids;
}

interface TreeRowsProps {
  nodes: CategoriaTree[];
  depth: number;
  expandedIds: Set<number>;
  onToggle: (id: number) => void;
  onEdit: (cat: Categoria) => void;
  onDelete: (cat: Categoria) => void;
  onRestore: (cat: Categoria) => void;
  onView: (cat: Categoria) => void;
}

function TreeRows({ nodes, depth, expandedIds, onToggle, onEdit, onDelete, onRestore, onView }: TreeRowsProps) {
  return (
    <>
      {nodes.map((node) => {
        const isDeleted = Boolean(node.deleted_at);
        const isRoot = node.parent_id === null;
        const hasChildren = node.children.length > 0;
        const isExpanded = expandedIds.has(node.id);
        const indent = depth * 20; // 20px por nivel

        return (
          <>
            <tr
              key={node.id}
              className={`border-b border-gray-100 hover:bg-gray-50/60 transition-colors ${isDeleted ? 'opacity-60 bg-red-50/20' : ''}`}
            >
              {/* Nombre + indentación */}
              <td className="p-3">
                <div className="flex items-center gap-2" style={{ paddingLeft: `${indent}px` }}>
                  {/* Flecha expand/collapse o spacer */}
                  {hasChildren ? (
                    <button
                      type="button"
                      onClick={() => onToggle(node.id)}
                      className="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-700 transition-colors shrink-0"
                      title={isExpanded ? 'Colapsar' : 'Expandir'}
                    >
                      <span className="text-xs font-bold">{isExpanded ? '▼' : '▶'}</span>
                    </button>
                  ) : (
                    <span className="w-5 shrink-0" />
                  )}

                  {/* Imagen o placeholder */}
                  {node.imagen_url ? (
                    <img src={node.imagen_url} alt={node.nombre} className="w-8 h-8 rounded object-cover border border-gray-200 shrink-0" />
                  ) : (
                    <div className="w-8 h-8 rounded bg-gray-100 border border-gray-200 flex items-center justify-center shrink-0">
                      <span className="text-gray-400 text-[10px] font-bold">CAT</span>
                    </div>
                  )}

                  <div className="min-w-0">
                    <span className={`font-bold text-sm ${isDeleted ? 'line-through text-gray-400' : 'text-charcoal'}`}>
                      {node.nombre}
                    </span>
                    {node.descripcion && (
                      <p className="text-xs text-gray-400 truncate max-w-[200px]">{node.descripcion}</p>
                    )}
                  </div>
                </div>
              </td>

              {/* Badges: nivel + estado */}
              <td className="p-3">
                <div className="flex flex-wrap gap-1.5">
                  {isRoot && (
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-black uppercase tracking-wide rounded-full">
                      Principal
                    </span>
                  )}
                  {hasChildren && (
                    <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-[10px] font-black uppercase tracking-wide rounded-full">
                      {node.children.length} {node.children.length === 1 ? 'hijo' : 'hijos'}
                    </span>
                  )}
                  {isDeleted ? (
                    <span className="px-2 py-0.5 bg-red-100 text-red-700 text-[10px] font-black uppercase tracking-wide rounded-full">
                      Baja
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 bg-green-100 text-green-700 text-[10px] font-black uppercase tracking-wide rounded-full">
                      Activa
                    </span>
                  )}
                </div>
              </td>

              {/* Orden */}
              <td className="p-3 text-sm text-gray-400 font-medium text-center">
                {node.orden_display}
              </td>

              {/* Acciones */}
              <td className="p-3">
                <div className="flex items-center justify-end gap-1.5">
                  <button
                    type="button"
                    onClick={() => onView(node)}
                    className="px-2.5 py-1 text-xs font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                  >
                    Ver
                  </button>
                  {!isDeleted ? (
                    <>
                      <button
                        type="button"
                        onClick={() => onEdit(node)}
                        className="px-2.5 py-1 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded transition-colors"
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        onClick={() => onDelete(node)}
                        className="px-2.5 py-1 text-xs font-bold text-red-700 bg-red-50 hover:bg-red-100 rounded transition-colors"
                      >
                        Baja
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      onClick={() => onRestore(node)}
                      className="px-2.5 py-1 text-xs font-bold text-green-700 bg-green-50 hover:bg-green-100 rounded transition-colors"
                    >
                      Alta
                    </button>
                  )}
                </div>
              </td>
            </tr>

            {/* Hijos recursivos, solo si está expandido */}
            {hasChildren && isExpanded && (
              <TreeRows
                nodes={node.children}
                depth={depth + 1}
                expandedIds={expandedIds}
                onToggle={onToggle}
                onEdit={onEdit}
                onDelete={onDelete}
                onRestore={onRestore}
                onView={onView}
              />
            )}
          </>
        );
      })}
    </>
  );
}

export function CategoriasTree({ tree, onEdit, onDelete, onRestore, onView }: CategoriasTreeProps) {
  const [expandedIds, setExpandedIds] = useState<Set<number>>(() => collectAllIds(tree));

  const handleToggle = (id: number) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleExpandAll = () => setExpandedIds(collectAllIds(tree));
  const handleCollapseAll = () => setExpandedIds(new Set());

  if (tree.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="font-bold text-lg">Sin categorías</p>
        <p className="text-sm mt-1">Creá la primera categoría para empezar.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Controles del árbol */}
      <div className="flex items-center gap-2 mb-3 justify-end">
        <button
          type="button"
          onClick={handleExpandAll}
          className="text-xs font-bold text-gray-500 hover:text-gray-800 px-2 py-1 rounded hover:bg-gray-100 transition-colors"
        >
          Expandir todo
        </button>
        <span className="text-gray-300">|</span>
        <button
          type="button"
          onClick={handleCollapseAll}
          className="text-xs font-bold text-gray-500 hover:text-gray-800 px-2 py-1 rounded hover:bg-gray-100 transition-colors"
        >
          Colapsar todo
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="p-3 font-bold text-xs text-gray-500 uppercase tracking-wide">Categoría</th>
              <th className="p-3 font-bold text-xs text-gray-500 uppercase tracking-wide">Estado</th>
              <th className="p-3 font-bold text-xs text-gray-500 uppercase tracking-wide text-center">Orden</th>
              <th className="p-3 font-bold text-xs text-gray-500 uppercase tracking-wide text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <TreeRows
              nodes={tree}
              depth={0}
              expandedIds={expandedIds}
              onToggle={handleToggle}
              onEdit={onEdit}
              onDelete={onDelete}
              onRestore={onRestore}
              onView={onView}
            />
          </tbody>
        </table>
      </div>
    </div>
  );
}
