document.addEventListener("DOMContentLoaded", function () {
  const cognitoDomain = "5225a3.auth.us-east-1.amazoncognito.com";
  const clientId = "45smhfrhqo4aimjrb25fv3t5rj";
  const logoutRedirectUri = "http://localhost:5501/login.html";

  // Logout functionality
  document
    .getElementById("logoutButton")
    .addEventListener("click", function () {
      const logoutUrl = `https://${cognitoDomain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(
        logoutRedirectUri
      )}`;
      localStorage.removeItem("idToken");
      localStorage.removeItem("username");
      window.location.href = logoutUrl;
    });

  const username = localStorage.getItem("username");
  if (username) {
    document.getElementById("username").textContent = username;
  }

  const manageTagsForm = document.getElementById("manageTagsForm");
  const urlInput = document.getElementById("urlInput");
  const operationType = document.getElementById("operationType");
  const tagsInput = document.getElementById("tagsInput");
  const result = document.getElementById("result");
  const queryTagsButton = document.getElementById("queryTagsButton");
  const deleteImagesButton = document.getElementById("deleteImagesButton");
  const getImageButton = document.getElementById("getImageButton");
  const searchByImageButton = document.getElementById("searchByImageButton");

  function clearMessages() {
    result.innerHTML = "";
  }

  if (manageTagsForm) {
    manageTagsForm.addEventListener("submit", function (event) {
      event.preventDefault();
      clearMessages();
      const urls = urlInput.value
        .split(",")
        .map((url) => url.trim())
        .filter((url) => url !== "");
      const operationTypeValue = parseInt(operationType.value, 10);

      if (urls.length === 0) {
        alert("Please enter at least one URL.");
        return;
      }

      const tagsInputValue = tagsInput.value;
      const tagsArray = tagsInputValue.split(",").map((tag) => tag.trim());

      if (tagsArray.length === 0) {
        alert("Please enter at least one tag.");
        return;
      }

      const data = { url: urls, tags: tagsArray, type: operationTypeValue };
      const idToken = localStorage.getItem("idToken");

      console.log("Managing tags:", data);

      fetch(
        "https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/ManageTags",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${idToken}`,
          },
          body: JSON.stringify(data),
        }
      )
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          const notFoundUrls = data.results.filter(
            (item) => item.status === "URL not found"
          );

          const tagsNotFound = data.results.filter(
            (item) => item.status === "Tags to remove not found"
          );

          if (notFoundUrls.length > 0) {
            result.innerHTML = `<p style='color: red;'>The following URLs were not found: ${notFoundUrls
              .map((item) => item.url)
              .join(", ")}</p>`;
          } else if (tagsNotFound.length > 0) {
            result.innerHTML = `<p style='color: red;'>The following tags were already removed or not found: ${tagsNotFound
              .map((item) => item.nonexistent_tags.join(", "))
              .join(", ")}. Please try other tags.</p>`;
          } else if (operationTypeValue === 1) {
            result.innerHTML =
              "<p style='color: green;'>Tags added successfully!</p>";
          } else {
            result.innerHTML =
              "<p style='color: green;'>Tags removed successfully!</p>";
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          if (operationTypeValue === 1) {
            result.innerHTML =
              "<p style='color: red;'>Failed to add tags, please try again.</p>";
          } else {
            result.innerHTML =
              "<p style='color: red;'>Failed to remove tags, please try again.</p>";
          }
        });
    });
  }

  if (queryTagsButton) {
    queryTagsButton.addEventListener("click", function () {
      clearMessages();
      const tags = prompt(
        "Enter tags to query, separated by commas (e.g., 'person, 3'):"
      );

      if (tags) {
        const tagsArray = tags.split(",").map((tag) => tag.trim());
        if (tagsArray.length === 0 || tagsArray.length % 2 !== 0) {
          alert("Please enter tags in 'tag, count' format.");
          return;
        }

        const formattedTags = [];
        for (let i = 0; i < tagsArray.length; i += 2) {
          formattedTags.push(`${tagsArray[i]}, ${tagsArray[i + 1]}`);
        }

        const username = localStorage.getItem("username");

        const queryParams = {
          username: username,
          tags: formattedTags,
        };

        fetch(
          "https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/SearchImageByTags",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${localStorage.getItem("idToken")}`,
            },
            body: JSON.stringify(queryParams),
          }
        )
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then((data) => {
            if (data.links && data.links.length > 0) {
              result.innerHTML = data.links
                .map(
                  (link) =>
                    `<div class="thumbnail" data-url="${link}"><img src="${link}" alt="Thumbnail" style="width: 100px; margin: 5px;"><p>${link}</p></div>`
                )
                .join("");

              const thumbnails = document.querySelectorAll(".thumbnail");
              thumbnails.forEach((thumbnail) => {
                thumbnail.addEventListener("click", function () {
                  const thumbnailUrl = this.getAttribute("data-url");
                  const idToken = localStorage.getItem("idToken");

                  fetch(
                    `https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/GetImageFromThumbnail?thumbnail_url=${encodeURIComponent(
                      thumbnailUrl
                    )}`,
                    {
                      method: "GET",
                      headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${idToken}`,
                      },
                    }
                  )
                    .then((response) => {
                      if (!response.ok) {
                        throw new Error("Network response was not ok");
                      }
                      return response.json();
                    })
                    .then((data) => {
                      const fullSizeUrl = data.fullSizeUrl;
                      window.open(fullSizeUrl, "_blank");
                    })
                    .catch((error) => {
                      console.error("Error:", error);
                      alert(
                        "Failed to query full-size image, please try again."
                      );
                    });
                });
              });
            } else {
              result.innerHTML =
                "<p style='color: red;'>No images found matching the criteria.</p>";
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            result.innerHTML =
              "<p style='color: red;'>Query failed, this image cannot be found, please try a different image.</p>";
          });
      }
    });
  }

  if (deleteImagesButton) {
    deleteImagesButton.addEventListener("click", function () {
      clearMessages();
      const urls = prompt("Enter image URLs to delete, separated by commas:");
      if (urls) {
        const data = { urls: urls.split(",").map((url) => url.trim()) };
        const idToken = localStorage.getItem("idToken");

        fetch(
          "https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/deleteimage",
          {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${idToken}`,
            },
            body: JSON.stringify(data),
          }
        )
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then((data) => {
            if (data.message === "Images not found") {
              result.innerHTML =
                "<p style='color: red;'>One or more images not found in the database, deletion failed.</p>";
            } else {
              document.getElementById("result").innerHTML =
                "<p style='color: green;'>Images deleted successfully!</p>";
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            document.getElementById("result").innerHTML =
              "<p style='color: red;'>Deletion failed, please try again.</p>";
          });
      }
    });
  }

  if (getImageButton) {
    getImageButton.addEventListener("click", function () {
      clearMessages();
      const thumbnailUrl = prompt(
        "Enter the thumbnail URL to get the full-size image:"
      );

      if (thumbnailUrl) {
        const idToken = localStorage.getItem("idToken");

        fetch(
          `https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/GetImageFromThumbnail?thumbnail_url=${encodeURIComponent(
            thumbnailUrl
          )}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${idToken}`,
            },
          }
        )
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then((data) => {
            const fullSizeUrl = data.fullSizeUrl;
            window.open(fullSizeUrl, "_blank");
          })
          .catch((error) => {
            console.error("Error:", error);
            alert("Failed to get full-size image, please try again.");
          });
      }
    });
  }

  if (searchByImageButton) {
    searchByImageButton.addEventListener("click", function () {
      clearMessages();
      const fileInput = document.getElementById("fileInput");
      const file = fileInput.files[0];

      if (!file) {
        alert("Please select an image file.");
        return;
      }

      const reader = new FileReader();
      reader.onload = function (event) {
        const base64Image = event.target.result.split(",")[1];
        const idToken = localStorage.getItem("idToken");

        const data = {
          file: base64Image,
        };

        fetch(
          "https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/GetImageByTagsOfImage",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${idToken}`,
            },
            body: JSON.stringify(data),
          }
        )
          .then((response) => {
            if (response.status === 400) {
              return response.json().then((data) => {
                if (data.error === "No tags detected") {
                  throw new Error("No tags detected");
                }
                throw new Error("Query failed");
              });
            } else if (!response.ok) {
              throw new Error("Query failed");
            }
            return response.json();
          })
          .then((data) => {
            if (data.thumbnail_urls && data.thumbnail_urls.length > 0) {
              result.innerHTML = data.thumbnail_urls
                .map(
                  (url) =>
                    `<div class="thumbnail" data-url="${url}"><img src="${url}" alt="Thumbnail" style="width: 100px; margin: 5px;"><p>${url}</p></div>`
                )
                .join("");

              const thumbnails = document.querySelectorAll(".thumbnail");
              thumbnails.forEach((thumbnail) => {
                thumbnail.addEventListener("click", function () {
                  const thumbnailUrl = this.getAttribute("data-url");
                  const idToken = localStorage.getItem("idToken");

                  fetch(
                    `https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/GetImageFromThumbnail?thumbnail_url=${encodeURIComponent(
                      thumbnailUrl
                    )}`,
                    {
                      method: "GET",
                      headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${idToken}`,
                      },
                    }
                  )
                    .then((response) => {
                      if (!response.ok) {
                        throw new Error("Network response was not ok");
                      }
                      return response.json();
                    })
                    .then((data) => {
                      const fullSizeUrl = data.fullSizeUrl;
                      window.open(fullSizeUrl, "_blank");
                    })
                    .catch((error) => {
                      console.error("Error:", error);
                      alert(
                        "Failed to query full-size image, please try again."
                      );
                    });
                });
              });
            } else {
              result.innerHTML =
                "<p style='color: red;'>No images found matching the criteria.</p>";
            }
          })
          .catch((error) => {
            if (error.message === "No tags detected") {
              result.innerHTML =
                "<p style='color: red;'>No tags detected, please try a different image.</p>";
            } else {
              console.error("Error:", error);
              result.innerHTML =
                "<p style='color: red;'>Query failed, this image cannot be found, please try a different image.</p>";
            }
          });
      };
      reader.readAsDataURL(file);
    });
  }

  // Attach event listeners to all input fields to clear the result message
  document.querySelectorAll("input, select, button").forEach((element) => {
    element.addEventListener("click", clearMessages);
  });
});
