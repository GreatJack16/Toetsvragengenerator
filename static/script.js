document.addEventListener('DOMContentLoaded', () => {
const radios = document.querySelectorAll('input[name="subgoals_mode"]');
const generateBox = document.getElementById('generate-subdoelen-box');
const uploadBox = document.getElementById('upload-subdoelen-box');

const onderwerp = document.getElementById('onderwerp');
const niveau = document.getElementById('niveau');
const selection = document.getElementById('selection');
const aOnthouden = document.getElementById('aantal_onthouden');
const aBegrijpen = document.getElementById('aantal_begrijpen');
const aToepassen = document.getElementById('aantal_toepassen');
const extra = document.getElementById('extra_instructions');
const sumSelection = document.getElementById('sum-selection');
const sumOnderwerp = document.getElementById('sum-onderwerp');
const sumNiveau = document.getElementById('sum-niveau');
const sumBlooms = document.getElementById('sum-blooms');
const sumSubgoals = document.getElementById('sum-subgoals');
const sumFiles = document.getElementById('sum-files');
const form = document.querySelector('form');
const loading = document.getElementById('loading');

form.addEventListener('submit', function () {
  if (generateBtn) {
    generateBtn.style.display = 'none';
  }

  if (loading) {
    loading.style.display = 'block';
  }
});

function getFileName(inputId){
  const el = document.getElementById(inputId);
  return el && el.files && el.files.length ? el.files[0].name : null;
}

function updateSubgoalsUI() {
  const selected = document.querySelector('input[name="subgoals_mode"]:checked').value;
  const subgen = document.getElementById('subgen');
  const subup = document.getElementById('subup');
  if (selected === 'generate') {
    generateBox.style.display = 'grid';
    uploadBox.style.display = 'none';
    subgen.style.display = 'block'
    subup.style.display = 'none'
    sumSubgoals.textContent = 'Genereer';
  } else {
    generateBox.style.display = 'none';
    uploadBox.style.display = 'flex';
    subgen.style.display = 'none'
    subup.style.display = 'block'
    sumSubgoals.textContent = 'Upload';
  }
}

function updateSummary() {
  sumSelection.textContent = selection.value.trim() || '—';
  sumOnderwerp.textContent = onderwerp.value.trim() || '—';
  sumNiveau.textContent = niveau.options[niveau.selectedIndex]?.text || '—';
  const blooms = [];
  if (aOnthouden.value.trim()) blooms.push(`Onthouden: ${aOnthouden.value.trim()}`);
  if (aBegrijpen.value.trim()) blooms.push(`Begrijpen: ${aBegrijpen.value.trim()}`);
  if (aToepassen.value.trim()) blooms.push(`Toepassen: ${aToepassen.value.trim()}`);
  sumBlooms.textContent = blooms.length ? blooms.join(', ') : '—';
  const files = [];
  const f1 = getFileName('study_material'); if (f1) files.push(`Studiemateriaal: ${f1}`);
  const f2 = getFileName('leerdoelen'); if (f2) files.push(`Leerdoelen: ${f2}`);
  const f3 = getFileName('voorbeeldvragen'); if (f3) files.push(`Voorbeeldvragen: ${f3}`);
  const f4 = getFileName('subdoelen_file'); if (f4) files.push(`Subdoelen: ${f4}`);
  sumFiles.textContent = files.length ? files.join(' | ') : 'geen bestanden geselecteerd';
}

[onderwerp, niveau, selection, aOnthouden, aBegrijpen, aToepassen, extra].forEach(el => el && el.addEventListener('input', updateSummary));
[document.getElementById('study_material'), document.getElementById('leerdoelen'), document.getElementById('voorbeeldvragen'), document.getElementById('subdoelen_file')].forEach(el => el && el.addEventListener('change', updateSummary));
radios.forEach(radio => radio.addEventListener('change', () => { updateSubgoalsUI(); updateSummary(); }));
updateSubgoalsUI();
updateSummary();

const generateSubBtn = document.getElementById('generate-subgoals-btn');
const generatedSubdoelen = document.getElementById('generated_subdoelen');

generateSubBtn.addEventListener('click', async () => {
  const form = document.querySelector('form');
  const formData = new FormData(form);
  formData.append('action', 'generate_subdoelen');

  const response = await fetch('/generate-subdoelen', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  generatedSubdoelen.value = data.generated_subdoelen || '';
});

const generateBtn = document.getElementById('generate-btn');
const examOutput = document.getElementById('exam-output');
const examResult = document.getElementById('exam-result');
const exportButtons = document.getElementById('export-buttons');

async function runGeneration() {
    const form = document.querySelector('form');
    const formData = new FormData(form);
    formData.append('action', 'generate_exam');

    loading.style.display = 'block';
    generateBtn.style.display = 'none';
    examOutput.style.display = 'none';

    try {
        const response = await fetch('/generate', { method: 'POST', body: formData });
        const data = await response.json();
        examResult.value = data.exam_text || 'Geen output ontvangen.';
        examOutput.style.display = 'block';
    } catch (error) {
        alert('Er ging iets mis.');
        generateBtn.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
}

generateBtn.addEventListener('click', runGeneration);
document.getElementById('btn-regenerate').addEventListener('click', runGeneration);
document.getElementById('btn-approve').addEventListener('click', approveExam);

function regenerateEverything() {
    runGeneration();
}

function approveExam() {
    document.getElementById('export-buttons').style.display = 'block';
    document.querySelector('.btn.primary').style.display = 'none';
}

document.getElementById('btn-download-docx').addEventListener('click', () => {
        downloadFile('docx');
    });

document.getElementById('btn-download-pdf').addEventListener('click', () => {
        downloadFile('pdf');
    });

function downloadFile(format) {
    const text = document.getElementById('exam-result').value;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/download/' + format;

    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'exam_text';
    input.value = text;

    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}
});