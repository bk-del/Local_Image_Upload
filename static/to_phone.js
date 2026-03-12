const VIDEO_FILE_PATTERN = /\.(mp4|mov|m4v|webm|avi)$/i;
const toPhoneForm = document.getElementById("to-phone-form");
const toPhoneFileInput = document.getElementById("to-phone-file-input");
const toPhonePreviewList = document.getElementById("to-phone-preview-list");
const toPhoneSubmitButton = document.getElementById("to-phone-submit-button");
const toPhoneStatus = document.getElementById("to-phone-status");
const toPhoneConfirmation = document.getElementById("to-phone-confirmation");
const toPhoneConfirmationSummary = document.getElementById("to-phone-confirmation-summary");
const toPhoneConfirmationFolder = document.getElementById("to-phone-confirmation-folder");
const toPhoneConfirmationLink = document.getElementById("to-phone-confirmation-link");
const toPhoneConfirmationFiles = document.getElementById("to-phone-confirmation-files");

const setStatus = (message, kind = "") => {
  if (!toPhoneStatus) {
    return;
  }
  toPhoneStatus.textContent = message;
  toPhoneStatus.className = `status ${kind}`.trim();
};

const clearConfirmation = () => {
  if (!toPhoneConfirmation) {
    return;
  }
  toPhoneConfirmation.hidden = true;
  toPhoneConfirmationSummary.textContent = "";
  toPhoneConfirmationFolder.textContent = "";
  toPhoneConfirmationLink.textContent = "";
  toPhoneConfirmationFiles.innerHTML = "";
};

const buildPreviewItem = (file, index) => {
  const item = document.createElement("article");
  item.className = "preview-item";

  const thumb = document.createElement("div");
  thumb.className = "preview-thumb";

  const objectUrl = URL.createObjectURL(file);
  if (file.type.startsWith("video/")) {
    const video = document.createElement("video");
    video.src = objectUrl;
    video.controls = true;
    video.preload = "metadata";
    thumb.appendChild(video);
  } else {
    const image = document.createElement("img");
    image.src = objectUrl;
    image.alt = file.name;
    thumb.appendChild(image);
  }

  const meta = document.createElement("div");
  meta.className = "preview-meta";

  const filename = document.createElement("p");
  filename.textContent = file.name;

  const nameField = document.createElement("input");
  nameField.type = "text";
  nameField.name = "custom-name";
  nameField.dataset.index = index;
  nameField.maxLength = 120;
  nameField.placeholder = "Optional custom filename";

  meta.append(filename, nameField);
  item.append(thumb, meta);
  return item;
};

const buildConfirmationItem = (item) => {
  const card = document.createElement("article");
  card.className = "confirmation-item";

  const isVideo = VIDEO_FILE_PATTERN.test(item.saved_name || "");
  let thumb;
  if (isVideo) {
    thumb = document.createElement("video");
    thumb.src = item.preview_url;
    thumb.controls = true;
    thumb.preload = "metadata";
  } else {
    thumb = document.createElement("img");
    thumb.src = item.preview_url;
    thumb.alt = item.saved_name;
    thumb.loading = "lazy";
  }

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
  if (!toPhoneConfirmation) {
    return;
  }

  toPhoneConfirmationSummary.textContent = `Staged ${payload.uploaded_count} file(s) for phone download.`;
  toPhoneConfirmationFolder.textContent = `Saved to: ${payload.saved_folder}`;
  toPhoneConfirmationLink.textContent = `Phone page: ${payload.phone_download_url}`;
  toPhoneConfirmationFiles.innerHTML = "";
  payload.saved_files.forEach((item) => {
    toPhoneConfirmationFiles.appendChild(buildConfirmationItem(item));
  });
  toPhoneConfirmation.hidden = false;
};

const refreshPreviews = () => {
  if (!toPhoneFileInput || !toPhonePreviewList || !toPhoneSubmitButton) {
    return;
  }

  toPhonePreviewList.innerHTML = "";
  const files = Array.from(toPhoneFileInput.files || []);
  if (!files.length) {
    toPhoneSubmitButton.disabled = true;
    return;
  }

  files.forEach((file, index) => {
    toPhonePreviewList.appendChild(buildPreviewItem(file, index));
  });
  toPhoneSubmitButton.disabled = false;
};

const initToPhoneForm = () => {
  if (!toPhoneForm || !toPhoneFileInput || !toPhoneSubmitButton) {
    return;
  }

  toPhoneFileInput.addEventListener("change", () => {
    setStatus("");
    clearConfirmation();
    refreshPreviews();
  });

  toPhoneForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const files = Array.from(toPhoneFileInput.files || []);
    if (!files.length) {
      setStatus("Select at least one photo or video to stage.", "error");
      return;
    }

    const maxBytes = (window.APP_CONFIG?.maxUploadMb || 500) * 1024 * 1024;
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

    toPhoneSubmitButton.disabled = true;
    setStatus("Staging files for phone download...");
    clearConfirmation();

    try {
      const response = await fetch("/to-phone/stage", {
        method: "POST",
        body: formData,
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Could not stage files.");
      }

      setStatus(payload.message, "success");
      showConfirmation(payload);
      toPhoneForm.reset();
      refreshPreviews();
    } catch (error) {
      setStatus(error.message || "Could not stage files.", "error");
    } finally {
      toPhoneSubmitButton.disabled = false;
    }
  });
};

initToPhoneForm();
