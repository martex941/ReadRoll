// Dark-light mode toggle 
function toggleSwitch() {
    var body = document.getElementById("html-body");
    body.classList.toggle("dark-theme");

    // Save the user's theme preference in local storage
    if (body.classList.contains("dark-theme")) {
        localStorage.setItem("theme", "dark");
    } 

    else {
        localStorage.setItem("theme", "light");
    }
}

// Ensure the selected theme is consistently set
function setTheme() {
    var body = document.getElementById("html-body");
    var theme = localStorage.getItem("theme");

    if (theme === "dark") {
        body.classList.add("dark-theme");
    } 

    else {
        body.classList.remove("dark-theme");
    }
}

// Make sure that the theme is set before the main content of the page loads
document.addEventListener("DOMContentLoaded", function() {
    setTheme();
});



// Dynamic footer depending whether the scrollbar is present or not
window.addEventListener('load', () => {
    const fixedFooterCSS = document.getElementById('fixed-footer');
    const hasScrollbar = () => document.documentElement.scrollHeight > window.innerHeight;
    const toggleFixedFooterCSS = () => {
      if (hasScrollbar()) {
        fixedFooterCSS.disabled = true;
      } else {
        fixedFooterCSS.disabled = false;
      }
    };
    toggleFixedFooterCSS();
    window.addEventListener('resize', toggleFixedFooterCSS);
    window.addEventListener('scroll', toggleFixedFooterCSS);
  });

