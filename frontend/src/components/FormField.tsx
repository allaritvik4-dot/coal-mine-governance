import React from 'react';
import styles from './FormField.module.css';

interface BaseFieldProps {
  label: string;
  error?: string;
  helper?: string;
  required?: boolean;
}

interface InputProps extends BaseFieldProps, React.InputHTMLAttributes<HTMLInputElement> {
  as?: 'input';
}

interface SelectProps extends BaseFieldProps, React.SelectHTMLAttributes<HTMLSelectElement> {
  as: 'select';
  options?: { value: string | number; label: string }[];
  children?: React.ReactNode;
}

interface TextareaProps extends BaseFieldProps, React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  as: 'textarea';
}

type FormFieldProps = InputProps | SelectProps | TextareaProps;

export const FormField: React.FC<FormFieldProps> = (props) => {
  const { label, error, helper, required, ...rest } = props;
  const id = props.id || props.name || label.toLowerCase().replace(/\s+/g, '-');

  const renderControl = () => {
    if (props.as === 'textarea') {
      const textareaProps = rest as React.TextareaHTMLAttributes<HTMLTextAreaElement>;
      return (
        <textarea
          id={id}
          className={`${styles.textarea} ${error ? styles.textareaError : ''}`}
          {...textareaProps}
        />
      );
    }

    if (props.as === 'select') {
      const { options, children, ...selectProps } = rest as SelectProps;
      return (
        <select
          id={id}
          className={`${styles.select} ${error ? styles.selectError : ''}`}
          {...selectProps}
        >
          {options
            ? options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))
            : children}
        </select>
      );
    }

    const inputProps = rest as React.InputHTMLAttributes<HTMLInputElement>;
    return (
      <input
        id={id}
        className={`${styles.input} ${error ? styles.inputError : ''}`}
        {...inputProps}
      />
    );
  };

  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        {label}
        {required && <span className={styles.required}>*</span>}
      </label>
      {renderControl()}
      {error && <span className={styles.error}>{error}</span>}
      {!error && helper && <span className={styles.helper}>{helper}</span>}
    </div>
  );
};

export default FormField;
