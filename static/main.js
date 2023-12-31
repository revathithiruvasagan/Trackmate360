document.addEventListener("DOMContentLoaded", function () {
  const checkbox = document.getElementById("checkbox");
  const themeStyleLink = document.getElementById("theme-style");
  const toggleImage = document.getElementById("toggleImage");

  // Function to set the theme based on the checkbox state
  function setTheme() {
    const theme = checkbox.checked ? "light" : "dummy";
    themeStyleLink.href = `/static/${theme}.css`; // Use absolute path
    // Save the theme preference in a cookie
    Cookies.set("theme", theme, { expires: 365 }); // Expires in 365 days

    // Toggle the image based on the checkbox state
    toggleImage.src = checkbox.checked
      ? "/static/logolight.png"
      : "/static/logo.png";
  }

  // Check the cookie for the theme preference
  const savedTheme = Cookies.get("theme");
  if (savedTheme) {
    checkbox.checked = savedTheme === "light";
    setTheme(); // Apply the saved theme
  }

  // Add event listener for theme switch
  checkbox.addEventListener("change", setTheme);
});
