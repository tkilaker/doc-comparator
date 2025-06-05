document.addEventListener("DOMContentLoaded", function () {
  const compareForm = document.getElementById("compareForm")
  const compareBtn = document.getElementById("compareBtn")
  const loadingIndicator = document.getElementById("loadingIndicator")
  const errorMessage = document.getElementById("errorMessage")
  const resultsSection = document.getElementById("resultsSection")
  const diffResults = document.getElementById("diffResults")
  const fileName1 = document.getElementById("fileName1")
  const fileName2 = document.getElementById("fileName2")
  const newComparisonBtn = document.getElementById("newComparisonBtn")
  const file1Input = document.getElementById("file1")
  const file2Input = document.getElementById("file2")

  // Hide all sections initially except upload
  hideElement(loadingIndicator)
  hideElement(errorMessage)
  hideElement(resultsSection)

  // Form submission handler
  compareForm.addEventListener("submit", function (e) {
    e.preventDefault()

    // Validate files are selected
    if (!file1Input.files[0] || !file2Input.files[0]) {
      showError("Please select both files before comparing.")
      return
    }

    // Validate file types
    const file1 = file1Input.files[0]
    const file2 = file2Input.files[0]

    if (!isValidFileType(file1) || !isValidFileType(file2)) {
      showError("Please select only PDF or DOCX files.")
      return
    }

    // Validate file sizes (16MB max)
    const maxSize = 16 * 1024 * 1024 // 16MB
    if (file1.size > maxSize || file2.size > maxSize) {
      showError("File size must be less than 16MB.")
      return
    }

    compareDocuments()
  })

  // New comparison button handler
  newComparisonBtn.addEventListener("click", function () {
    resetForm()
  })

  // File input change handlers for better UX
  file1Input.addEventListener("change", function () {
    hideElement(errorMessage)
    updateFileInputDisplay(this)
  })

  file2Input.addEventListener("change", function () {
    hideElement(errorMessage)
    updateFileInputDisplay(this)
  })

  function compareDocuments() {
    const formData = new FormData()
    formData.append("file1", file1Input.files[0])
    formData.append("file2", file2Input.files[0])

    // Show loading state
    showLoading()
    hideElement(errorMessage)
    hideElement(resultsSection)
    compareBtn.disabled = true

    fetch("/compare", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        hideElement(loadingIndicator)
        compareBtn.disabled = false

        if (data.success) {
          showResults(data)
        } else {
          showError(
            data.error || "An error occurred while comparing documents."
          )
        }
      })
      .catch((error) => {
        hideElement(loadingIndicator)
        compareBtn.disabled = false
        console.error("Error:", error)
        showError("Network error. Please check your connection and try again.")
      })
  }

  function showResults(data) {
    fileName1.textContent = data.file1_name
    fileName2.textContent = data.file2_name
    diffResults.innerHTML = data.diff_html
    showElement(resultsSection)

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: "smooth" })
  }

  function showLoading() {
    showElement(loadingIndicator)
  }

  function showError(message) {
    errorMessage.textContent = message
    showElement(errorMessage)

    // Scroll to error message
    errorMessage.scrollIntoView({ behavior: "smooth" })
  }

  function resetForm() {
    compareForm.reset()
    hideElement(errorMessage)
    hideElement(resultsSection)
    hideElement(loadingIndicator)
    compareBtn.disabled = false

    // Reset file input displays
    updateFileInputDisplay(file1Input)
    updateFileInputDisplay(file2Input)

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  function isValidFileType(file) {
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    const validExtensions = [".pdf", ".docx"]

    return (
      validTypes.includes(file.type) ||
      validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext))
    )
  }

  function updateFileInputDisplay(input) {
    // This function can be extended to show file names or other info
    // For now, it's a placeholder for future enhancements
  }

  function showElement(element) {
    element.classList.remove("hidden")
  }

  function hideElement(element) {
    element.classList.add("hidden")
  }

  // Drag and drop functionality
  const uploadSection = document.querySelector(".upload-section")

  ;["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    uploadSection.addEventListener(eventName, preventDefaults, false)
    document.body.addEventListener(eventName, preventDefaults, false)
  })

  ;["dragenter", "dragover"].forEach((eventName) => {
    uploadSection.addEventListener(eventName, highlight, false)
  })

  ;["dragleave", "drop"].forEach((eventName) => {
    uploadSection.addEventListener(eventName, unhighlight, false)
  })

  uploadSection.addEventListener("drop", handleDrop, false)

  function preventDefaults(e) {
    e.preventDefault()
    e.stopPropagation()
  }

  function highlight(e) {
    uploadSection.classList.add("drag-over")
  }

  function unhighlight(e) {
    uploadSection.classList.remove("drag-over")
  }

  function handleDrop(e) {
    const dt = e.dataTransfer
    const files = dt.files

    if (files.length > 0) {
      if (files.length === 1) {
        // If only one file, put it in the first empty input
        if (!file1Input.files[0]) {
          file1Input.files = files
        } else if (!file2Input.files[0]) {
          file2Input.files = files
        }
      } else if (files.length >= 2) {
        // If two or more files, put first two in respective inputs
        const dt1 = new DataTransfer()
        const dt2 = new DataTransfer()
        dt1.items.add(files[0])
        dt2.items.add(files[1])
        file1Input.files = dt1.files
        file2Input.files = dt2.files
      }

      updateFileInputDisplay(file1Input)
      updateFileInputDisplay(file2Input)
    }
  }
})
