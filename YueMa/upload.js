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

  document
    .getElementById("manageTagsButton")
    .addEventListener("click", function () {
      window.location.href = "subscribe.html";
    });

  const urlParams = new URLSearchParams(window.location.hash.substr(1));
  const idToken = urlParams.get("id_token");

  if (idToken) {
    localStorage.setItem("idToken", idToken);
    const base64Url = idToken.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );
    const user = JSON.parse(jsonPayload);
    localStorage.setItem("username", user["cognito:username"] || user.email);
  }

  const username = localStorage.getItem("username");
  const storedIdToken = localStorage.getItem("idToken");

  if (!username || !storedIdToken) {
    alert("You need to login first.");
    window.location.href = "login.html";
    return;
  } else {
    console.log("Username:", username);
    document.getElementById(
      "welcomeMessage"
    ).textContent = `Welcome, ${username}`;
  }

  const imageFileInput = document.getElementById("imageFile");
  imageFileInput.addEventListener("click", function () {
    // Clear the previous result message
    document.getElementById("result").innerHTML = "";
    // Clear the previous thumbnail
    document.getElementById("thumbnail").innerHTML = "";
    document.getElementById("fileName").value = "No file chosen";
  });

  imageFileInput.addEventListener("change", function () {
    const file = imageFileInput.files[0];
    const fileName = file?.name || "No file chosen";
    document.getElementById("fileName").value = fileName;

    // Display the new thumbnail
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const img = document.createElement("img");
        img.src = e.target.result;
        img.alt = "Thumbnail";
        img.style.width = "150px";
        const thumbnailContainer = document.getElementById("thumbnail");
        thumbnailContainer.innerHTML = "";
        thumbnailContainer.appendChild(img);
      };
      reader.readAsDataURL(file);
    }
  });

  document
    .getElementById("uploadForm")
    .addEventListener("submit", function (event) {
      event.preventDefault();

      const imageFile = document.getElementById("imageFile").files[0];
      if (!imageFile) {
        alert("Please select an image");
        return;
      }

      // Clear the previous result message before starting the upload
      document.getElementById("result").innerHTML = "";

      const reader = new FileReader();
      reader.readAsDataURL(imageFile);
      reader.onload = function () {
        const base64String = reader.result
          .replace("data:", "")
          .replace(/^.+,/, "");

        const data = {
          file: base64String,
          username: username,
          name: imageFile.name,
        };

        console.log("Uploading data:", data);

        fetch(
          "https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/uploadimage",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${storedIdToken}`,
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
            document.getElementById("result").innerHTML =
              "<p style='color: green;'>Upload successful!</p>";
          })
          .catch((error) => {
            console.error("Error:", error);
            document.getElementById("result").innerHTML =
              "<p style='color: red;'>Upload failed, please try again.</p>";
          });
      };
    });
});
