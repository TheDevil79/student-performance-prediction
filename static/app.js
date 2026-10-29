/**
 * Student Performance Predictor - Frontend Client Logic
 * Handles system health check, quick profile presets, form data serialization,
 * FastAPI /predict integration, dynamic gauge rendering, and friendly error reporting.
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("predictionForm");
  const submitBtn = document.getElementById("submitBtn");
  const btnSpinner = document.getElementById("btnSpinner");

  // Status indicators
  const systemStatus = document.getElementById("systemStatus");
  const statusDot = systemStatus.querySelector(".status-dot");
  const statusText = document.getElementById("statusText");

  // Result elements
  const resultPlaceholder = document.getElementById("resultPlaceholder");
  const resultActive = document.getElementById("resultActive");
  const scoreNum = document.getElementById("scoreNum");
  const roundedGrade = document.getElementById("roundedGrade");
  const tierPill = document.getElementById("tierPill");
  const meterFill = document.getElementById("meterFill");
  const interpretationText = document.getElementById("interpretationText");
  const inferenceStatus = document.getElementById("inferenceStatus");

  // Error banner
  const errorBanner = document.getElementById("errorBanner");
  const errorTitle = document.getElementById("errorTitle");
  const errorMessage = document.getElementById("errorMessage");

  // Preset buttons
  const presetHighAchiever = document.getElementById("presetHighAchiever");
  const presetAverage = document.getElementById("presetAverage");
  const presetAtRisk = document.getElementById("presetAtRisk");
  const presetReset = document.getElementById("presetReset");

  // Numerical field names
  const NUMERICAL_FIELDS = new Set([
    "age",
    "Medu",
    "Fedu",
    "traveltime",
    "studytime",
    "failures",
    "famrel",
    "freetime",
    "goout",
    "Dalc",
    "Walc",
    "health",
    "absences",
  ]);

  // Sample Student Profiles
  const PROFILES = {
    high: {
      school: "GP",
      sex: "F",
      age: 16,
      address: "U",
      famsize: "GT3",
      Pstatus: "T",
      Medu: 4,
      Fedu: 4,
      Mjob: "health",
      Fjob: "teacher",
      reason: "reputation",
      guardian: "mother",
      traveltime: 1,
      studytime: 4,
      failures: 0,
      schoolsup: "no",
      famsup: "yes",
      paid: "yes",
      activities: "yes",
      nursery: "yes",
      higher: "yes",
      internet: "yes",
      romantic: "no",
      famrel: 5,
      freetime: 3,
      goout: 2,
      Dalc: 1,
      Walc: 1,
      health: 5,
      absences: 2,
    },
    average: {
      school: "GP",
      sex: "M",
      age: 17,
      address: "U",
      famsize: "GT3",
      Pstatus: "T",
      Medu: 2,
      Fedu: 2,
      Mjob: "services",
      Fjob: "other",
      reason: "course",
      guardian: "mother",
      traveltime: 1,
      studytime: 2,
      failures: 0,
      schoolsup: "no",
      famsup: "yes",
      paid: "no",
      activities: "yes",
      nursery: "yes",
      higher: "yes",
      internet: "yes",
      romantic: "no",
      famrel: 4,
      freetime: 3,
      goout: 3,
      Dalc: 1,
      Walc: 2,
      health: 4,
      absences: 6,
    },
    atRisk: {
      school: "MS",
      sex: "M",
      age: 19,
      address: "R",
      famsize: "LE3",
      Pstatus: "A",
      Medu: 1,
      Fedu: 1,
      Mjob: "at_home",
      Fjob: "other",
      reason: "other",
      guardian: "other",
      traveltime: 3,
      studytime: 1,
      failures: 3,
      schoolsup: "yes",
      famsup: "no",
      paid: "no",
      activities: "no",
      nursery: "no",
      higher: "no",
      internet: "no",
      romantic: "yes",
      famrel: 2,
      freetime: 4,
      goout: 5,
      Dalc: 4,
      Walc: 5,
      health: 2,
      absences: 24,
    },
  };

  /**
   * Applies a profile object to form inputs
   */
  function applyProfile(profile) {
    for (const [key, value] of Object.entries(profile)) {
      const field = form.elements[key];
      if (field) {
        field.value = value;
      }
    }
    hideError();
  }

  // Preset button listeners
  presetHighAchiever.addEventListener("click", () => applyProfile(PROFILES.high));
  presetAverage.addEventListener("click", () => applyProfile(PROFILES.average));
  presetAtRisk.addEventListener("click", () => applyProfile(PROFILES.atRisk));
  presetReset.addEventListener("click", () => {
    form.reset();
    hideError();
    resultActive.classList.add("hidden");
    resultPlaceholder.classList.remove("hidden");
  });

  /**
   * Check backend /health endpoint to report live status
   */
  async function checkHealth() {
    try {
      const response = await fetch("/health");
      if (response.ok) {
        const data = await response.json();
        if (data.model_loaded) {
          statusDot.className = "status-dot online";
          statusText.textContent = "API & Model Online";
        } else {
          statusDot.className = "status-dot offline";
          statusText.textContent = "Model Not Loaded (Run train.py)";
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (err) {
      statusDot.className = "status-dot offline";
      statusText.textContent = "Backend Offline";
    }
  }

  // Initial health check
  checkHealth();

  /**
   * Form submission handler
   */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();

    // Serialize form values with numerical type casting
    const formData = new FormData(form);
    const payload = {};

    for (const [key, value] of formData.entries()) {
      if (NUMERICAL_FIELDS.has(key)) {
        payload[key] = Number(value);
      } else {
        payload[key] = value;
      }
    }

    // Set UI loading state
    setLoading(true);

    try {
      const response = await fetch("/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        let msg = "An unexpected error occurred during prediction.";
        if (data && data.detail) {
          if (Array.isArray(data.detail)) {
            // Pydantic validation error details
            msg = data.detail.map((err) => `${err.loc.join(".")}: ${err.msg}`).join("; ");
          } else {
            msg = data.detail;
          }
        }
        showError("Prediction Failed", msg);
        return;
      }

      displayResult(data);
    } catch (err) {
      showError(
        "Network Error",
        "Could not connect to the FastAPI prediction endpoint. Please verify the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  });

  /**
   * Renders the returned prediction into the result panel
   */
  function displayResult(result) {
    const grade = result.predicted_grade;
    const rounded = result.rounded_grade;
    const tier = result.performance_level;

    scoreNum.textContent = grade.toFixed(2);
    roundedGrade.textContent = `${rounded} / 20`;
    tierPill.textContent = tier;

    // Remove existing tier classes
    tierPill.className = "tier-pill";
    if (grade >= 16.0) {
      tierPill.classList.add("tier-exc");
    } else if (grade >= 14.0) {
      tierPill.classList.add("tier-good");
    } else if (grade >= 12.0) {
      tierPill.classList.add("tier-sat");
    } else if (grade >= 10.0) {
      tierPill.classList.add("tier-pass");
    } else {
      tierPill.classList.add("tier-fail");
    }

    // Fill progress bar (0 to 20 mapped to 0% to 100%)
    const pct = Math.min(100, Math.max(0, (grade / 20) * 100));
    meterFill.style.width = `${pct}%`;

    // Dynamic interpretation text
    interpretationText.textContent = getInterpretation(grade);
    inferenceStatus.textContent = "200 OK";

    // Reveal active result view
    resultPlaceholder.classList.add("hidden");
    resultActive.classList.remove("hidden");
  }

  function getInterpretation(grade) {
    if (grade >= 16.0) {
      return "Outstanding performance! The model predicts this student will achieve high honors with a firm grasp of core mathematical competencies.";
    } else if (grade >= 14.0) {
      return "Strong academic standing. The student exhibits solid study habits and favorable environmental factors contributing to good scores.";
    } else if (grade >= 12.0) {
      return "Satisfactory progress. The student comfortably meets curriculum standards, though targeted study habits could elevate grades further.";
    } else if (grade >= 10.0) {
      return "Borderline passing grade (10/20 cutoff). The student is at moderate risk of slipping if absences increase or study hours decrease.";
    } else {
      return "At risk of failing (< 10 cutoff). The model identified significant risk factors such as high absences, past failures, or limited study time.";
    }
  }

  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    if (isLoading) {
      btnSpinner.classList.remove("hidden");
      submitBtn.querySelector(".btn-text").textContent = "Predicting Grade...";
    } else {
      btnSpinner.classList.add("hidden");
      submitBtn.querySelector(".btn-text").textContent = "Predict Final Math Grade (G3)";
    }
  }

  function showError(title, msg) {
    errorTitle.textContent = title;
    errorMessage.textContent = msg;
    errorBanner.classList.remove("hidden");
    resultActive.classList.add("hidden");
    resultPlaceholder.classList.remove("hidden");
  }

  function hideError() {
    errorBanner.classList.add("hidden");
  }
});
