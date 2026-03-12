const fileInput = document.getElementById("file-input");
const previewList = document.getElementById("preview-list");
const uploadForm = document.getElementById("upload-form");
const submitButton = document.getElementById("submit-button");
const statusBox = document.getElementById("status");
const openUploadsButton = document.getElementById("open-uploads-button");
const confirmationBox = document.getElementById("upload-confirmation");
const confirmationSummary = document.getElementById("confirmation-summary");
const confirmationFolder = document.getElementById("confirmation-folder");
const confirmationFiles = document.getElementById("confirmation-files");

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

const clearConfirmation = () => {
  if (!confirmationBox) {
    return;
  }
  confirmationBox.hidden = true;
  confirmationSummary.textContent = "";
  confirmationFolder.textContent = "";
  confirmationFiles.innerHTML = "";
};

const buildConfirmationItem = (item) => {
  const card = document.createElement("article");
  card.className = "confirmation-item";

  const thumb = document.createElement("img");
  thumb.src = item.preview_url;
  thumb.alt = item.saved_name;
  thumb.loading = "lazy";

  const info = document.createElement("div");
  info.className = "confirmation-meta";

  const name = document.createElement("p");
  name.className = "confirmation-name";
  name.textContent = item.saved_name;

  const path = document.createElement("p");
  path.className = "confirmation-path";
  path.textContent = item.relative_path;

  info.append(name, path);
  card.append(thumb, info);
  return card;
};

const showConfirmation = (payload) => {
  if (!confirmationBox) {
    return;
  }

  confirmationSummary.textContent = `Uploaded ${payload.uploaded_count} photo(s) successfully.`;
  confirmationFolder.textContent = `Saved to: ${payload.saved_folder}`;
  confirmationFiles.innerHTML = "";
  payload.saved_files.forEach((item) => {
    confirmationFiles.appendChild(buildConfirmationItem(item));
  });
  confirmationBox.hidden = false;
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
  clearConfirmation();
  refreshPreviews();
});

if (openUploadsButton) {
  openUploadsButton.addEventListener("click", async () => {
    openUploadsButton.disabled = true;
    setStatus("Opening uploads folder...");

    try {
      const response = await fetch("/open-uploads", { method: "POST" });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Could not open uploads folder.");
      }
      setStatus(payload.message, "success");
    } catch (error) {
      setStatus(error.message || "Could not open uploads folder.", "error");
    } finally {
      openUploadsButton.disabled = false;
    }
  });
}

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
  setStatus("Sending photos to computer...");
  clearConfirmation();

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Upload failed.");
    }

    setStatus(payload.message, "success");
    showConfirmation(payload);
    uploadForm.reset();
    clearPreviews();
  } catch (error) {
    setStatus(error.message || "Upload failed.", "error");
  } finally {
    submitButton.disabled = false;
  }
});
