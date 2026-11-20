import React from 'react';
import './ContentBox.css';

const fmt = (d) => {
  const dt = new Date(d);
  return `${dt.getFullYear()}/${String(dt.getMonth()+1).padStart(2,'0')}/${String(dt.getDate()).padStart(2,'0')}`;
};

const DeleteContentBox = ({ onSubmit, content }) => {
  const [record] = React.useState(content);
  return (
    <div className="content-box product-card">
      <div className="product-header">
        <div className="product-avatar">
          {record.name ? record.name.charAt(0).toUpperCase() : '🏋'}
        </div>
        <div className="product-title-block">
          {record.name && <div className="product-person-name">👤 {record.name}</div>}
          <div className="product-name">{record.exercise}</div>
          <div className="product-rating">★★★★★ <span className="rating-count">(128)</span></div>
        </div>
      </div>
      <div className="product-stats">
        <div className="stat-row">
          <span className="stat-icon">⚖️</span>
          <span className="stat-label">Weight</span>
          <span className="stat-value weight-value">{record.weight} kg</span>
        </div>
        {record.diet && (
          <div className="stat-row">
            <span className="stat-icon">🥗</span>
            <span className="stat-label">Diet</span>
            <span className="stat-value diet-value">{record.diet}</span>
          </div>
        )}
        <div className="stat-row">
          <span className="stat-icon">📅</span>
          <span className="stat-label">Added</span>
          <span className="stat-value date-value">{fmt(record.date)}</span>
        </div>
      </div>
      <button className="btn-danger" onClick={() => onSubmit(record.id)}>Remove Record</button>
    </div>
  );
};

export default DeleteContentBox;
