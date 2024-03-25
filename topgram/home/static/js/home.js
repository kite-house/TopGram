function dark_light(){
  const toggleButton = document.querySelector(".dark-light");
  const colors = document.querySelectorAll(".color");

  colors.forEach(color => {
    color.addEventListener("click", e => {
      colors.forEach(c => c.classList.remove("selected"));
      const theme = color.getAttribute("data-color");
      document.body.setAttribute("data-theme", theme);
      color.classList.add("selected");
    });
  });
  document.body.classList.toggle("dark-mode");
}

error: {
  icon: `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
</svg>`,
  color: "red-500"
},