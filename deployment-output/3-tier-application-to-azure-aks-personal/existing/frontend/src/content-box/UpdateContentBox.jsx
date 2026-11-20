import React from 'react';
import './ContentBox.css';

const fmt = (d) => {
  const dt = new Date(d);
  return `${dt.getFullYear()}/${String(dt.getMonth()+1).padStart(2,'0')}/${String(dt.getDate()).padStart(2,'0')}`;
};

const UpdateContentBox = ({ onSubmit, content }) => {
  const [record, setRecord] = React.useState(content);

  return (
    <div className="content-box">
      <div className="field-group">
        <label className="field-label">👤 Person Name</label>
        <input
          type="text"
          value={record.name || ''}
          onChange={(e) => setRecord({ ...record, name: e.target.value })}
          placeholder="e.g. Prashant Kumar"
        />
      </div>
      <div className="field-group">
        <label className="field-label">🏋️ Exercise Name</label>
        <input
          type="text"
          value={record.exercise}
          onChange={(e) => setRecord({ ...record, exercise: e.target.value })}
          placeholder="Exercise name"
        />
      </div>
      <div className="field-group">
        <label className="field-label">⚖️ Body Weight (kg)</label>
        <input
          type="number"
          value={record.weight}
          onChange={(e) => setRecord({ ...record, weight: parseInt(e.target.value) })}
          placeholder="e.g. 75"
        />
      </div>
      <div className="field-group">
        <label className="field-label">🥗 Diet / Nutrition</label>
        <input
          type="text"
          value={record.diet || ''}
          onChange={(e) => setRecord({ ...record, diet: e.target.value })}
          placeholder="e.g. High protein"
        />
      </div>
      <div className="date-tag">📅 Added: {fmt(record.date)}</div>
      <button className="btn-primary" onClick={() => onSubmit(record)}>Update Record</button>
    </div>
  );
};

export default UpdateContentBox;
