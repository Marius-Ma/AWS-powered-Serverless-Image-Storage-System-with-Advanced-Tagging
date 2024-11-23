document.addEventListener("DOMContentLoaded", function () {
  const cognitoDomain = "5225a3.auth.us-east-1.amazoncognito.com";
  const clientId = "45smhfrhqo4aimjrb25fv3t5rj";

  document.getElementById("loginButton").addEventListener("click", function () {
    const loginUrl = `https://${cognitoDomain}/login?client_id=${clientId}&response_type=token&scope=email+openid+phone&redirect_uri=http://localhost:5501/upload.html`;
    window.location.href = loginUrl;
  });
});
