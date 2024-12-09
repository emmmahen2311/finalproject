import React from "react";
import './CandidateDetailsStep.css'

function CandidateDetailsStep({ children, candidate, setCandidate }) {
  console.log(candidate);
  
  const handleChange = (event) => {
    const { name, type, value, checked } = event.target;
    console.log(name);
    
    
    type === "checkbox"
      ? setCandidate((prev) => ({
          ...prev,
          [name]: checked,
        }))
      : setCandidate((prev) => ({
          ...prev,
          [name]: value,
        }));
  };

  return (
    <div className="candidate-details-step">
      <div className="form-group">
        <label>
          סיכום ראיון:
          <textarea
            name="סיכום ריאיון"
            value={candidate["סיכום ריאיון"]}
            onChange={handleChange}
            className="form-textarea"
          />
        </label>
      </div>
      <div className="form-group">
        <label>
          שנות ניסיון:
          <input
            min={0}
            max={30}
            type="number"
            name="שנות ניסיון"
            value={candidate["שנות ניסיון"]}
            onChange={(event =>{
              if(+event.target.value >= 0 && +event.target.value <= 30)
                handleChange(event)
              else
                alert(`${event.target.name} חייב להיות בין 0 ל 30`);
            })}
            className="form-input"
          />
        </label>
      </div>
      <div className="form-group checkbox-group">
        <label>
          סיווג ביטחוני:
          <input
            type="checkbox"
            name="סיווג ביטחוני"
            onChange={handleChange}
            className="form-checkbox"
            value={candidate["סיווג ביטחוני"]}
            checked={candidate["סיווג ביטחוני"] ? true : false}
          />
        </label>
        <label>
          בטיחות:
          <select
           name="בטיחות"
           onChange={handleChange}
           className="form-checkbox"
           value={candidate.בטיחות}
          >
            <option value="true">כן</option>
            <option value="false">לא</option>
          </select>
        </label>
        <label>
          101:
          <select
           name="'101'"
           onChange={handleChange}
           className="form-checkbox"
           value={candidate["'101'"]}
          >
            <option value="true">כן</option>
            <option value="false">לא</option>
          </select>          
        </label>
      </div>
      <div className="form-group">
        <label>
          תאריך ראיון:
          <input
            type="date"
            name="תאריך ריאיון"
            value={candidate["תאריך ריאיון"]}
            onChange={handleChange}
            className="form-input"
          />
        </label>
        {children}
      </div>
    </div>
  );
}

export default CandidateDetailsStep;
