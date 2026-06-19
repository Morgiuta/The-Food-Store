import { FormEvent, useEffect, useState } from 'react';
import type { Categoria, CategoriaFormValues, CategoriaTree } from '../../../../types/categoria';
import { uploadImagen, deleteImagen } from '../../../../services/uploadsService';
import { SearchableSelect } from '../../../../components/ui/SearchableSelect';

const initialValues: CategoriaFormValues = {
  nombre: '',
  descripcion: '',
  imagen_url: '',
  parent_id: null,
  orden_display: 0,
};

interface CategoriaFormProps {
  selectedCategoria: Categoria | null;
  categoriasTree: CategoriaTree[];
  isSubmitting?: boolean;
  existingNames: string[];
  onSubmit: (values: CategoriaFormValues) => Promise<void>;
  onCancelEdit: () => void;
}

export function CategoriaForm({
  selectedCategoria,
  categoriasTree,
  isSubmitting = false,
  existingNames,
  onSubmit,
  onCancelEdit,
}: CategoriaFormProps) {
  const [values, setValues] = useState<CategoriaFormValues>(initialValues);
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    setValues(
      selectedCategoria
        ? {
            nombre: selectedCategoria.nombre,
            descripcion: selectedCategoria.descripcion ?? '',
            imagen_url: selectedCategoria.imagen_url ?? '',
            parent_id: selectedCategoria.parent_id ?? null,
            orden_display: selectedCategoria.orden_display ?? 0,
          }
        : initialValues,
    );
    setSubmitAttempted(false);
  }, [selectedCategoria]);

  const isEditing = Boolean(selectedCategoria);
  const normalizedName = values.nombre.trim().toLowerCase();
  const hasDuplicatedName = existingNames.some(
    (name) => name.toLowerCase() === normalizedName,
  );
  
  const errors = {
    nombre: !values.nombre.trim()
      ? 'El nombre es obligatorio.'
      : values.nombre.trim().length < 2
        ? 'Debe tener al menos 2 caracteres.'
        : hasDuplicatedName
          ? 'Ya existe una categoría con ese nombre.'
          : '',
    descripcion:
      values.descripcion.trim().length > 300
        ? 'La descripción no puede superar 300 caracteres.'
        : '',
    orden_display: values.orden_display < 0 ? 'El orden no puede ser negativo.' : '',
  };
  
  const isSubmitDisabled = Boolean(errors.nombre || errors.descripcion || errors.orden_display) || isSubmitting;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitAttempted(true);

    if (isSubmitDisabled) {
      return;
    }

    await onSubmit({
      nombre: values.nombre.trim(),
      descripcion: values.descripcion.trim(),
      imagen_url: values.imagen_url.trim(),
      parent_id: values.parent_id === 0 ? null : values.parent_id,
      orden_display: Number(values.orden_display),
    });

    setValues(initialValues);
    setSubmitAttempted(false);
  };

  // Flatten tree to select options (preventing selecting itself as parent)
  const getFlatOptions = (tree: CategoriaTree[], prefix = ''): { id: number, label: string }[] => {
    let options: { id: number, label: string }[] = [];
    tree.forEach(node => {
      // Don't show the category itself or its descendants as potential parents
      if (selectedCategoria && node.id === selectedCategoria.id) return;
      options.push({ id: node.id, label: `${prefix}${node.nombre}` });
      if (node.children && node.children.length > 0) {
        options = options.concat(getFlatOptions(node.children, prefix + '— '));
      }
    });
    return options;
  };

  const parentOptions = getFlatOptions(categoriasTree);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const response = await uploadImagen(file, 'foodstore/categorias');
      setValues((current) => ({ ...current, imagen_url: response.secure_url }));
    } catch (error) {
      console.error('Error al subir la imagen:', error);
      alert('Hubo un error al subir la imagen. Por favor, intente de nuevo.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveImage = async () => {
    if (!values.imagen_url) return;
    
    try {
      const urlParts = values.imagen_url.split('/');
      const publicIdWithExt = urlParts[urlParts.length - 1];
      const publicId = `foodstore/categorias/${publicIdWithExt.split('.')[0]}`;
      await deleteImagen(publicId);
    } catch (error) {
      console.error('Error al eliminar imagen de Cloudinary:', error);
    }

    setValues((current) => ({ ...current, imagen_url: '' }));
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div>
        <label className="block text-sm font-bold text-charcoal mb-2">Nombre de categoría</label>
        <input
          className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.nombre ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
          name="nombre"
          placeholder="Ej: Hamburguesas"
          value={values.nombre}
          maxLength={100}
          onChange={(event) => setValues((current) => ({ ...current, nombre: event.target.value }))}
        />
        {submitAttempted && errors.nombre && <p className="text-red-500 text-xs mt-1 font-medium">{errors.nombre}</p>}
      </div>

      <div>
        <label className="block text-sm font-bold text-charcoal mb-2">Categoría Padre (Opcional)</label>
        <SearchableSelect
          value={values.parent_id || 0}
          onChange={(val) => setValues((current) => ({ ...current, parent_id: Number(val) || null }))}
          options={[
            { value: 0, label: 'Ninguna (Categoría Principal)' },
            ...parentOptions.map((opt) => ({ value: opt.id, label: opt.label }))
          ]}
          placeholder="Seleccione categoría padre..."
        />
      </div>

      <div>
        <label className="block text-sm font-bold text-charcoal mb-2">Descripción</label>
        <textarea
          className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-y ${submitAttempted && errors.descripcion ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
          name="descripcion"
          placeholder="Detalle breve de la categoría"
          rows={3}
          value={values.descripcion}
          maxLength={300}
          onChange={(event) =>
            setValues((current) => ({ ...current, descripcion: event.target.value }))
          }
        />
        {submitAttempted && errors.descripcion && <p className="text-red-500 text-xs mt-1 font-medium">{errors.descripcion}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Orden Visual (Display)</label>
          <input
            type="number"
            min="0"
            step="1"
            className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${submitAttempted && errors.orden_display ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
            name="orden_display"
            value={values.orden_display}
            onChange={(event) => setValues((current) => ({ ...current, orden_display: Number(event.target.value) }))}
          />
          {submitAttempted && errors.orden_display && <p className="text-red-500 text-xs mt-1 font-medium">{errors.orden_display}</p>}
        </div>

        <div>
          <label className="block text-sm font-bold text-charcoal mb-2">Imagen de Categoría</label>
          {values.imagen_url ? (
            <div className="relative inline-block">
              <img src={values.imagen_url} alt="Vista previa" className="h-24 w-24 object-cover rounded-md border border-gray-200" />
              <button
                type="button"
                onClick={handleRemoveImage}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600 shadow-sm"
                title="Eliminar imagen"
              >
                ×
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <input
                type="file"
                accept="image/jpeg, image/png, image/webp"
                onChange={handleFileChange}
                disabled={isUploading}
                className="w-full p-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary-dark"
              />
              {isUploading && <span className="text-sm text-gray-500 font-medium">Subiendo...</span>}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-100">
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
          {isSubmitting ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Crear categoría'}
        </button>
      </div>
    </form>
  );
}
