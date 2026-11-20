import React from 'react';
import './FitnessAdvisor.css';

// ── WHO-standard BMI recommendations (Senior Athlete & Diet Consultant) ───────
const RECOMMENDATIONS = {
  severely_underweight: {
    label: 'Severely Underweight',
    color: '#DC2626',
    bg: '#FEF2F2',
    border: '#FECACA',
    icon: '⚠️',
    exercises: [
      'Light Resistance Training',
      'Bodyweight Squats',
      'Dumbbell Rows',
      'Seated Overhead Press',
      'Leg Press Machine',
      'Gentle Stretching',
    ],
    exerciseNote: '2–3 sessions/week only. No high-intensity cardio. Focus on gentle resistance movements. Consult a physician before starting any programme.',
    diet: 'Aggressive caloric surplus of 500–700 kcal/day above maintenance. Protein: 1.8–2.2 g per kg body weight. Eat every 2–3 hours.',
    meals: [
      'Whole milk oats with banana, honey & peanut butter',
      'Grilled chicken breast with white rice & olive oil',
      'Full-fat Greek yoghurt with granola & mixed nuts',
      'Egg omelette (3–4 eggs) with avocado on wholegrain toast',
      'Whey protein shake with whole milk & almond butter',
    ],
    avoid: [
      'Skipping meals',
      'Excessive cardio or aerobic exercise',
      'Low-calorie or diet foods',
      'Intermittent fasting',
    ],
    water: '2.5–3 L/day',
    tip: 'Medical attention is strongly advised. Work with a registered dietitian to safely increase body weight. Resistance training helps build muscle rather than just fat. Never crash-bulk with unhealthy foods.',
  },

  underweight: {
    label: 'Underweight',
    color: '#F59E0B',
    bg: '#FFFBEB',
    border: '#FDE68A',
    icon: '⚡',
    exercises: [
      'Progressive Resistance Training',
      'Barbell Squats',
      'Conventional Deadlifts',
      'Bench Press',
      'Pull-Ups / Assisted Pull-Ups',
      'Overhead Press',
    ],
    exerciseNote: '3–4 sessions/week. Prioritise compound movements. Limit cardio to 1–2 light sessions/week to avoid burning excess calories.',
    diet: 'Caloric surplus of 300–500 kcal/day. Protein: 1.6–2.2 g per kg body weight. Complex carbohydrates and healthy fats at every meal.',
    meals: [
      'Oats with full-fat milk, banana & peanut butter',
      'Grilled salmon with brown rice & steamed vegetables',
      'Whole egg scramble with cheese & wholegrain toast',
      'Chicken thighs with sweet potato & broccoli',
      'Trail mix (almonds, cashews, dried fruits) as snack',
    ],
    avoid: [
      'Excessive running or HIIT',
      'Skipping breakfast',
      'Low-fat or reduced-calorie products',
      'Alcohol (inhibits muscle protein synthesis)',
    ],
    water: '2.5–3 L/day',
    tip: 'Focus on progressive overload — increase weight or reps every week. Eat within 30 minutes post-workout (protein + carbs). Sleep 8 hours for optimal muscle recovery and growth hormone release.',
  },

  normal: {
    label: 'Healthy Weight',
    color: '#059669',
    bg: '#F0FDF4',
    border: '#A7F3D0',
    icon: '✅',
    exercises: [
      'Running / Jogging',
      'Swimming',
      'Cycling',
      'HIIT (High-Intensity Interval Training)',
      'Yoga / Pilates',
      'Strength Training',
    ],
    exerciseNote: '4–5 sessions/week. Mix 3 cardio sessions + 2 strength sessions. 30–45 min per session. Include one active rest day (yoga/walking).',
    diet: 'Maintenance calories with balanced macronutrients: 30% lean protein, 40% complex carbohydrates, 30% healthy fats. Focus on micronutrient diversity.',
    meals: [
      'Greek yoghurt with mixed berries, flaxseeds & granola',
      'Grilled salmon or chicken with quinoa & roasted vegetables',
      'Lentil or chickpea soup with wholegrain bread',
      'Stir-fried tofu with brown rice & mixed greens',
      'Apple with almond butter as a snack',
    ],
    avoid: [
      'Refined sugars and white bread',
      'Trans fats (margarine, processed snacks)',
      'Excessive alcohol',
      'Sugary beverages and energy drinks',
    ],
    water: '2.5–3 L/day',
    tip: 'Excellent work maintaining a healthy BMI. Periodise your training every 6–8 weeks (strength → hypertrophy → endurance phases) for continued improvement. Annual blood work recommended to monitor nutritional status.',
  },

  overweight: {
    label: 'Overweight',
    color: '#F97316',
    bg: '#FFF7ED',
    border: '#FED7AA',
    icon: '🔥',
    exercises: [
      'Brisk Walking (45–60 min)',
      'Swimming',
      'Cycling (Low-Moderate Intensity)',
      'HIIT — 20 min, 2–3x/week',
      'Resistance Training (Full-Body)',
      'Elliptical Trainer',
    ],
    exerciseNote: '5 sessions/week. 45–60 min cardio on most days. 2 full-body resistance sessions to preserve lean muscle during fat loss.',
    diet: 'Caloric deficit of 300–500 kcal/day. Protein: 1.6 g per kg body weight (muscle preservation). Reduce refined carbohydrates. Increase dietary fibre to 30–35 g/day.',
    meals: [
      'Grilled chicken breast salad with olive oil & lemon dressing',
      'Baked fish with steamed broccoli & cauliflower',
      'Boiled eggs with sliced avocado & tomato',
      'Vegetable and lentil stir-fry',
      'Low-fat cottage cheese with cucumber as snack',
    ],
    avoid: [
      'Sugary beverages (sodas, fruit juices, flavoured coffees)',
      'White bread, white pasta, white rice',
      'Fried and deep-fried foods',
      'Processed and packaged snacks',
      'Late-night eating after 8 PM',
    ],
    water: '3–3.5 L/day',
    tip: 'Combine cardio with resistance training for optimal fat loss while preserving lean muscle mass. Aim for a sustainable loss of 0.5–1 kg/week. Track your caloric intake using a food diary or app for the first 4 weeks.',
  },

  obese_1: {
    label: 'Obese — Class I',
    color: '#EF4444',
    bg: '#FEF2F2',
    border: '#FECACA',
    icon: '❗',
    exercises: [
      'Brisk Walking (20–30 min)',
      'Water Aerobics / Aqua Jogging',
      'Stationary Cycling (Low Resistance)',
      'Resistance Band Exercises',
      'Chair-Based Strength Exercises',
      'Low-Impact Aerobics',
    ],
    exerciseNote: 'Begin with 20 min/day, 3x/week. Increase by 5 min each week. Low-impact only to protect knees, hips and ankles. Consult a physician first.',
    diet: 'Caloric deficit of 500–600 kcal/day. Very high protein (1.6–1.8 g/kg) to prevent muscle loss. Eliminate all added sugars and ultra-processed foods. High fibre (35–40 g/day) for satiety.',
    meals: [
      'Grilled white fish with steamed green vegetables',
      'Egg white omelette with spinach, tomatoes & mushrooms',
      'Mixed salad with grilled chicken, chickpeas & lemon dressing',
      'Vegetable soup with beans (no cream)',
      'Low-fat plain yoghurt with cucumber as snack',
    ],
    avoid: [
      'All sugary drinks including 100% fruit juice',
      'Alcohol in all forms',
      'Deep-fried and fast foods',
      'Refined carbohydrates (white bread, pastries, cakes)',
      'High-sodium processed foods',
      'Eating in front of screens (mindless eating)',
    ],
    water: '3.5–4 L/day',
    tip: 'Start slowly and be consistent. Even a 5–10% reduction in body weight significantly improves cardiovascular health, blood sugar, and joint pain. Work with both a physician and a registered dietitian. Sleep quality directly impacts weight loss hormones (leptin and ghrelin).',
  },

  obese_2: {
    label: 'Obese — Class II / III',
    color: '#B91C1C',
    bg: '#FEF2F2',
    border: '#FCA5A5',
    icon: '🚨',
    exercises: [
      'Gentle Walking (10–15 min)',
      'Water-Based Exercise (Aqua Therapy)',
      'Seated Resistance Band Exercises',
      'Chair Yoga',
      'Supervised Physiotherapy',
      'Breathing Exercises',
    ],
    exerciseNote: 'Strictly supervised exercise only. Start with 10–15 min of gentle movement. Medical clearance is mandatory. A physiotherapist or certified personal trainer is strongly recommended.',
    diet: 'Medically supervised caloric deficit of 600–800 kcal/day. Protein: 1.8–2 g/kg to prevent muscle and bone loss. Eliminate all processed foods. Anti-inflammatory foods only.',
    meals: [
      'Steamed fish with boiled vegetables (no oil)',
      'Egg whites with spinach and tomatoes',
      'Clear vegetable broth with tofu',
      'Grilled chicken breast (no skin) with salad greens',
      'Celery sticks with low-fat hummus as snack',
    ],
    avoid: [
      'All sugary foods and beverages',
      'All fried and processed foods',
      'Alcohol completely',
      'Red meat and full-fat dairy',
      'High-GI carbohydrates',
      'Large portion sizes — use smaller plates',
    ],
    water: '4 L/day (sipped throughout the day)',
    tip: 'Immediate consultation with a physician, endocrinologist, and registered dietitian is strongly recommended. Medical interventions may be required. Focus on non-scale victories: better sleep, reduced joint pain, improved blood pressure. Every small step matters.',
  },
};

