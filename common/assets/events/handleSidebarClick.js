function initializerSidebar () {
  const reportButton = document.getElementById('report__page');
  const dropdownMenu = document.getElementById('dropdown__menu');
  const sidebar = document.querySelector('.sidebar');

  reportButton.addEventListener('click', function () {
    dropdownMenu.classList.toggle('show');
  });

  sidebar.addEventListener('mouseleave', function () {
    dropdownMenu.classList.remove('show');
  });


  const closeAppBtn = document.getElementById('sidebar__button--close');
  if (closeAppBtn) {
    closeAppBtn.addEventListener("click", function () {
      handler.close_application();
    });
  };
};