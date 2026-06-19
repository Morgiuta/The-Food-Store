import React from 'react';
import Select, { ActionMeta, SingleValue, MultiValue, Props as SelectProps } from 'react-select';

export interface Option {
  value: string | number;
  label: string;
}

interface SearchableSelectProps extends Omit<SelectProps<Option, false>, 'value' | 'onChange' | 'options'> {
  value: string | number | null;
  onChange: (value: string | number) => void;
  options: Option[];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  hasError?: boolean;
}

export function SearchableSelect({
  value,
  onChange,
  options,
  placeholder = 'Seleccionar...',
  disabled = false,
  className = '',
  hasError = false,
  ...rest
}: SearchableSelectProps) {
  const selectedOption = options.find((opt) => opt.value === value) || null;

  const handleChange = (
    newValue: SingleValue<Option>,
    _actionMeta: ActionMeta<Option>
  ) => {
    if (newValue) {
      onChange(newValue.value);
    }
  };

  return (
    <div className={className}>
      <Select
        value={selectedOption}
        onChange={handleChange}
        options={options}
        placeholder={placeholder}
        isDisabled={disabled}
        isClearable={false}
        isSearchable={true}
        noOptionsMessage={() => "No se encontraron resultados"}
        styles={{
          control: (base, state) => ({
            ...base,
            borderColor: hasError ? '#ef4444' : state.isFocused ? '#f97316' : '#d1d5db',
            boxShadow: state.isFocused ? (hasError ? '0 0 0 2px #fecaca' : '0 0 0 2px #fdba74') : 'none',
            backgroundColor: hasError ? '#fef2f2' : disabled ? '#f3f4f6' : 'white',
            padding: '2px',
            borderRadius: '0.375rem',
            '&:hover': {
              borderColor: state.isFocused ? '#f97316' : '#9ca3af',
            },
          }),
          option: (base, state) => ({
            ...base,
            backgroundColor: state.isSelected
              ? '#f97316' // primary color
              : state.isFocused
              ? '#fff7ed' // orange-50
              : 'white',
            color: state.isSelected ? 'white' : '#374151',
            cursor: 'pointer',
            '&:active': {
              backgroundColor: '#ea580c', // primary-dark
            },
          }),
        }}
        {...rest}
      />
    </div>
  );
}
