import { FormEvent, useEffect, useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import type { Producto, ProductoFormValues } from '../../../../types/producto';
import type { CategoriaTree } from '../../../../types/categoria';
import type { Supply } from '../../../../types/supply';

const initialValues: ProductoFormValues = {
  nombre: '',
  descripcion: '',
  precio_base: 0,
  imagen_url: '',
  imagenes_url: [],
  stock_cantidad: 0,
  tiempo_prep_min: null,
  disponible: true,
  categorias: [],
  ingredientes: [],
};

interface ProductoFormProps {
  selectedProducto: Producto | null;
  categoriasTree: CategoriaTree[];
  ingredientesList: Supply[];
  isSubmitting?: boolean;
  onSubmit: (values: ProductoFormValues) => Promise<void>;
  onCancelEdit: () => void;
}

export function ProductoForm({
  selectedProducto,
  categoriasTree,
  ingredientesList,
  isSubmitting = false,
  onSubmit,
  onCancelEdit,
}: ProductoFormProps) {
  const [values, setValues] = useState<ProductoFormValues>(initialValues);
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [activeTab, setActiveTab] = useState<'general' | 'receta'>('general');

  useEffect(() => {
    setValues(
      selectedProducto
        ? {
            nombre: selectedProducto.nombre,
            descripcion: selectedProducto.descripcion ?? '',
            precio_base: selectedProducto.precio_base,
            imagen_url: selectedProducto.imagen_url ?? '',
            imagenes_url: selectedProducto.imagenes_url ?? [],
            stock_cantidad: selectedProducto.stock_cantidad,
            tiempo_prep_min: selectedProducto.tiempo_prep_min ?? null,
            disponible: selectedProducto.disponible,
            categorias: selectedProducto.categorias.map(c => ({ categoria_id: c.categoria_id, es_principal: c.es_principal })),
            ingredientes: selectedProducto.ingredientes.map(i => ({
              ingrediente_id: i.ingrediente_id,
              es_removible: i.es_removible,
              es_opcional: i.es_opcional,
              cantidad_requerida: i.cantidad_requerida,
            })),
          }
        : initialValues,
    );
    setSubmitAttempted(false);
    setActiveTab('general');
  }, [selectedProducto]);

  const isEditing = Boolean(selectedProducto);

  const errors = {
    nombre: !values.nombre.trim()
      ? 'El nombre es obligatorio.'
      : values.nombre.trim().length < 2
        ? 'Debe tener al menos 2 caracteres.'
        : '',
    precio_base: values.precio_base < 0 ? 'El precio no puede ser negativo.' : '',
    stock_cantidad: values.stock_cantidad < 0 ? 'El stock no puede ser negativo.' : '',
    categorias: values.categorias.length === 0 ? 'Debe seleccionar al menos una categoría.' : '',
  };

  const isSubmitDisabled = Boolean(errors.nombre || errors.precio_base || errors.stock_cantidad || errors.categorias) || isSubmitting;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitAttempted(true);

    if (isSubmitDisabled) {
      if (errors.categorias && activeTab !== 'receta') {
        setActiveTab('receta');
      }
      return;
    }

    await onSubmit({
      ...values,
      nombre: values.nombre.trim(),
      descripcion: values.descripcion.trim(),
      imagen_url: values.imagen_url.trim(),
      precio_base: Number(values.precio_base),
      stock_cantidad: Number(values.stock_cantidad),
      tiempo_prep_min: values.tiempo_prep_min ? Number(values.tiempo_prep_min) : null,
      // Ensure one category is principal
      categorias: values.categorias.map((c, i) => ({ ...c, es_principal: i === 0 })),
    });

    if (!isEditing) {
      setValues(initialValues);
    }
    setSubmitAttempted(false);
  };

  const getFlatOptions = (tree: CategoriaTree[], prefix = ''): { id: number, label: string }[] => {
    let options: { id: number, label: string }[] = [];
    tree.forEach(node => {
      options.push({ id: node.id, label: `${prefix}${node.nombre}` });
      if (node.children && node.children.length > 0) {
        options = options.concat(getFlatOptions(node.children, prefix + '— '));
      }
    });
    return options;
  };

  const categoriasOptions = getFlatOptions(categoriasTree);
  const ingredientesActivos = ingredientesList.filter(i => !i.deleted_at);

  return (
    <form className="flex flex-col h-full" onSubmit={handleSubmit}>
      <div className="flex border-b border-gray-200 mb-6">
        <button
          type="button"
          onClick={() => setActiveTab('general')}
          className={`py-3 px-6 font-bold text-sm border-b-2 transition-colors ${activeTab === 'general' ? 'border-primary text-primary-dark' : 'border-transparent text-gray-500 hover:text-charcoal'}`}
        >
          Datos Generales
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('receta')}
          className={`py-3 px-6 font-bold text-sm border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'receta' ? 'border-primary text-primary-dark' : 'border-transparent text-gray-500 hover:text-charcoal'}`}
        >
          Receta y Categorías
          {submitAttempted && errors.categorias && <span className="w-2 h-2 rounded-full bg-red-500 block"></span>}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-6 pb-6 px-1">
        {activeTab === 'general' && (
          <div className="space-y-6 animate-in fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-charcoal mb-2">Nombre del producto</label>
                <input
                  className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.nombre ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
                  name="nombre"
                  placeholder="Ej: Hamburguesa Doble"
                  value={values.nombre}
                  maxLength={150}
                  onChange={(e) => setValues(v => ({ ...v, nombre: e.target.value }))}
                />
                {submitAttempted && errors.nombre && <p className="text-red-500 text-xs mt-1 font-medium">{errors.nombre}</p>}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-charcoal mb-2">Descripción</label>
                <textarea
                  className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-y"
                  name="descripcion"
                  placeholder="Detalle del producto para el menú"
                  rows={3}
                  value={values.descripcion}
                  onChange={(e) => setValues(v => ({ ...v, descripcion: e.target.value }))}
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-charcoal mb-2">Precio Base ($)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.precio_base ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
                  name="precio_base"
                  value={values.precio_base}
                  onChange={(e) => setValues(v => ({ ...v, precio_base: Number(e.target.value) }))}
                />
                {submitAttempted && errors.precio_base && <p className="text-red-500 text-xs mt-1 font-medium">{errors.precio_base}</p>}
              </div>

              <div>
                <label className="block text-sm font-bold text-charcoal mb-2">Tiempo Prep. (Mins) - Opcional</label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  name="tiempo_prep_min"
                  value={values.tiempo_prep_min ?? ''}
                  onChange={(e) => setValues(v => ({ ...v, tiempo_prep_min: e.target.value ? Number(e.target.value) : null }))}
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-charcoal mb-2">URL de Imagen Principal</label>
                <input
                  className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  name="imagen_url"
                  placeholder="https://ejemplo.com/img.jpg"
                  value={values.imagen_url}
                  onChange={(e) => setValues(v => ({ ...v, imagen_url: e.target.value }))}
                />
              </div>
              
              <div className="md:col-span-2 mt-2">
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative flex items-center justify-center">
                    <input
                      checked={values.disponible}
                      type="checkbox"
                      className="peer sr-only"
                      onChange={(e) => setValues(v => ({ ...v, disponible: e.target.checked }))}
                    />
                    <div className="w-6 h-6 border-2 border-gray-300 rounded peer-checked:bg-green-500 peer-checked:border-green-500 transition-colors"></div>
                    <svg className="absolute w-4 h-4 text-white opacity-0 peer-checked:opacity-100 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="font-medium text-charcoal group-hover:text-green-600 transition-colors">Producto Visible (Disponible para venta)</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'receta' && (
          <div className="space-y-8 animate-in fade-in">
            {/* Categorías Section */}
            <div className="bg-gray-50 p-5 rounded-lg border border-gray-100">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h4 className="font-bold text-charcoal">Categorías</h4>
                  <p className="text-xs text-gray-500">¿Dónde aparecerá este producto? (La primera será la principal)</p>
                </div>
                <button
                  type="button"
                  onClick={() => setValues(v => ({ ...v, categorias: [...v.categorias, { categoria_id: 0, es_principal: v.categorias.length === 0 }] }))}
                  className="text-sm font-bold text-primary hover:text-primary-dark flex items-center gap-1"
                >
                  <Plus size={16} /> Añadir Categoría
                </button>
              </div>

              {submitAttempted && errors.categorias && <p className="text-red-500 text-xs mb-3 font-medium">{errors.categorias}</p>}

              {values.categorias.length === 0 ? (
                <div className="text-center py-4 bg-white rounded border border-dashed border-gray-300 text-gray-400 text-sm">
                  Ninguna categoría seleccionada.
                </div>
              ) : (
                <div className="space-y-3">
                  {values.categorias.map((cat, idx) => (
                    <div key={idx} className="flex gap-3 items-center bg-white p-3 rounded shadow-sm border border-gray-100">
                      <div className="flex-1">
                        <select
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-primary outline-none"
                          value={cat.categoria_id}
                          onChange={(e) => {
                            const val = Number(e.target.value);
                            setValues(v => ({
                              ...v,
                              categorias: v.categorias.map((c, i) => i === idx ? { ...c, categoria_id: val } : c)
                            }));
                          }}
                        >
                          <option value={0} disabled>Seleccione una categoría...</option>
                          {categoriasOptions.map(opt => (
                            <option key={opt.id} value={opt.id}>{opt.label}</option>
                          ))}
                        </select>
                      </div>
                      {idx === 0 && <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded">Principal</span>}
                      <button
                        type="button"
                        onClick={() => setValues(v => ({ ...v, categorias: v.categorias.filter((_, i) => i !== idx) }))}
                        className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Quitar"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Ingredientes Section */}
            <div className="bg-orange-50/50 p-5 rounded-lg border border-orange-100">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h4 className="font-bold text-charcoal">Receta (Ingredientes)</h4>
                  <p className="text-xs text-gray-500">Insumos que se descuentan del stock al vender.</p>
                </div>
                <button
                  type="button"
                  onClick={() => setValues(v => ({ 
                    ...v, 
                    ingredientes: [...v.ingredientes, { ingrediente_id: 0, cantidad_requerida: 1, es_removible: true, es_opcional: false }] 
                  }))}
                  className="text-sm font-bold text-orange-600 hover:text-orange-700 flex items-center gap-1"
                >
                  <Plus size={16} /> Añadir Ingrediente
                </button>
              </div>

              {values.ingredientes.length === 0 ? (
                <div className="text-center py-4 bg-white rounded border border-dashed border-orange-200 text-gray-400 text-sm">
                  Sin ingredientes. El producto no descontará stock de insumos.
                </div>
              ) : (
                <div className="space-y-3">
                  {values.ingredientes.map((ing, idx) => (
                    <div key={idx} className="flex flex-wrap md:flex-nowrap gap-3 items-start md:items-center bg-white p-3 rounded shadow-sm border border-orange-100">
                      <div className="w-full md:w-1/3">
                        <select
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 outline-none text-sm"
                          value={ing.ingrediente_id}
                          onChange={(e) => {
                            const val = Number(e.target.value);
                            setValues(v => ({
                              ...v,
                              ingredientes: v.ingredientes.map((c, i) => i === idx ? { ...c, ingrediente_id: val } : c)
                            }));
                          }}
                        >
                          <option value={0} disabled>Seleccione insumo...</option>
                          {ingredientesActivos.map(opt => (
                            <option key={opt.id} value={opt.id}>{opt.nombre}</option>
                          ))}
                        </select>
                      </div>
                      <div className="w-24">
                        <input
                          type="number"
                          min="0"
                          step="0.01"
                          placeholder="Cant."
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 outline-none text-sm"
                          value={ing.cantidad_requerida}
                          onChange={(e) => setValues(v => ({
                            ...v,
                            ingredientes: v.ingredientes.map((c, i) => i === idx ? { ...c, cantidad_requerida: Number(e.target.value) } : c)
                          }))}
                        />
                      </div>
                      <div className="flex-1 flex gap-4 text-sm">
                        <label className="flex items-center gap-1 cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={ing.es_removible}
                            onChange={(e) => setValues(v => ({
                              ...v,
                              ingredientes: v.ingredientes.map((c, i) => i === idx ? { ...c, es_removible: e.target.checked } : c)
                            }))}
                            className="rounded border-gray-300 text-orange-500 focus:ring-orange-500" 
                          />
                          <span className="text-gray-600">Removible</span>
                        </label>
                        <label className="flex items-center gap-1 cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={ing.es_opcional}
                            onChange={(e) => setValues(v => ({
                              ...v,
                              ingredientes: v.ingredientes.map((c, i) => i === idx ? { ...c, es_opcional: e.target.checked } : c)
                            }))}
                            className="rounded border-gray-300 text-orange-500 focus:ring-orange-500" 
                          />
                          <span className="text-gray-600">Opcional (Extra)</span>
                        </label>
                      </div>
                      <button
                        type="button"
                        onClick={() => setValues(v => ({ ...v, ingredientes: v.ingredientes.filter((_, i) => i !== idx) }))}
                        className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors self-end md:self-auto"
                        title="Quitar ingrediente"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        )}
      </div>

      <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-100 bg-white">
        <button 
          type="button" 
          onClick={onCancelEdit}
          className="px-6 py-2.5 font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          disabled={isSubmitDisabled}
          className="px-6 py-2.5 font-bold text-white bg-primary hover:bg-primary-dark rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Crear producto'}
        </button>
      </div>
    </form>
  );
}