const getCategory = (bmi) => {
  if (bmi < 16.0) return 'severely_underweight';
  if (bmi < 18.5) return 'underweight';
  if (bmi < 25.0) return 'normal';
  if (bmi < 30.0) return 'overweight';
  if (bmi < 35.0) return 'obese_1';
  return 'obese_2';
};

const FitnessAdvisor = ({ onApply }) => {
  const [name, setName]         = React.useState('');
  const [height, setHeight]     = React.useState('');
  const [weight, setWeight]     = React.useState('');
  const [result, setResult]     = React.useState(null);
  const [selected, setSelected] = React.useState(null);
  const [activeTab, setActiveTab] = React.useState('exercise');

  const calculate = () => {
    const h = parseFloat(height);
    const w = parseFloat(weight);
    if (!h || !w || h < 50 || h > 300 || w < 10 || w > 500) return;
    const bmi = w / ((h / 100) ** 2);
    const cat = getCategory(bmi);
    setResult({ bmi: bmi.toFixed(1), personName: name.trim() || 'Athlete', ...RECOMMENDATIONS[cat] });
    setSelected(null);
    setActiveTab('exercise');
  };

  const handleApply = (exercise) => {
    if (!result) return;
    setSelected(exercise);
    onApply(exercise, result.diet);
  };

  const bmiPercent = result
    ? Math.min(((parseFloat(result.bmi) - 10) / 30) * 100, 100)
    : 0;

  return (
    <div className="advisor-wrapper">
      <div className="advisor-card">

        {/* ── Header ── */}
        <div className="advisor-header">
          <div className="advisor-header-left">
            <span className="advisor-icon">🏅</span>
            <div>
              <h3 className="advisor-title">Senior Fitness &amp; Diet Advisor</h3>
              <p className="advisor-subtitle">Professional BMI analysis with personalised exercise &amp; nutrition plan</p>
            </div>
          </div>
          <span className="advisor-badge">Expert Recommended</span>
        </div>

        {/* ── Inputs ── */}
        <div className="advisor-inputs">
          <div className="adv-field adv-field-name">
            <label className="adv-label">👤 Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Prashant Kumar"
              className="adv-input"
            />
          </div>
          <div className="adv-field">
            <label className="adv-label">📏 Height (cm)</label>
            <input
              type="number"
              value={height}
              onChange={(e) => setHeight(e.target.value)}
              placeholder="e.g. 175"
              className="adv-input"
            />
          </div>
          <div className="adv-field">
            <label className="adv-label">⚖️ Body Weight (kg)</label>
            <input
              type="number"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              placeholder="e.g. 70"
              className="adv-input"
            />
          </div>
          <button className="adv-btn" onClick={calculate}>Analyse My BMI</button>
        </div>

        {/* ── Result ── */}
        {result && (
          <div className="advisor-result" style={{ borderColor: result.border, background: result.bg }}>

            {/* Personalised greeting */}
            <div className="person-greeting">
              <span className="person-avatar">
                {result.personName.charAt(0).toUpperCase()}
              </span>
              <div>
                <p className="person-hello">Hello, <strong>{result.personName}</strong>! 👋</p>
                <p className="person-sub">Here is your personalised fitness &amp; nutrition plan based on your BMI.</p>
              </div>
            </div>

            {/* BMI Score row */}
            <div className="bmi-row">
              <div className="bmi-score-block">
                <span className="bmi-number" style={{ color: result.color }}>{result.bmi}</span>
                <span className="bmi-label">BMI Score</span>
              </div>
              <div className="bmi-category-block">
                <span className="bmi-icon">{result.icon}</span>
                <span className="bmi-category" style={{ color: result.color }}>{result.label}</span>
                <span className="bmi-tip">{result.tip}</span>
              </div>
              <div className="bmi-water-block">
                <span className="water-icon">💧</span>
                <span className="water-value">{result.water}</span>
                <span className="water-label">Daily Water</span>
              </div>
            </div>

            {/* BMI progress bar */}
            <div className="bmi-bar-wrap">
              <div className="bmi-bar-track">
                <div className="bmi-segment seg-su" />
                <div className="bmi-segment seg-uw" />
                <div className="bmi-segment seg-nw" />
                <div className="bmi-segment seg-ow" />
                <div className="bmi-segment seg-ob1" />
                <div className="bmi-segment seg-ob2" />
                <div
                  className="bmi-marker"
                  style={{ left: `${bmiPercent}%`, borderColor: result.color }}
                  title={`BMI: ${result.bmi}`}
                />
              </div>
              <div className="bmi-scale-labels">
                <span>{'< 16'}</span>
                <span>16–18.5</span>
                <span>18.5–25</span>
                <span>25–30</span>
                <span>30–35</span>
                <span>{'> 35'}</span>
              </div>
            </div>

            {/* Tabs */}
            <div className="adv-tabs">
              {[
                { key: 'exercise', label: '🏋️ Exercise Plan' },
                { key: 'diet',     label: '🥗 Nutrition Plan' },
                { key: 'meals',    label: '🍽️ Meal Ideas' },
                { key: 'avoid',    label: '🚫 Avoid' },
              ].map((t) => (
                <button
                  key={t.key}
                  className={`adv-tab ${activeTab === t.key ? 'adv-tab-active' : ''}`}
                  style={activeTab === t.key ? { borderBottomColor: result.color, color: result.color } : {}}
                  onClick={() => setActiveTab(t.key)}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Tab content */}
            <div className="adv-tab-content">

              {activeTab === 'exercise' && (
                <div>
                  <p className="tab-note">⏱️ {result.exerciseNote}</p>
                  <p className="rec-title">Click an exercise to apply it to your CREATE form:</p>
                  <div className="rec-tags">
                    {result.exercises.map((ex) => (
                      <button
                        key={ex}
                        className={`rec-tag ${selected === ex ? 'rec-tag-active' : ''}`}
                        onClick={() => handleApply(ex)}
                        style={selected === ex
                          ? { background: result.color, borderColor: result.color, color: '#fff' }
                          : {}}
                      >
                        {selected === ex ? '✓ ' : ''}{ex}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'diet' && (
                <div className="tab-diet-block">
                  <div className="rec-diet">
                    <span className="diet-icon">🥗</span>
                    <div>
                      <p className="diet-title">Nutrition Strategy</p>
                      <p className="diet-text">{result.diet}</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'meals' && (
                <div>
                  <p className="tab-note">✅ Recommended meals for your BMI category:</p>
                  <ul className="meal-list">
                    {result.meals.map((meal, i) => (
                      <li key={i} className="meal-item">
                        <span className="meal-bullet" style={{ background: result.color }}>
                          {i + 1}
                        </span>
                        {meal}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {activeTab === 'avoid' && (
                <div>
                  <p className="tab-note">🚫 Strictly avoid these for optimal results:</p>
                  <ul className="avoid-list">
                    {result.avoid.map((item, i) => (
                      <li key={i} className="avoid-item">
                        <span className="avoid-x">✕</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FitnessAdvisor;
