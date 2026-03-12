const fileInput = document.getElementById("file-input");
const previewList = document.getElementById("preview-list");
const uploadForm = document.getElementById("upload-form");
const submitButton = document.getElementById("submit-button");
const statusBox = document.getElementById("status");

const formatBytes = (bytes) => {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const setStatus = (message, kind = "") => {
  statusBox.textContent = message;
  statusBox.className = `status ${kind}`.trim();
};

const clearPreviews = () => {
  previewList.innerHTML = "";
};

const buildPreview = (file, index) => {
  const item = document.createElement("article");
  item.className = "preview-item";

  const thumb = document.createElement("div");
  thumb.className = "preview-thumb";

  const image = document.createElement("img");
  image.src = URL.createObjectURL(file);
  image.alt = file.name;
  thumb.appendChild(image);

  const meta = document.createElement("div");
  meta.className = "preview-meta";

  const filename = document.createElement("p");
  filename.textContent = file.name;

  const fileSize = document.createElement("p");
  fileSize.className = "file-size";
  fileSize.textContent = formatBytes(file.size);

  const nameField = document.createElement("input");
  nameField.type = "text";
  nameField.name = "custom-name";
  nameField.dataset.index = index;
  nameField.maxLength = 120;
  nameField.placeholder = "Optional custom filename";

  meta.append(filename, fileSize, nameField);
  item.append(thumb, meta);
  return item;
};

const refreshPreviews = () => {
  clearPreviews();
  const files = Array.from(fileInput.files || []);

  if (!files.length) {
    submitButton.disabled = true;
    return;
  }

  files.forEach((file, index) => {
    previewList.appendChild(buildPreview(file, index));
  });

  submitButton.disabled = false;
};

fileInput.addEventListener("change", () => {
  setStatus("");
  refreshPreviews();
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const files = Array.from(fileInput.files || []);
  if (!files.length) {
    setStatus("Select at least one image before uploading.", "error");
    return;
  }

  const maxBytes = (window.APP_CONFIG?.maxUploadMb || 15) * 1024 * 1024;
  const tooLarge = files.find((file) => file.size > maxBytes);
  if (tooLarge) {
    setStatus(`${tooLarge.name} exceeds the upload size limit.`, "error");
    return;
  }

  const formData = new FormData();
  const customInputs = Array.from(document.querySelectorAll('input[name="custom-name"]'));

  files.forEach((file, index) => {
    formData.append("files", file, file.name);
    formData.append("names", customInputs[index]?.value?.trim() || "");
  });

  submitButton.disabled = true;
  setStatus("Uploading images...");

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Upload failed.");
    }

    const savedFiles = payload.saved_files.map((item) => item.saved_name).join(", ");
    setStatus(`${payload.message} Saved as: ${savedFiles}`, "success");
    uploadForm.reset();
    clearPreviews();
  } catch (error) {
    setStatus(error.message || "Upload failed.", "error");
  } finally {
    submitButton.disabled = false;
  }
});
