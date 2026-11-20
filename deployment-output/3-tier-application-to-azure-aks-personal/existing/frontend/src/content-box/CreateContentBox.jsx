import React from 'react';
import './ContentBox.css';

const CreateContentBox = ({ onSubmit, advisorPick = { exercise: '', diet: '' } }) => {
  const [name, setName]         = React.useState('');
  const [exercise, setExercise] = React.useState('');
  const [weight, setWeight]     = React.useState('');
  const [diet, setDiet]         = React.useState('');

  React.useEffect(() => {
    if (advisorPick.exercise) setExercise(advisorPick.exercise);
    if (advisorPick.diet)     setDiet(advisorPick.diet);
  }, [advisorPick]);

  const handleSubmit = () => {
    if (!exercise.trim()) return;
    onSubmit(name.trim(), exercise.trim(), parseInt(weight) || 0, diet.trim());
    setName(''); setExercise(''); setWeight(''); setDiet('');
  };

  const isAdvisorFilled = advisorPick.exercise && exercise === advisorPick.exercise;

  return (
    <div className="content-box">
      {isAdvisorFilled && (
        <div className="advisor-applied-tag">✅ Advisor recommendation applied</div>
      )}
      <div className="field-group">
        <label className="field-label">👤 Person Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Prashant Kumar"
        />
      </div>
      <div className="field-group">
        <label className="field-label">🏋️ Exercise Name</label>
        <input
          type="text"
          value={exercise}
          onChange={(e) => setExercise(e.target.value)}
          placeholder="e.g. Bench Press, Running"
        />
      </div>
      <div className="field-group">
        <label className="field-label">⚖️ Body Weight (kg)</label>
        <input
          type="number"
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
          placeholder="e.g. 75"
        />
      </div>
      <div className="field-group">
        <label className="field-label">🥗 Diet / Nutrition</label>
        <input
          type="text"
          value={diet}
          onChange={(e) => setDiet(e.target.value)}
          placeholder="e.g. High protein, Low carb"
        />
      </div>
      <button className="btn-primary" onClick={handleSubmit}>Add Record</button>
    </div>
  );
};

export default CreateContentBox;
