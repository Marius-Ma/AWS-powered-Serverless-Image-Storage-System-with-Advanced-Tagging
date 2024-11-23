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

  const tagsDropdownButton = document.getElementById("tagsDropdownButton");
  const tagsDropdownMenu = document.getElementById("tagsDropdown");
  const tagsInput = document.getElementById("tagsInput");

  function clearMessages() {
    document.getElementById("result").innerHTML = "";
  }

  if (tagsDropdownButton && tagsDropdownMenu && tagsInput) {
    tagsDropdownButton.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      tagsDropdownMenu.style.display =
        tagsDropdownMenu.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", function (event) {
      if (
        !tagsDropdownButton.contains(event.target) &&
        !tagsDropdownMenu.contains(event.target)
      ) {
        tagsDropdownMenu.style.display = "none";
      }
    });

    tagsDropdownMenu.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      const item = event.target;
      if (item.classList.contains("dropdown-item")) {
        console.log("Tag selected:", item.textContent); // Log the selected tag
        const selectedTag = item.textContent.trim();
        let currentTags = tagsInput.value
          .split(",")
          .map((tag) => tag.trim())
          .filter((tag) => tag !== "");
        if (!currentTags.includes(selectedTag)) {
          currentTags.push(selectedTag);
        }
        tagsInput.value = currentTags.join(", ");
        tagsDropdownMenu.style.display = "none";
        clearMessages(); // Clear messages when selecting a tag
      }
    });

    // Clear success message when tags input is modified
    tagsInput.addEventListener("input", clearMessages);
  }

  const subscribeForm = document.getElementById("subscribeForm");
  if (subscribeForm) {
    subscribeForm.addEventListener("submit", function (event) {
      event.preventDefault();
      clearMessages();

      const email = document.getElementById("email").value;
      const tagsInputValue = tagsInput.value;
      const tags = tagsInputValue
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag !== "");

      if (!email) {
        alert("Please enter your email.");
        return;
      }

      if (tags.length === 0) {
        alert("Please select at least one tag.");
        return;
      }

      const username = localStorage.getItem("username");

      const data = { email, tag: tags[0], username };
      const idToken = localStorage.getItem("idToken");

      console.log("Subscribing to tags:", data);

      fetch(
        "https://pvpzcr0ae2.execute-api.us-east-1.amazonaws.com/test/TagSubscriber",
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
          document.getElementById("result").innerHTML =
            "<p style='color: green;'>Subscription successful!</p>";
        })
        .catch((error) => {
          console.error("Error:", error);
          document.getElementById("result").innerHTML =
            "<p style='color: red;'>Subscription failed, please try again.</p>";
        });
    });
  }

  const manageImagesTagsButton = document.getElementById(
    "manageImagesTagsButton"
  );
  if (manageImagesTagsButton) {
    manageImagesTagsButton.addEventListener("click", function () {
      window.location.href = "manage.html";
    });
  }

  // Clear success message on any input or button click
  const inputs = document.querySelectorAll("input, button");
  inputs.forEach((input) => {
    input.addEventListener("click", clearMessages);
  });

  // Clear success message on subscribe button click
  document
    .getElementById("subscribeForm")
    .addEventListener("submit", clearMessages);
});
