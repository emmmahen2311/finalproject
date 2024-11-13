import React from "react";

function ChooseFileStep({ children, setPickedFile }) {

  return (
    <div className="candidate-details-step">
      <div className="form-group">
        <label>
          בחר קובץ וורד:
          <input
            type="file"
            name="file"
            className="form-input"
            onChange={(e) => {
              setPickedFile(e.target.files[0])
            }}
          />
        </label>

        <div className="form-group">
       
        {children}
      </div>
      </div>
    </div>
  );
}

export default ChooseFileStep;
